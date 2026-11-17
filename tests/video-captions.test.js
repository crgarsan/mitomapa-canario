const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

// Execute the production track construction, with only the DOM boundary replaced.
// This catches accidentally enabling captions when a video already prints its text.
function createProductionTrack(book={captions:'media/la-palma/subtitulos.vtt'}){
 const source=fs.readFileSync(path.resolve(__dirname,'../formatos.js'),'utf8');
 const start=source.indexOf("const track=el('track')");
 const appendTrack='video.append(track);';
 const appendAt=source.indexOf(appendTrack,start);
 const end=appendAt+appendTrack.length;
 assert.ok(start>=0&&appendAt>start,'production caption construction must be present');
 const appended=[];
 const context={
  book,id:'la-palma',
  el(tag){assert.equal(tag,'track');return {default:false};},
  safeLocalURL(value){return value;},
  video:{append(track){appended.push(track);}}
 };
 vm.createContext(context);
 vm.runInContext(source.slice(start,end),context);
 assert.equal(appended.length,1);
 return appended[0];
}

test('video captions are optional on first load while the Spanish track remains available',()=>{
 const track=createProductionTrack();
 assert.equal(track.default,false);
 assert.equal(track.kind,'captions');
 assert.equal(track.srclang,'es');
 assert.equal(track.label,'Español');
 assert.equal(track.src,'media/la-palma/subtitulos.vtt');
});

test('a story without an explicit captions path retains its local Spanish caption file',()=>{
 const track=createProductionTrack({});
 assert.equal(track.default,false);
 assert.equal(track.src,'media/la-palma/subtitulos.vtt');
});
