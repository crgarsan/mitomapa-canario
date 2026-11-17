const test=require('node:test');const assert=require('node:assert/strict');
const f=require('../formatos.js');
const english=require('../formatos-en.js');
test('only two interactive views remain, with video as the default',()=>{assert.equal(f.normalizeMode('video'),'video');assert.equal(f.normalizeMode('audio-text'),'audio-text');for(const mode of ['audio','book',undefined,'pdf'])assert.equal(f.normalizeMode(mode),'video');});
test('pausing a view retains its media position and source',()=>{const m={currentTime:24.5,src:'media/tenerife/cuento.mp4',paused:false,pause(){this.paused=true;}};f.pausePreservingPosition(m);assert.equal(m.paused,true);assert.equal(m.currentTime,24.5);assert.equal(m.src,'media/tenerife/cuento.mp4');f.pausePreservingPosition(null);});
test('only local safe document and media paths are accepted',()=>{assert.equal(f.safeLocalURL('media/tenerife/cuento-ilustrado.pdf'),'media/tenerife/cuento-ilustrado.pdf');for(const u of ['javascript:alert(1)','https://x/a','media/../private','media/%2e%2e/private'])assert.equal(f.safeLocalURL(u),'');});

test('a video error points to the available reading format', () => {
  assert.equal(
    f.videoFailureMessage({mode: 'video', hasSource: true, errorCode: 2}),
    'No se puede cargar el vídeo. Elige «Audio y texto» para seguir el cuento.',
  );
  assert.equal(f.videoFailureMessage({mode: 'audio-text', hasSource: true, errorCode: 2}), '');
});

test('Chrome on iPhone gets the full-video option before an error', () => {
  assert.equal(english.showFullVideoInitially('Mozilla/5.0 (iPhone; CPU iPhone OS 26_0) CriOS/142.0 Mobile Safari/604.1'), true);
  assert.equal(english.showFullVideoInitially('Mozilla/5.0 (iPhone; CPU iPhone OS 26_0) Version/26.0 Mobile Safari/604.1'), false);
  assert.equal(english.showFullVideoInitially('Mozilla/5.0 (Linux; Android 13; Pixel 7) Chrome/145.0 Mobile Safari/537.36'), false);
});

test('the full-video retry uses a same-origin non-range GET with an abort signal', async () => {
  const path = 'en/media/lanzarote/story.mp4';
  const {signal} = new AbortController();
  const blob = await english.loadFullVideo(path, signal, async (source, settings) => {
    assert.equal(source, path);
    assert.equal(settings.signal, signal);
    assert.equal(settings.mode, 'same-origin');
    assert.equal(settings.redirect, 'error');
    assert.equal(settings.method, 'GET');
    assert.equal(new Headers(settings.headers).has('Range'), false);
    return new Response('clip bytes', {headers: {'Content-Type': 'video/mp4', 'Content-Length': '10'}});
  });
  assert.equal(blob.size, 10);
  assert.equal(await blob.text(), 'clip bytes');
});

test('the full-video retry rejects unexpected sources and invalid media responses', async () => {
  for (const source of ['https://example.org/story.mp4', 'en/media/../story.mp4', 'en/media/lanzarote/story.mp4?retry=1']) {
    await assert.rejects(english.loadFullVideo(source, undefined, () => assert.fail('Unexpected request')));
  }
  const path = 'en/media/lanzarote/story.mp4';
  for (const [body, status, headers] of [
    ['partial', 206, {'Content-Type': 'video/mp4'}],
    ['error', 200, {'Content-Type': 'text/html'}],
    ['empty', 200, {'Content-Type': 'video/mp4', 'Content-Length': '0'}],
    ['too large', 200, {'Content-Type': 'video/mp4', 'Content-Length': String(25 * 1024 * 1024 + 1)}],
    ['short', 200, {'Content-Type': 'video/mp4', 'Content-Length': '100'}],
  ]) {
    await assert.rejects(english.loadFullVideo(path, undefined, async () => new Response(body, {status, headers})));
  }
});
