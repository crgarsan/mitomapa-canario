const test=require('node:test');const assert=require('node:assert/strict');
const f=require('../formatos.js');
test('only two interactive views remain, with reading as the default',()=>{assert.equal(f.normalizeMode('video'),'video');for(const mode of ['audio-text','audio','book',undefined,'pdf'])assert.equal(f.normalizeMode(mode),'audio-text');});
test('pausing a view retains its media position and source',()=>{const m={currentTime:24.5,src:'media/tenerife/cuento.mp4',paused:false,pause(){this.paused=true;}};f.pausePreservingPosition(m);assert.equal(m.paused,true);assert.equal(m.currentTime,24.5);assert.equal(m.src,'media/tenerife/cuento.mp4');f.pausePreservingPosition(null);});
test('only local safe document and media paths are accepted',()=>{assert.equal(f.safeLocalURL('media/tenerife/cuento-ilustrado.pdf'),'media/tenerife/cuento-ilustrado.pdf');for(const u of ['javascript:alert(1)','https://x/a','media/../private','media/%2e%2e/private'])assert.equal(f.safeLocalURL(u),'');});
