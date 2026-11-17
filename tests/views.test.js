const test=require('node:test');const assert=require('node:assert/strict');
const f=require('../formatos.js');
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
