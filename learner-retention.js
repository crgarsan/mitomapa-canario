/* Fixed local retention; no network, accounts or new browser permissions. */
(() => {
  'use strict';
  const sessionKey='mitomapa-canario-sesion-v1';
  const key='mitomapa-canario-caducidad-v1';
  const preferencesKey='mitomapa-canario-preferencias-v3';
  const lifetime=15*24*60*60*1000;
  const learnerKeys=[key,'mitomapa-canario-v1','mitomapa-canario-v2',preferencesKey,
    'mitomapa-canario-cuaderno-v1','mitomapa-canario-itinerarios-v1','mitomapa-canario-final-v1',
    'mitomapa-canario-ruta-acordada-v1','mitomapa-canario-secuencias-v1',
    'mitomapa-canario-comparaciones-v1','mitomapa-canario-ultimo-apartado-v1'];
  const scoped=(name,generation)=>generation?`${sessionKey}:${generation}:${name}`:name;
  const pending=raw=>Array.isArray(raw?.pendingRemoval)?raw.pendingRemoval.filter(value=>value===null||typeof value==='string'&&value.length<=80):[];
  function record(previous){
    const pendingRemoval=previous===undefined?[]:[previous,null];
    try{pendingRemoval.push(...pending(JSON.parse(window.localStorage.getItem(scoped(key,previous)))));}catch(error){ /* Storage status is checked by the caller. */ }
    return {startedAt:Date.now(),...(pendingRemoval.length?{pendingRemoval:[...new Set(pendingRemoval)]}:{})};
  }

  function safePreferences(storage,generation){
    try{
      const raw=JSON.parse(storage.getItem(scoped(preferencesKey,generation))||'{}');
      const result={};
      for(const name of ['readerMode','learningLevel','selectedVoiceURI','narrationAmbient']){
        if(typeof raw?.[name]===(name==='narrationAmbient'?'boolean':'string'))result[name]=raw[name];
      }
      return result;
    }catch(error){return {};}
  }

  function removeGeneration(storage,generation){
    for(const name of learnerKeys)storage.removeItem(scoped(name,generation));
  }

  function retryCleanup(storage,generation,saved){
    const removals=pending(saved);
    if(!removals.length)return false;
    try{
      for(const previous of removals){
        if(storage.getItem(sessionKey)!==generation)return true;
        if(previous!==generation)removeGeneration(storage,previous);
      }
      if(storage.getItem(sessionKey)!==generation)return true;
      storage.setItem(scoped(key,generation),JSON.stringify({startedAt:saved.startedAt}));
      return false;
    }catch(error){return true;}
  }

  function ensure(expire=false){
    let generation,expiresAt=null;
    try{
      const storage=window.localStorage;
      // Another tab can publish while we stage. Adopt its generation, never erase it.
      for(let attempt=0;attempt<3;attempt++){
        generation=storage.getItem(sessionKey);
        const raw=storage.getItem(scoped(key,generation));
        if(raw===null){
          const first=record();
          try{storage.setItem(scoped(key,generation),JSON.stringify(first));}
          catch(error){return {generation,expiresAt:null,unavailable:true};}
          if(storage.getItem(sessionKey)!==generation)continue;
          return {generation,expiresAt:first.startedAt+lifetime};
        }
        let saved,startedAt;
        try{saved=JSON.parse(raw);startedAt=saved?.startedAt;}catch(error){ /* Invalid dates expire safely. */ }
        expiresAt=Number.isSafeInteger(startedAt)&&startedAt>=0&&startedAt<=Date.now()?startedAt+lifetime:0;
        if(Date.now()<expiresAt){
          const unavailable=retryCleanup(storage,generation,saved);
          if(storage.getItem(sessionKey)!==generation)continue;
          return {generation,expiresAt,unavailable};
        }
        // Runtime guards hide/reload first. Bootstrap takes the same Web Lock as imports.
        if(!expire)return {generation,expiresAt,expired:true};

        const preferences=safePreferences(storage,generation);
        // The l- prefix belongs exclusively to the app's Web Lock transactions.
        const next=Array.from(crypto.getRandomValues(new Uint8Array(16)),byte=>byte.toString(16).padStart(2,'0')).join('');
        const fresh=record(generation);
        const stage=()=>{
          storage.setItem(scoped(preferencesKey,next),JSON.stringify(preferences));
          storage.setItem(scoped(key,next),JSON.stringify(fresh));
        };
        try{
          try{stage();}
          catch(error){
            if(error.name!=='QuotaExceededError'||storage.getItem(sessionKey)!==generation)throw error;
            // Only data whose deadline has passed may make room for an empty session.
            removeGeneration(storage,generation);
            stage();
          }
          if(storage.getItem(sessionKey)!==generation){removeGeneration(storage,next);continue;}
          storage.setItem(sessionKey,next);
          if(storage.getItem(sessionKey)!==next){removeGeneration(storage,next);continue;}
        }catch(error){
          try{if(storage.getItem(sessionKey)!==next)removeGeneration(storage,next);}catch(cleanupError){ /* Access can be blocked too. */ }
          return {generation,expiresAt,preferences,blocked:true,unavailable:true};
        }
        const unavailable=retryCleanup(storage,next,fresh);
        return {generation:next,expiresAt:fresh.startedAt+lifetime,cleared:true,unavailable};
      }
      return {generation,expiresAt,blocked:true,unavailable:true};
    }catch(error){return {generation:undefined,expiresAt,unavailable:true};}
  }

  let preparedState;
  async function prepare(){
    if(typeof navigator!=='undefined'&&navigator.locks){
      let started=false;
      try{preparedState=await navigator.locks.request(sessionKey,()=>{started=true;return ensure(true);});return preparedState;}
      catch(error){if(started)throw error;}
    }
    preparedState=ensure(true);
    return preparedState;
  }

  function initial(){
    const current=ensure();
    return current.expired&&preparedState?.blocked?preparedState:current;
  }
  window.MitoMapaRetention=Object.freeze({key,record,ensure,prepare,initial});
  const appSource=typeof document==='undefined'?null:document.currentScript?.dataset.appSrc;
  if(appSource){
    const failed=()=>{
      const notice=document.getElementById('storageNotice');
      if(notice){notice.hidden=false;notice.textContent=document.documentElement.lang==='en'?'MitoMapa could not start safely. Reload the page or try another browser.':'MitoMapa no pudo iniciarse de forma segura. Recarga la página o prueba otro navegador.';}
    };
    prepare().then(()=>{
      const app=document.createElement('script');
      app.src=appSource;
      app.addEventListener('error',failed);
      document.head.append(app);
    },failed);
  }
})();
