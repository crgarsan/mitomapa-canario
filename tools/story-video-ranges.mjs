import mediaManifest from "../MEDIA_MANIFEST.json" with { type: "json" };

const ISLANDS = [
  'el-hierro', 'fuerteventura', 'gran-canaria', 'la-gomera',
  'la-graciosa', 'la-palma', 'lanzarote', 'tenerife',
];
const VIDEO_PATHS = new Set(ISLANDS.flatMap(island => [
  '/media/' + island + '/cuento.mp4', '/en/media/' + island + '/story.mp4',
]));
const MAX_VIDEO_BYTES = 25 * 1024 * 1024;
const VIDEO_PART_BYTES = 1024 * 1024;
const VIDEO_FILES = new Map(
  Object.entries(mediaManifest.files)
    .map(([path, metadata]) => [`/${path}`, metadata])
    .filter(([path]) => VIDEO_PATHS.has(path)),
);
const STRONG_ETAG = /^"[!\x23-\x7e\x80-\xff]*"$/;

function parseRange(value) {
  const match = /^bytes=([0-9]*)-([0-9]*)$/i.exec(value ?? "");
  if (!match || (!match[1] && !match[2])) return null;

  const start = match[1].replace(/^0+(?=[0-9])/, "");
  const end = match[2].replace(/^0+(?=[0-9])/, "");
  if (start && end && (start.length > end.length ||
      (start.length === end.length && start > end))) return null;

  return {
    start: start === "" ? null : Number(start),
    end: end === "" ? null : Number(end),
  };
}

function rangeBounds(range, size) {
  if (range.start === null) {
    return range.end === 0 ? null : [Math.max(0, size - range.end), size - 1];
  }
  if (range.start >= size) return null;
  // AVFoundation expects explicit ranges in full. Open-ended requests can
  // be continued at the next byte, as Chromium does during playback.
  const blockEnd = (Math.floor(range.start / VIDEO_PART_BYTES) + 1) * VIDEO_PART_BYTES - 1;
  const requestedEnd = range.end ?? blockEnd;
  return [range.start, Math.min(requestedEnd, size - 1)];
}

function ifRangeMatches(value, headers) {
  // Only strong ETags are known to be reliable across asset versions.
  return value === null || (STRONG_ETAG.test(value) && value === headers.get("ETag"));
}

function sliceRange(body, start, end, size) {
  const reader = body.getReader();
  let offset = 0;
  return new ReadableStream({
    async pull(controller) {
      while (true) {
        const { value, done } = await reader.read();
        if (done || offset + value.byteLength > size) {
          void reader.cancel().catch(() => {});
          throw new Error("Unexpected video body length");
        }

        const previous = offset;
        offset += value.byteLength;
        if (offset <= start) continue;

        const chunk = value.subarray(Math.max(0, start - previous), end + 1 - previous);
        // A slice through the final byte also verifies the end of the upstream body.
        if (end === size - 1 && offset === size && !(await reader.read()).done) {
          void reader.cancel().catch(() => {});
          throw new Error("Unexpected video body length");
        }
        controller.enqueue(chunk);
        if (offset > end) {
          controller.close();
          void reader.cancel().catch(() => {});
        }
        return;
      }
    },
    cancel(reason) {
      return reader.cancel(reason);
    },
  });
}

function invalidAssetResponse() {
  return new Response(null, { status: 502, headers: { "Cache-Control": "no-store" } });
}

async function readPart(assets, origin, video, index) {
  const url = new URL(`/_story_video_parts/${video.sha256}/${index}.bin`, origin);
  const response = await assets.fetch(new Request(url, { headers: { "Accept-Encoding": "identity" } }));
  const expected = Math.min(VIDEO_PART_BYTES, video.bytes - index * VIDEO_PART_BYTES);
  const reported = response.headers.get("Content-Length");
  const type = response.headers.get("Content-Type")?.split(";", 1)[0].trim().toLowerCase();
  const encoding = response.headers.get("Content-Encoding");
  if (response.status !== 200 || type !== "application/octet-stream" ||
      (reported !== null && reported !== String(expected)) ||
      (encoding !== null && encoding.toLowerCase() !== "identity")) {
    if (response.body) void response.body.cancel().catch(() => {});
    throw new Error("Invalid story video fragment");
  }
  const bytes = new Uint8Array(await response.arrayBuffer());
  if (bytes.byteLength !== expected) throw new Error("Unexpected story video fragment length");
  return bytes;
}

async function readShortRange(assets, origin, video, start, end) {
  const firstIndex = Math.floor(start / VIDEO_PART_BYTES);
  const lastIndex = Math.floor(end / VIDEO_PART_BYTES);
  const offset = start % VIDEO_PART_BYTES;
  if (firstIndex === lastIndex) {
    const part = await readPart(assets, origin, video, firstIndex);
    return part.subarray(offset, offset + end - start + 1);
  }
  const [first, last] = await Promise.all([
    readPart(assets, origin, video, firstIndex),
    readPart(assets, origin, video, lastIndex),
  ]);
  const fragment = new Uint8Array(end - start + 1);
  fragment.set(first.subarray(offset));
  fragment.set(last.subarray(0, end % VIDEO_PART_BYTES + 1), first.byteLength - offset);
  return fragment;
}

function rangeHeaders(asset) {
  const headers = new Headers(asset.headers);
  headers.set("Accept-Ranges", "bytes");
  // These fields describe the original message body.
  headers.delete("Content-Digest");
  headers.delete("Content-MD5");
  headers.delete("Digest");
  headers.delete("Transfer-Encoding");
  return headers;
}

export default {
  async fetch(request, env) {
    const rangeValue = request.headers.get("Range");
    const url = new URL(request.url);
    const video = VIDEO_FILES.get(url.pathname);
    if (rangeValue === null || video === undefined ||
        !["GET", "HEAD"].includes(request.method)) {
      return env.ASSETS.fetch(request);
    }
    const size = video.bytes;

    const range = request.method === "GET" ? parseRange(rangeValue) : null;
    const upstreamHeaders = new Headers(request.headers);
    upstreamHeaders.delete("Range");
    upstreamHeaders.delete("If-Range");
    if (range) upstreamHeaders.set("Accept-Encoding", "identity");
    const asset = await env.ASSETS.fetch(new Request(request, { headers: upstreamHeaders }));
    if (!range || asset.status !== 200 || !ifRangeMatches(request.headers.get("If-Range"), asset.headers)) {
      return asset;
    }

    const type = asset.headers.get("Content-Type")?.split(";", 1)[0].trim().toLowerCase();
    const encoding = asset.headers.get("Content-Encoding")?.toLowerCase();
    if (type !== "video/mp4" || (encoding && encoding !== "identity")) return asset;

    // Staging verifies each asset against the manifest. The binding can omit the length header.
    const rawSize = asset.headers.get("Content-Length");
    const lengthMismatch = rawSize !== null && (!/^[0-9]+$/.test(rawSize) || Number(rawSize) !== size);
    if (!asset.body || !Number.isSafeInteger(size) || size < 1 || size > MAX_VIDEO_BYTES || lengthMismatch) {
      if (asset.body) void asset.body.cancel().catch(() => {});
      return invalidAssetResponse();
    }

    const bounds = rangeBounds(range, size);
    const headers = rangeHeaders(asset);
    if (!bounds) {
      void asset.body.cancel().catch(() => {});
      headers.delete("Content-Type");
      headers.delete("Content-Encoding");
      headers.delete("Content-Disposition");
      headers.set("Content-Length", "0");
      headers.set("Content-Range", `bytes */${size}`);
      return new Response(null, { status: 416, headers });
    }

    const [start, end] = bounds;
    const length = end - start + 1;
    headers.set("Content-Length", String(length));
    headers.set("Content-Range", `bytes ${start}-${end}/${size}`);

    if (length > VIDEO_PART_BYTES) {
      // Preserve full explicit ranges without buffering an entire video.
      const slice = sliceRange(asset.body, start, end, size);
      const output = new FixedLengthStream(length);
      void slice.pipeTo(output.writable).catch(() => {});
      return new Response(output.readable, { status: 206, headers });
    }

    // Read the staged fragment directly, without scanning the original video.
    void asset.body.cancel().catch(() => {});
    try {
      const fragment = await readShortRange(env.ASSETS, url.origin, video, start, end);
      return new Response(fragment, { status: 206, headers });
    } catch (_) {
      return invalidAssetResponse();
    }
  },
};
