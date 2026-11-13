import mediaManifest from "../MEDIA_MANIFEST.json" with { type: "json" };

const VIDEO_PATH = /^\/media\/(?:el-hierro|fuerteventura|gran-canaria|la-gomera|la-graciosa|la-palma|lanzarote|tenerife)\/cuento\.mp4$/;
const MAX_VIDEO_BYTES = 25 * 1024 * 1024;
const VIDEO_SIZES = new Map(
  Object.entries(mediaManifest.files)
    .map(([path, { bytes }]) => [`/${path}`, bytes])
    .filter(([path]) => VIDEO_PATH.test(path)),
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
  return [range.start, Math.min(range.end ?? size - 1, size - 1)];
}

function ifRangeMatches(value, headers) {
  // Only strong ETags are known to be reliable across asset versions.
  return value === null || (STRONG_ETAG.test(value) && value === headers.get("ETag"));
}

function streamRange(body, start, end, size) {
  const reader = body.getReader();
  let offset = 0;
  const slice = new ReadableStream({
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

  const output = new FixedLengthStream(end - start + 1);
  // pipeTo aborts the readable response if the source fails.
  void slice.pipeTo(output.writable).catch(() => {});
  return output.readable;
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
    const size = VIDEO_SIZES.get(new URL(request.url).pathname);
    if (rangeValue === null || size === undefined ||
        !["GET", "HEAD"].includes(request.method)) {
      return env.ASSETS.fetch(request);
    }

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
      return new Response(null, { status: 502, headers: { "Cache-Control": "no-store" } });
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
    headers.set("Content-Length", String(end - start + 1));
    headers.set("Content-Range", `bytes ${start}-${end}/${size}`);
    return new Response(streamRange(asset.body, start, end, size), { status: 206, headers });
  },
};
