/* Lectura directa: dos vistas del cuento y una descarga independiente. */
(function(global){
 'use strict';
 const MODES=Object.freeze(['video','audio-text']);
 const MAX_VIDEO_BYTES=25*1024*1024;
 function normalizeMode(value){return MODES.includes(value)?value:MODES[0];}
 function safeLocalURL(value){
  if(typeof value!=='string'||value.length>2048||!/^(?:en\/media|media|assets)\/[A-Za-z0-9._/%#?=&-]+$/.test(value))return '';
  let decoded;try{decoded=decodeURIComponent(value.split(/[?#]/,1)[0]);}catch(_){return '';}
  return decoded.split('/').some(part=>part==='..'||part==='.')?'':value;
 }
 function pausePreservingPosition(media){if(media&&typeof media.pause==='function')media.pause();}
 function videoFailureMessage(state){return state.mode==='video'&&state.hasSource&&[1,2,3,4].includes(state.errorCode)?"The video could not load. Open the separate player or choose “Audio and text”.":'';}
 async function loadFullVideo(source,signal,fetcher=global.fetch.bind(global)){
  if(typeof source!=='string'||!/^en\/media\/[a-z0-9-]+\/story\.mp4$/.test(source))throw new Error('Unexpected video source');
  const response=await fetcher(source,{method:'GET',mode:'same-origin',cache:'reload',redirect:'error',signal});
  const type=response.headers.get('Content-Type')?.split(';',1)[0].trim().toLowerCase();
  const contentLength=response.headers.get('Content-Length');
  const length=contentLength===null?null:Number(contentLength);
  if(response.status!==200||type!=='video/mp4'||(length!==null&&(!/^\d+$/.test(contentLength)||length<1||length>MAX_VIDEO_BYTES))){
   void response.body?.cancel().catch(()=>{});
   throw new Error('Unexpected video response');
  }
  if(length!==null){
   const blob=await response.blob();
   if(blob.size!==length)throw new Error('Incomplete video');
   return blob;
  }
  const reader=response.body?.getReader();
  if(!reader)throw new Error('Unavailable video body');
  const chunks=[];
  let size=0;
  try{
   for(let chunk=await reader.read();!chunk.done;chunk=await reader.read()){
    size+=chunk.value.byteLength;
    if(size>MAX_VIDEO_BYTES)throw new Error('Unexpected video size');
    chunks.push(chunk.value);
   }
  }catch(error){
   void reader.cancel().catch(()=>{});
   throw error;
  }
  if(!size)throw new Error('Empty video');
  return new Blob(chunks,{type});
 }
 if(typeof module==='object'&&module.exports)module.exports=Object.freeze({normalizeMode,safeLocalURL,pausePreservingPosition,videoFailureMessage,loadFullVideo});
 if(!global.document)return;
 const document=global.document,controllers=new Set(),mounted=new WeakMap();
 function el(tag,className,text){const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=text;return e;}
 function p(parent,text){const e=el('p','',text);parent.append(e);return e;}
 function localLink(label,value){const url=safeLocalURL(value);if(!url)return null;const a=el('a','format-document-link',label);a.href=url;a.target='_blank';a.rel='noopener';return a;}
 function stopOwnedMedia(except=null,release=true){
  controllers.forEach(c=>{
   if(c.video===except)return;
   pausePreservingPosition(c.video);
   if(release)c.releaseFullVideo();
  });
 }
 function pauseAll(release=true){stopOwnedMedia(null,release);controllers.values().next().value?.pauseBase();}
 function enhance(section,route,options={}){
  if(!section||!route||mounted.has(section))return mounted.get(section)||null;
  const book=global.MitoMapaFormatData?.books?.find(b=>b.slug===route.id);
  const grid=section.querySelector('.route-grid'),support=section.querySelector('.reading-support'),story=grid?.querySelector('.story'),narrator=support?.querySelector('.narrator');
  if(!book||!grid||!support||!story||!narrator)return null;
  const id=route.id;let mode;
  const videoSource=safeLocalURL(book.video);
  const pauseBase=()=>{if(typeof options.pauseBase==='function')options.pauseBase();else options.stopBase?.();};
  const group=e=>{e.dataset.routeFlowGroup='cuento';return e;};
  const picker=group(el('section','format-picker'));picker.id=`format-picker-${id}`;picker.setAttribute('aria-label',"How to experience the story");
  const choices=el('fieldset','format-options');choices.append(el('legend','',"Story format"));
  if(!grid.id)grid.id=`format-reading-${id}`;
  const labels={'video':'Video','audio-text':"Audio and text"};
  const radios=MODES.map(value=>{
   const l=el('label','format-option'),r=el('input');r.type='radio';r.name=`format-${id}`;r.value=value;
   r.setAttribute('aria-controls',value==='video'?`format-video-${id}`:`${support.id} ${grid.id}`);
   l.append(r,el('span','',labels[value]));choices.append(l);r.addEventListener('change',()=>{if(r.checked)selectMode(r.value);});return r;
  });
  const pdf=localLink("↓ Download story (PDF)",book.pdf);
  if(pdf){pdf.className='format-pdf-download button secondary';pdf.removeAttribute('target');pdf.removeAttribute('rel');pdf.download=`MitoMapa_${id.replaceAll('-','_')}_Story.pdf`;}
  picker.append(choices);if(pdf)picker.append(pdf);support.before(picker);
  narrator.querySelector('h3').textContent="Listen to the story";
  const videoPanel=group(el('section','format-video-panel'));videoPanel.id=`format-video-${id}`;videoPanel.hidden=true;videoPanel.setAttribute('aria-label',`Video of ${book.title}`);
  const video=el('video','format-video-player');video.id=`story-video-${id}`;video.controls=true;video.playsInline=true;video.preload='none';video.poster=safeLocalURL(book.poster);video.setAttribute('aria-label',`Story video: ${book.title}`);
  const status=el('p','format-video-status');status.id=`format-video-status-${id}`;status.setAttribute('role','status');status.setAttribute('aria-live','polite');video.setAttribute('aria-describedby',status.id);
  const videoLinks=el('div','format-links');
  const separatePlayer=el('a','format-document-link format-video-separate','Open video in a separate player');
  separatePlayer.href=`video-player-en.html?island=${encodeURIComponent(id)}`;
  const retry=el('button','button secondary format-video-retry','Load full video');
  retry.type='button';retry.setAttribute('aria-controls',video.id);retry.setAttribute('aria-describedby',status.id);
  const track=el('track');track.kind='captions';track.srclang='en';track.label="English";track.default=false;track.src=safeLocalURL(book.captions||`en/media/${id}/captions.vtt`);video.append(track);
  videoLinks.append(separatePlayer,retry);
  videoPanel.append(videoLinks,status,video);grid.after(videoPanel);
  const info=group(el('div','format-information')),links=el('div','format-links');
  for(const [label,url] of [["Story sources",book.sources?.local_url||global.MitoMapaFormatData.sources_url],["Narration and sound credits","media/creditos-audio-en.html"]]){const link=localLink(label,url);if(link)links.append(link);}
  const credits=el('details','format-credits');credits.append(el('summary','',"Story authors and media credits"));
  p(credits,"Authors: "+(book.credits?.authors||[]).join(', ')+'.');p(credits,"Narration: "+(book.credits?.narrator||global.MitoMapaFormatData.narrator)+'.');
  if(book.credits?.illustrations)p(credits,book.credits.illustrations);if(book.credits?.license)p(credits,book.credits.license);
  info.append(links,credits);videoPanel.after(info);
  let download=null,objectURL='',resumeAt=0;
  function releaseFullVideo(){
   const pending=download;
   if(!pending&&!objectURL)return;
   download=null;
   pending?.abort();
   retry.removeAttribute('aria-disabled');
   retry.textContent='Load full video';
   status.textContent='';
   if(!objectURL)return;
   if(video.currentTime>0&&!video.ended)resumeAt=video.currentTime;
   const obsoleteURL=objectURL;
   objectURL='';
   video.preload='none';
   video.src=videoSource;
   global.URL.revokeObjectURL(obsoleteURL);
  }
  video.addEventListener('loadedmetadata',()=>{
   if(resumeAt>0&&Number.isFinite(video.duration)){
    video.currentTime=Math.min(resumeAt,video.duration);
    resumeAt=0;
   }
  });
  retry.addEventListener('click',async()=>{
   if(download||mode!=='video'||!section.classList.contains('active'))return;
   if(objectURL){
    try{await video.play();}
    catch(_){status.textContent='Playback did not start. Open the separate player or choose “Audio and text”.';}
    return;
   }
   const attempt=new AbortController();
   download=attempt;
   retry.setAttribute('aria-disabled','true');
   status.textContent='Loading the full video…';
   try{
    const blob=await loadFullVideo(videoSource,attempt.signal);
    if(download!==attempt)return;
    if(video.currentTime>0&&!video.ended)resumeAt=video.currentTime;
    pausePreservingPosition(video);
    objectURL=global.URL.createObjectURL(blob);
    video.src=objectURL;
    video.preload='metadata';
    retry.textContent='Play video';
    status.textContent='Full video ready. Choose “Play video” to start.';
   }catch(_){
    if(download===attempt)status.textContent='The full video could not load. Open the separate player or choose “Audio and text”.';
   }finally{
    if(download===attempt){download=null;retry.removeAttribute('aria-disabled');}
   }
  });
  const controller={video,section,pauseBase,releaseFullVideo};controllers.add(controller);mounted.set(section,controller);
  function selectMode(value){
   const next=normalizeMode(value);if(mode===next)return;
   if(mode!==undefined){pauseBase();stopOwnedMedia();}
   mode=next;section.dataset.contentFormat=mode;
   radios.forEach(r=>{r.checked=r.value===mode;});
   const showVideo=mode==='video';
   grid.hidden=showVideo;
   support.hidden=showVideo;
   videoPanel.hidden=!showVideo;
   if(mode==='video'&&!video.hasAttribute('src'))video.src=videoSource;
  }
  video.addEventListener('play',()=>{if(mode!=='video'||!section.classList.contains('active')){pausePreservingPosition(video);return;}status.textContent='';pauseBase();stopOwnedMedia(video);});
  video.addEventListener('error',()=>{
   const message=videoFailureMessage({mode,hasSource:video.hasAttribute('src'),errorCode:video.error?.code});
   if(!message||download)return;
   if(objectURL)releaseFullVideo();
   status.textContent=message;
  });
  section.querySelector('.narration-play')?.addEventListener('click',()=>stopOwnedMedia(),true);
  selectMode();return controller;
 }
 document.addEventListener('mitomapa:route-step',event=>{if(event.detail?.step!=='cuento')pauseAll();});
 global.addEventListener('hashchange',()=>pauseAll());global.addEventListener('pagehide',()=>pauseAll());
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pauseAll(false);});
 global.MitoMapaFormats=Object.freeze({enhance,stopOwnedMedia});
})(typeof window==='object'?window:globalThis);
