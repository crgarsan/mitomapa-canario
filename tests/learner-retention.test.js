const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const vm=require('node:vm');

const SESSION='mitomapa-canario-sesion-v1';
const RETENTION='mitomapa-canario-caducidad-v1';
const PREFS='mitomapa-canario-preferencias-v3';
const WORK='mitomapa-canario-cuaderno-v1';
const START=1795168800000;
const scoped=(key,generation)=>generation?`${SESSION}:${generation}:${key}`:key;

function fixture(entries={}){
  const values=new Map(Object.entries(entries));
  let now=START, counter=0;
  const storage={
    getItem:key=>values.get(key)??null,
    setItem(key,value){values.set(key,String(value));},
    removeItem:key=>values.delete(key),
  };
  const window={localStorage:storage};
  const navigator={};
  vm.runInNewContext(readFileSync(new URL('../learner-retention.js',`file://${__filename}`),'utf8'),{
    window,navigator,Date:{now:()=>now},crypto:{getRandomValues:bytes=>bytes.fill(++counter)},
  });
  return {api:window.MitoMapaRetention,storage,values,navigator,at:value=>{now=value;}};
}

test('undated work receives one full window which visits do not extend',async()=>{
  const f=fixture({[WORK]:'existing work'});
  assert.equal((await f.api.prepare()).expiresAt,1796464800000);
  f.at(1796378400000);
  assert.equal((await f.api.prepare()).expiresAt,1796464800000);
  assert.equal(f.values.get(WORK),'existing work');
  f.at(1796464799999);
  assert.equal((await f.api.prepare()).generation,null);
  f.at(1796464800000);
  assert.notEqual((await f.api.prepare()).generation,null);
  assert.equal(f.values.has(WORK),false);
});

test('expiry clears identifying work but preserves reading and other applications',async()=>{
  const f=fixture({[SESSION]:'old',
    [scoped(RETENTION,'old')]:JSON.stringify({startedAt:1793872800000}),
    [scoped(PREFS,'old')]:JSON.stringify({learnerName:'Fictitious learner',lastRouteId:'tenerife',readerMode:'guided',learningLevel:'advanced',selectedVoiceURI:'local-voice',narrationAmbient:false}),
    [scoped(WORK,'old')]:'Fictitious text and drawing',
    'mitomapa-canario-lectura-v1':'large text',
    'mitomapa-language':'en','mitomapa-canario-formulario-web-v1':'configured form',
    'other-application':'keep'});
  const state=(await f.api.prepare());
  assert.equal(state.cleared,true);
  assert.equal(state.generation.startsWith('l-'),false);
  assert.equal(state.expiresAt,1796464800000);
  assert.deepEqual(JSON.parse(f.values.get(scoped(PREFS,state.generation))),{
    readerMode:'guided',learningLevel:'advanced',selectedVoiceURI:'local-voice',narrationAmbient:false});
  assert.equal(f.values.has(scoped(WORK,'old')),false);
  assert.equal(f.values.has(scoped(RETENTION,'old')),false);
  assert.equal(f.values.get('mitomapa-canario-lectura-v1'),'large text');
  assert.equal(f.values.get('mitomapa-language'),'en');
  assert.equal(f.values.get('mitomapa-canario-formulario-web-v1'),'configured form');
  assert.equal(f.values.get('other-application'),'keep');
  assert.doesNotMatch(JSON.stringify([...f.values]),/Fictitious/);
});

test('quota failure removes only expired work before retrying an empty generation',async()=>{
  const f=fixture({[RETENTION]:JSON.stringify({startedAt:1793872800000}),[WORK]:'expired'});
  const set=f.storage.setItem;
  f.storage.setItem=(key,value)=>{
    if(f.values.has(WORK)){const error=new Error('Full');error.name='QuotaExceededError';throw error;}
    set(key,value);
  };
  assert.equal((await f.api.prepare()).cleared,true);
  assert.equal(f.values.has(WORK),false);
});

test('blocked writes never expose known expired work or pretend cleanup succeeded',async()=>{
  const f=fixture({[RETENTION]:JSON.stringify({startedAt:1793872800000}),[WORK]:'expired'});
  f.storage.setItem=()=>{throw new Error('Denied');};
  const state=(await f.api.prepare());
  assert.equal(state.blocked,true);
  assert.equal(state.unavailable,true);
  assert.notEqual(state.cleared,true);
  assert.equal(f.values.get(WORK),'expired');
});

test('a concurrent fresh generation is adopted without erasing its work',async()=>{
  const f=fixture({[RETENTION]:JSON.stringify({startedAt:1793872800000}),[WORK]:'expired'});
  const set=f.storage.setItem;
  let switched=false;
  f.storage.setItem=(key,value)=>{
    set(key,value);
    if(!switched&&key.includes(RETENTION)&&key!==RETENTION){
      switched=true;
      set(SESSION,'fresh');set(scoped(RETENTION,'fresh'),JSON.stringify({startedAt:START}));
      set(scoped(WORK,'fresh'),'newly imported work');
    }
  };
  assert.equal((await f.api.prepare()).generation,'fresh');
  assert.equal(f.values.get(scoped(WORK,'fresh')),'newly imported work');
});

test('malformed and future timestamps cannot extend an established window indefinitely',async()=>{
  for(const record of ['{broken',JSON.stringify({startedAt:START+1})]){
    const f=fixture({[RETENTION]:record,[WORK]:'old work'});
    const state=(await f.api.prepare());
    assert.equal(state.cleared,true);
    assert.equal(state.expiresAt,1796464800000);
    assert.equal(f.values.has(WORK),false);
  }
});

test('failed deletion is retried on the next visit instead of abandoning expired data',async()=>{
  const f=fixture({[SESSION]:'expired-generation',
    [scoped(RETENTION,'expired-generation')]:JSON.stringify({startedAt:1793872800000}),
    [scoped(WORK,'expired-generation')]:'expired identifying work'});
  const remove=f.storage.removeItem;
  f.storage.removeItem=()=>{throw new Error('Deletion temporarily blocked');};
  assert.equal((await f.api.prepare()).unavailable,true);
  f.storage.removeItem=remove;
  assert.notEqual((await f.api.prepare()).unavailable,true);
  assert.equal(f.values.has(scoped(WORK,'expired-generation')),false);
});

test('expiry waits for a simultaneous import and adopts its fresh work',async()=>{
  const f=fixture({[RETENTION]:JSON.stringify({startedAt:1793872800000}),[WORK]:'old work'});
  let finishImport;
  const importing=new Promise(resolve=>{finishImport=()=>{
    f.values.set(SESSION,'l-imported');
    f.values.set(scoped(RETENTION,'l-imported'),JSON.stringify({startedAt:START}));
    f.values.set(scoped(WORK,'l-imported'),'new imported work');
    resolve();
  };});
  f.navigator.locks={request:async(name,callback)=>{await importing;return callback();}};
  const prepared=f.api.prepare();
  finishImport();
  assert.equal((await prepared).generation,'l-imported');
  assert.equal(f.values.get(scoped(WORK,f.values.get(SESSION))),'new imported work');
});

test('an expired runtime guard leaves publication to the serialized bootstrap',()=>{
  const f=fixture({[RETENTION]:JSON.stringify({startedAt:1793872800000}),[WORK]:'old work'});
  assert.equal(f.api.ensure().expired,true);
  assert.equal(f.values.has(SESSION),false);
});

test('cleanup adopts a generation published while old keys are being removed',()=>{
  const f=fixture({[SESSION]:'current',
    [scoped(RETENTION,'current')]:JSON.stringify({startedAt:START,pendingRemoval:['obsolete']}),
    [scoped(WORK,'obsolete')]:'old work'});
  const remove=f.storage.removeItem;
  let changed=false;
  f.storage.removeItem=key=>{
    remove(key);
    if(!changed){
      changed=true;
      f.values.set(SESSION,'newly-imported');
      f.values.set(scoped(RETENTION,'newly-imported'),JSON.stringify({startedAt:START}));
      f.values.set(scoped(WORK,'newly-imported'),'fresh work');
    }
  };
  assert.equal(f.api.ensure().generation,'newly-imported');
  assert.equal(f.values.get(scoped(WORK,'newly-imported')),'fresh work');
});
