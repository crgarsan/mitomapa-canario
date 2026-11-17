const assert = require('node:assert/strict');
const { readFileSync, statSync } = require('node:fs');
const { join } = require('node:path');
const { before, after, test } = require('node:test');
const mediaManifest = require('../MEDIA_MANIFEST.json');

const origin = 'https://mitomapa.test';
const videoPath = '/media/la-palma/cuento.mp4';
const chunks = ['01', '234', '5', '6789'];
const video = chunks.join('');
const maxVideoSize = 25 * 1024 * 1024;
const partSize = 1024 * 1024;
const videoSize = mediaManifest.files[videoPath.slice(1)].bytes;
const encoder = new TextEncoder();
const padding = new Uint8Array(512 * 1024);
const assetHeaders = {
  'Cache-Control': 'public, max-age=0, must-revalidate',
  'Content-Digest': 'sha-256=:dGVzdA==:',
  'Content-Type': 'video/mp4',
  'ETag': '"asset-version"',
  'X-Content-Type-Options': 'nosniff',
};

function zeroChunks(length) {
  return [...Array(Math.floor(length / padding.length)).fill(padding),
    padding.subarray(0, length % padding.length)];
}

function paddedVideo(size = videoSize) {
  // Place identifiable bytes on each side of the first static part boundary.
  return [...chunks, ...zeroChunks(partSize - video.length - 3), 'abcDEF',
    ...zeroChunks(size - partSize - 7), '6789'];
}

function asBytes(chunk) {
  return typeof chunk === 'string' ? encoder.encode(chunk) : chunk;
}

function deploymentPart(bodyChunks, index, size) {
  const start = index * partSize;
  const end = Math.min(start + partSize, size);
  assert.ok(start < end, `Part ${index} must fit the mock asset`);
  const part = new Uint8Array(end - start);
  let offset = 0;
  let written = 0;
  for (const chunk of bodyChunks) {
    const bytes = asBytes(chunk);
    const lower = Math.max(start - offset, 0);
    const upper = Math.min(end - offset, bytes.length);
    if (lower < upper) {
      const selected = bytes.subarray(lower, upper);
      part.set(selected, written);
      written += selected.byteLength;
    }
    offset += bytes.length;
    if (offset >= end) break;
  }
  assert.equal(written, part.byteLength, `Mock body was truncated before part ${index}`);
  return part;
}

const originalFixedLengthStream = globalThis.FixedLengthStream;
let worker;

before(async () => {
  ({ default: worker } = await import('../tools/story-video-ranges.mjs'));
  globalThis.FixedLengthStream = class extends TransformStream {
    constructor(length) {
      let written = 0;
      super({
        transform(chunk, controller) {
          written += chunk.byteLength;
          assert.ok(written <= length);
          controller.enqueue(chunk);
        },
        flush() {
          assert.equal(written, length);
        },
      });
    }
  };
});

after(() => {
  if (originalFixedLengthStream === undefined) delete globalThis.FixedLengthStream;
  else globalThis.FixedLengthStream = originalFixedLengthStream;
});

async function fetchVideo({
  path = videoPath,
  method = 'GET',
  headers,
  status = 200,
  overrides,
  bodyChunks = chunks,
  partResponse,
} = {}) {
  const request = new Request(origin + path, { method, headers });
  const manifest = mediaManifest.files[new URL(request.url).pathname.slice(1)];
  let upstream;
  const traffic = { assetPulls: 0, assetCancels: 0, parts: [] };
  const env = {
    ASSETS: {
      fetch(assetRequest) {
        const url = new URL(assetRequest.url);
        if (url.pathname.startsWith('/_story_video_parts/')) {
          assert.ok(upstream, 'Read original asset metadata before requesting any part');
          assert.equal(url.origin, origin);
          assert.equal(url.search, '');
          assert.equal(url.hash, '');
          assert.equal(assetRequest.method, 'GET');
          assert.equal(assetRequest.headers.get('Range'), null);
          assert.equal(assetRequest.headers.get('If-Range'), null);
          const match = /^\/_story_video_parts\/([a-f\d]{64})\/(0|[1-9]\d*)\.bin$/.exec(url.pathname);
          assert.ok(match, `Unexpected static part path: ${url.pathname}`);
          assert.equal(match[1], manifest.sha256);
          const index = Number(match[2]);
          traffic.parts.push(index);
          const part = deploymentPart(bodyChunks, index, manifest.bytes);
          const responseHeaders = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': String(part.byteLength),
          };
          return partResponse ? partResponse(index, part, responseHeaders)
            : new Response(part, { headers: responseHeaders });
        }
        assert.equal(upstream, undefined);
        upstream = assetRequest;
        const responseHeaders = new Headers(assetHeaders);
        for (const [name, value] of Object.entries(overrides ?? {})) {
          if (value === null) responseHeaders.delete(name);
          else responseHeaders.set(name, value);
        }
        let nextChunk = 0;
        const body = method === 'HEAD' || status === 304 ? null : new ReadableStream({
          pull(controller) {
            traffic.assetPulls++;
            if (nextChunk === bodyChunks.length) {
              controller.close();
              return;
            }
            controller.enqueue(asBytes(bodyChunks[nextChunk++]));
          },
          cancel() { traffic.assetCancels++; },
        }, { highWaterMark: 0 });
        return new Response(body, { status, headers: responseHeaders });
      },
    },
  };

  const response = await worker.fetch(request, env);
  assert.equal(upstream.url, request.url);
  assert.equal(upstream.method, method);
  return { request, upstream, response, traffic };
}

test('only the sixteen story MP4s are served in ranges', async () => {
  const islands = [
    'el-hierro', 'fuerteventura', 'gran-canaria', 'la-gomera', 'la-graciosa', 'la-palma',
    'lanzarote', 'tenerife',
  ];
  const routes = islands.flatMap(island => [
    `/media/${island}/cuento.mp4`, `/en/media/${island}/story.mp4`,
  ]);
  const config = JSON.parse(readFileSync(join(__dirname, '../wrangler.jsonc'), 'utf8'));
  assert.deepEqual([...config.assets.run_worker_first].sort(), [...routes].sort());
  const manifestRoutes = Object.keys(mediaManifest.files)
    .filter(path => /^(?:media\/[^/]+\/cuento|en\/media\/[^/]+\/story)\.mp4$/.test(path))
    .map(path => '/' + path);
  assert.deepEqual(manifestRoutes.sort(), [...routes].sort());

  for (const path of routes) {
    const size = mediaManifest.files[path.slice(1)].bytes;
    assert.equal(statSync(join(__dirname, '..', path)).size, size, path);
    assert.ok(Number.isSafeInteger(size) && size > 0 && size <= maxVideoSize, path);
    const { response, traffic } = await fetchVideo({
      path: `${path}?v=1`,
      headers: { Range: 'bytes=0-1' },
      bodyChunks: paddedVideo(size),
    });
    assert.equal(response.status, 206, path);
    assert.equal(response.headers.get('Content-Range'), `bytes 0-1/${size}`, path);
    assert.equal(await response.text(), '01', path);
    assert.deepEqual(traffic, { assetPulls: 0, assetCancels: 1, parts: [0] }, path);
  }
  for (const path of [
    '/media/otra-isla/cuento.mp4', '/media/la-palma/otro.mp4',
    '/en/media/otra-isla/story.mp4', '/en/media/la-palma/cuento.mp4', '/index.html',
  ]) {
    const { request, upstream, response } = await fetchVideo({
      path,
      headers: { Range: 'bytes=0-1' },
    });
    assert.equal(upstream, request);
    assert.equal(response.status, 200);
    assert.equal(await response.text(), video);
  }
});

test('206 returns exact bytes from a static part and retains original asset metadata', async () => {
  const { upstream, response, traffic } = await fetchVideo({
    headers: { Range: 'bytes=1-6', 'Accept-Encoding': 'gzip, br' },
    bodyChunks: paddedVideo(),
  });
  assert.equal(upstream.headers.get('Range'), null);
  assert.equal(upstream.headers.get('Accept-Encoding'), 'identity');
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Accept-Ranges'), 'bytes');
  assert.equal(response.headers.get('Content-Range'), `bytes 1-6/${videoSize}`);
  assert.equal(response.headers.get('Content-Length'), '6');
  assert.equal(response.headers.get('Content-Digest'), null);
  for (const name of ['Cache-Control', 'Content-Type', 'ETag', 'X-Content-Type-Options']) {
    assert.equal(response.headers.get(name), assetHeaders[name]);
  }
  assert.equal(await response.text(), '123456');
  assert.deepEqual(traffic, { assetPulls: 0, assetCancels: 1, parts: [0] });
});

test('open-ended and suffix ranges use the complete asset length', async () => {
  const end = videoSize - 1;
  const cases = [
    [`bytes=${end - 2}-`, end - 2, '789'],
    ['bytes=-3', end - 2, '789'],
    [`bytes=000${end - 1}-99999999999999999999`, end - 1, '89'],
  ];
  for (const [range, start, body] of cases) {
    const { response, traffic } = await fetchVideo({ headers: { Range: range }, bodyChunks: paddedVideo() });
    assert.equal(response.status, 206, range);
    assert.equal(response.headers.get('Content-Range'), `bytes ${start}-${end}/${videoSize}`, range);
    assert.equal(response.headers.get('Content-Length'), String(body.length), range);
    assert.equal(await response.text(), body, range);
    assert.deepEqual(traffic, {
      assetPulls: 0,
      assetCancels: 1,
      parts: [...new Set([Math.floor(start / partSize), Math.floor(end / partSize)])],
    }, range);
  }
  const hugeSuffix = await fetchVideo({
    headers: { Range: 'bytes=-99999999999999999999' }, bodyChunks: paddedVideo(),
  });
  assert.equal(hugeSuffix.response.status, 206);
  assert.equal(hugeSuffix.response.headers.get('Content-Range'), `bytes 0-${end}/${videoSize}`);
  assert.deepEqual(hugeSuffix.traffic.parts, []);
  await hugeSuffix.response.body.cancel();
});

test('open-ended ranges stop at a part boundary and support continuation', async () => {
  for (const [start, end, expectedPrefix] of [
    [0, partSize - 1, '012345'],
    [partSize - 2, partSize - 1, 'bc'],
    [partSize, partSize * 2 - 1, 'DEF\0\0\0'],
  ]) {
    const { response, traffic } = await fetchVideo({
      headers: { Range: `bytes=${start}-` }, bodyChunks: paddedVideo(),
    });
    assert.equal(response.status, 206);
    assert.equal(response.headers.get('Content-Range'), `bytes ${start}-${end}/${videoSize}`);
    assert.equal(response.headers.get('Content-Length'), String(end - start + 1));
    const content = new Uint8Array(await response.arrayBuffer());
    assert.equal(content.length, end - start + 1);
    assert.equal(new TextDecoder().decode(content.subarray(0, expectedPrefix.length)), expectedPrefix);
    assert.deepEqual(traffic, { assetPulls: 0, assetCancels: 1, parts: [Math.floor(start / partSize)] });
  }
});

test('a short explicit range reads only the two parts it overlaps', async () => {
  const start = partSize - 3;
  const end = partSize + 2;
  const { response, traffic } = await fetchVideo({
    headers: { Range: `bytes=${start}-${end}` }, bodyChunks: paddedVideo(),
  });
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Content-Range'), `bytes ${start}-${end}/${videoSize}`);
  assert.equal(response.headers.get('Content-Length'), '6');
  assert.equal(await response.text(), 'abcDEF');
  assert.deepEqual(traffic, { assetPulls: 0, assetCancels: 1, parts: [0, 1] });
});

test('explicit video playback ranges are fulfilled in full for clients such as AVFoundation', async () => {
  const end = partSize * 2 - 1;
  const { response, traffic } = await fetchVideo({
    headers: { Range: `bytes=0-${end}` }, bodyChunks: paddedVideo(),
  });
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Content-Range'), `bytes 0-${end}/${videoSize}`);
  assert.equal((await response.arrayBuffer()).byteLength, end + 1);
  assert.deepEqual(traffic.parts, []);
  assert.ok(traffic.assetPulls > 0);
});

test('ordinary GET and HEAD, and methods outside the handler, preserve asset responses', async () => {
  for (const method of ['GET', 'HEAD']) {
    const { request, upstream, response } = await fetchVideo({
      method, overrides: { 'Content-Length': String(video.length) },
    });
    assert.equal(upstream, request);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('Content-Length'), String(video.length));
    assert.equal(await response.text(), method === 'HEAD' ? '' : video);
  }
  const head = await fetchVideo({ method: 'HEAD', headers: { Range: 'bytes=0-1' } });
  assert.equal(head.upstream.headers.get('Range'), null);
  assert.equal(head.response.status, 200);
  assert.equal(head.response.headers.get('Content-Range'), null);
  assert.equal(await head.response.text(), '');
  const post = await fetchVideo({ method: 'POST', headers: { Range: 'bytes=0-1' } });
  assert.equal(post.upstream, post.request);
  assert.equal(await post.response.text(), video);
});

test('malformed, unsupported, reversed, and multiple ranges are ignored', async () => {
  for (const range of ['bytes=7-2', 'bytes=-', 'bytes=0-1,3-4', 'items=0-1', 'bytes=+1-9']) {
    const { upstream, response } = await fetchVideo({ headers: { Range: range } });
    assert.equal(upstream.headers.get('Range'), null, range);
    assert.equal(response.status, 200, range);
    assert.equal(response.headers.get('Content-Range'), null, range);
    assert.equal(await response.text(), video, range);
  }
});

test('unsatisfiable ranges return 416 with the actual size and no body', async () => {
  for (const range of [`bytes=${videoSize}-`, 'bytes=-0', 'bytes=99999999999999999999-']) {
    const { response } = await fetchVideo({ headers: { Range: range } });
    assert.equal(response.status, 416, range);
    assert.equal(response.headers.get('Content-Range'), `bytes */${videoSize}`, range);
    assert.equal(response.headers.get('Content-Length'), '0', range);
    assert.equal(response.headers.get('Accept-Ranges'), 'bytes', range);
    assert.equal(await response.text(), '', range);
  }
});

test('If-Range requires an exact strong ETag match', async () => {
  const matches = await fetchVideo({
    headers: { Range: 'bytes=0-1', 'If-Range': assetHeaders.ETag },
    bodyChunks: paddedVideo(),
  });
  assert.equal(matches.upstream.headers.get('If-Range'), null);
  assert.equal(matches.response.status, 206);
  assert.equal(await matches.response.text(), '01');

  for (const validator of ['"old-version"', `W/${assetHeaders.ETag}`, 'Thu, 01 Jan 1970 00:00:00 GMT']) {
    const { response } = await fetchVideo({
      headers: { Range: 'bytes=0-1', 'If-Range': validator },
    });
    assert.equal(response.status, 200, validator);
    assert.equal(await response.text(), video, validator);
  }
});

test('asset errors, cache validators, and other representations are preserved', async () => {
  const headers = { Range: 'bytes=0-1', 'If-None-Match': assetHeaders.ETag };
  const cached = await fetchVideo({ headers, status: 304 });
  assert.equal(cached.upstream.headers.get('If-None-Match'), assetHeaders.ETag);
  assert.equal(cached.response.status, 304);
  assert.equal(await cached.response.text(), '');

  for (const [status, overrides] of [
    [404, { 'Content-Type': 'text/html' }],
    [200, { 'Content-Type': 'text/html' }],
    [200, { 'Content-Encoding': 'gzip' }],
  ]) {
    const { response } = await fetchVideo({ headers, status, overrides });
    assert.equal(response.status, status);
    assert.equal(response.headers.get('Content-Range'), null);
    assert.equal(await response.text(), video);
  }
});

test('binding length may be omitted but any reported length must match the manifest', async () => {
  const headers = { Range: 'bytes=0-1' };
  for (const length of ['0', 'invalid', String(videoSize - 1), String(maxVideoSize + 1)]) {
    const { response } = await fetchVideo({ headers, overrides: { 'Content-Length': length } });
    assert.equal(response.status, 502);
    assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.equal(await response.text(), '');
  }
  const { response } = await fetchVideo({
    headers,
    overrides: { 'Content-Length': String(videoSize) },
    bodyChunks: paddedVideo(),
  });
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Content-Range'), `bytes 0-1/${videoSize}`);
  assert.equal(await response.text(), '01');
});

test('a missing, failed, encoded or invalid static part rejects a short range before sending 206', async () => {
  const invalidParts = {
    missing: () => new Response(null, { status: 404 }),
    failed: () => new Response(null, { status: 503 }),
    rejected: () => Promise.reject(new Error('Static part fetch failed')),
    wrongType: (_index, part, headers) => new Response(part, {
      headers: { ...headers, 'Content-Type': 'text/html' },
    }),
    encoded: (_index, part, headers) => new Response(part, {
      headers: { ...headers, 'Content-Encoding': 'gzip' },
    }),
    wrongLength: (_index, part, headers) => new Response(part, {
      headers: { ...headers, 'Content-Length': String(part.byteLength - 1) },
    }),
    truncated: (_index, part, headers) => new Response(part.subarray(0, part.length - 1), { headers }),
  };
  for (const [label, partResponse] of Object.entries(invalidParts)) {
    const { response, traffic } = await fetchVideo({
      headers: { Range: 'bytes=1-6' }, bodyChunks: paddedVideo(), partResponse,
    });
    assert.equal(response.status, 502, label);
    assert.equal(response.headers.get('Cache-Control'), 'no-store', label);
    assert.equal(response.headers.get('Content-Range'), null, label);
    assert.equal(await response.text(), '', label);
    assert.deepEqual(traffic, { assetPulls: 0, assetCancels: 1, parts: [0] }, label);
  }
});

test('large explicit ranges propagate errors in the existing stream', async () => {
  const headers = { Range: `bytes=1-${partSize + 6}` };
  const truncated = await fetchVideo({ headers, bodyChunks: ['01', '23'] });
  const oversized = await fetchVideo({
    headers: { Range: 'bytes=-99999999999999999999' }, bodyChunks: [...paddedVideo(), 'extra'],
  });
  for (const { response, traffic } of [truncated, oversized]) {
    assert.deepEqual(traffic.parts, []);
    assert.equal(response.status, 206);
    await assert.rejects(response.arrayBuffer(), /Unexpected video body length/);
  }
});
