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
const videoSize = mediaManifest.files[videoPath.slice(1)].bytes;
const encoder = new TextEncoder();
const assetHeaders = {
  'Cache-Control': 'public, max-age=0, must-revalidate',
  'Content-Digest': 'sha-256=:dGVzdA==:',
  'Content-Type': 'video/mp4',
  'ETag': '"asset-version"',
  'X-Content-Type-Options': 'nosniff',
};

function paddedVideo() {
  // Reuse a chunk to simulate the complete asset without holding a full MP4 in memory.
  const padding = new Uint8Array(512 * 1024);
  const missing = videoSize - video.length;
  return ['01', '234', '5', ...Array(Math.floor(missing / padding.length)).fill(padding),
    padding.subarray(0, missing % padding.length), '6789'];
}

const originalFixedLengthStream = globalThis.FixedLengthStream;
let worker;

before(async () => {
  ({ default: worker } = await import('../tools/story-video-ranges.mjs'));
  // Model the Workers-only stream's exact-length checks with the Node Streams API.
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
} = {}) {
  const request = new Request(origin + path, { method, headers });
  let upstream;
  const env = {
    ASSETS: {
      fetch(assetRequest) {
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
            if (nextChunk === bodyChunks.length) {
              controller.close();
              return;
            }
            const chunk = bodyChunks[nextChunk++];
            controller.enqueue(typeof chunk === 'string' ? encoder.encode(chunk) : chunk);
          },
        });
        return new Response(body, { status, headers: responseHeaders });
      },
    },
  };

  const response = await worker.fetch(request, env);
  assert.equal(upstream.url, request.url);
  assert.equal(upstream.method, method);
  return { request, upstream, response };
}

test('only the eight story MP4s are served in ranges', async () => {
  const islands = [
    'el-hierro', 'fuerteventura', 'gran-canaria', 'la-gomera', 'la-graciosa', 'la-palma',
    'lanzarote', 'tenerife',
  ];
  const routes = islands.map(island => `/media/${island}/cuento.mp4`);
  const config = JSON.parse(readFileSync(join(__dirname, '../wrangler.jsonc'), 'utf8'));
  assert.deepEqual([...config.assets.run_worker_first].sort(), [...routes].sort());
  const manifestRoutes = Object.keys(mediaManifest.files)
    .filter(path => /^media\/[^/]+\/cuento\.mp4$/.test(path))
    .map(path => '/' + path);
  assert.deepEqual(manifestRoutes.sort(), [...routes].sort());

  for (const island of islands) {
    const path = `/media/${island}/cuento.mp4`;
    const size = mediaManifest.files[path.slice(1)].bytes;
    assert.equal(statSync(join(__dirname, '..', path)).size, size, island);
    assert.ok(Number.isSafeInteger(size) && size > 0 && size <= maxVideoSize, island);
    const { response } = await fetchVideo({
      path: `${path}?v=1`,
      headers: { Range: 'bytes=0-1' },
    });
    assert.equal(response.status, 206, island);
    assert.equal(response.headers.get('Content-Range'), `bytes 0-1/${size}`, island);
    assert.equal(await response.text(), '01', island);
  }
  for (const path of ['/media/otra-isla/cuento.mp4', '/media/la-palma/otro.mp4', '/index.html']) {
    const { request, upstream, response } = await fetchVideo({
      path,
      headers: { Range: 'bytes=0-1' },
    });
    assert.equal(upstream, request);
    assert.equal(response.status, 200);
    assert.equal(await response.text(), video);
  }
});

test('206 streams exact bytes across chunks and retains asset metadata', async () => {
  const { upstream, response } = await fetchVideo({
    headers: { Range: 'bytes=1-6', 'Accept-Encoding': 'gzip, br' },
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
});

test('open-ended and suffix ranges use the complete asset length', async () => {
  const end = videoSize - 1;
  const cases = [
    [`bytes=${end - 2}-`, end - 2, '789'],
    ['bytes=-3', end - 2, '789'],
    [`bytes=000${end - 1}-99999999999999999999`, end - 1, '89'],
  ];
  for (const [range, start, body] of cases) {
    const { response } = await fetchVideo({ headers: { Range: range }, bodyChunks: paddedVideo() });
    assert.equal(response.status, 206, range);
    assert.equal(response.headers.get('Content-Range'), `bytes ${start}-${end}/${videoSize}`, range);
    assert.equal(response.headers.get('Content-Length'), String(body.length), range);
    assert.equal(await response.text(), body, range);
  }
  const hugeSuffix = await fetchVideo({
    headers: { Range: 'bytes=-99999999999999999999' }, bodyChunks: paddedVideo(),
  });
  assert.equal(hugeSuffix.response.status, 206);
  assert.equal(hugeSuffix.response.headers.get('Content-Range'), `bytes 0-${end}/${videoSize}`);
  await hugeSuffix.response.body.cancel();
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
  });
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Content-Range'), `bytes 0-1/${videoSize}`);
  assert.equal(await response.text(), '01');
});

test('a truncated or oversized upstream body errors the partial response', async () => {
  const headers = { Range: 'bytes=1-6' };
  const truncated = await fetchVideo({ headers, bodyChunks: ['01', '23'] });
  assert.equal(truncated.response.status, 206);
  await assert.rejects(truncated.response.text(), /Unexpected video body length/);

  const oversized = await fetchVideo({
    headers: { Range: 'bytes=-3' }, bodyChunks: [...paddedVideo(), 'extra'],
  });
  assert.equal(oversized.response.status, 206);
  await assert.rejects(oversized.response.text(), /Unexpected video body length/);
});
