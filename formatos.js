/* Lectura directa: dos vistas del cuento y una descarga independiente. */
(function(global){
 'use strict';
 const MODES=Object.freeze(['video','audio-text']);
 function normalizeMode(value){return MODES.includes(value)?value:MODES[0];}
 function safeLocalURL(value){
  if(typeof value!=='string'||value.length>2048||!/^(?:media|assets)\/[A-Za-z0-9._/%#?=&-]+$/.test(value))return '';
  let decoded;try{decoded=decodeURIComponent(value.split(/[?#]/,1)[0]);}catch(_){return '';}
  return decoded.split('/').some(part=>part==='..'||part==='.')?'':value;
 }
 function pausePreservingPosition(media){if(media&&typeof media.pause==='function')media.pause();}
 function videoFailureMessage(state){return state.mode==='video'&&state.hasSource&&[1,2,3,4].includes(state.errorCode)?'No se puede cargar el vídeo. Elige «Audio y texto» para seguir el cuento.':'';}
 if(typeof module==='object'&&module.exports)module.exports=Object.freeze({normalizeMode,safeLocalURL,pausePreservingPosition,videoFailureMessage});
 if(!global.document)return;
 const document=global.document,controllers=new Set(),mounted=new WeakMap();
 function el(tag,className,text){const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=text;return e;}
 function p(parent,text){const e=el('p','',text);parent.append(e);return e;}
 function localLink(label,value){const url=safeLocalURL(value);if(!url)return null;const a=el('a','format-document-link',label);a.href=url;a.target='_blank';a.rel='noopener';return a;}
 function stopOwnedMedia(except=null){controllers.forEach(c=>{if(c.video!==except)pausePreservingPosition(c.video);});}
 function pauseAll(){stopOwnedMedia();controllers.values().next().value?.pauseBase();}
 function enhance(section,route,options={}){
  if(!section||!route||mounted.has(section))return mounted.get(section)||null;
  const book=global.MitoMapaFormatData?.books?.find(b=>b.slug===route.id);
  const grid=section.querySelector('.route-grid'),support=section.querySelector('.reading-support'),story=grid?.querySelector('.story'),narrator=support?.querySelector('.narrator');
  if(!book||!grid||!support||!story||!narrator)return null;
  const id=route.id;let mode;
  const pauseBase=()=>{if(typeof options.pauseBase==='function')options.pauseBase();else options.stopBase?.();};
  const group=e=>{e.dataset.routeFlowGroup='cuento';return e;};
  const picker=group(el('section','format-picker'));picker.id=`format-picker-${id}`;picker.setAttribute('aria-label','Cómo seguir el cuento');
  const choices=el('fieldset','format-options');choices.append(el('legend','','Formato del cuento'));
  if(!grid.id)grid.id=`format-reading-${id}`;
  const labels={'video':'Vídeo','audio-text':'Audio y texto'};
  const radios=MODES.map(value=>{
   const l=el('label','format-option'),r=el('input');r.type='radio';r.name=`format-${id}`;r.value=value;
   r.setAttribute('aria-controls',value==='video'?`format-video-${id}`:`${support.id} ${grid.id}`);
   l.append(r,el('span','',labels[value]));choices.append(l);r.addEventListener('change',()=>{if(r.checked)selectMode(r.value);});return r;
  });
  const pdf=localLink('↓ Descargar cuento (PDF)',book.pdf);
  if(pdf){pdf.className='format-pdf-download button secondary';pdf.removeAttribute('target');pdf.removeAttribute('rel');pdf.download=`MitoMapa_${id.replaceAll('-','_')}_Cuento.pdf`;}
  picker.append(choices);if(pdf)picker.append(pdf);support.before(picker);
  narrator.querySelector('h3').textContent='Escucha el cuento';
  const videoPanel=group(el('section','format-video-panel'));videoPanel.id=`format-video-${id}`;videoPanel.hidden=true;videoPanel.setAttribute('aria-label',`Vídeo de ${book.title}`);
  const video=el('video','format-video-player');video.controls=true;video.playsInline=true;video.preload='none';video.poster=safeLocalURL(book.poster);video.setAttribute('aria-label',`Vídeo del cuento: ${book.title}`);
  const status=el('p','format-video-status');status.id=`format-video-status-${id}`;status.setAttribute('role','status');status.setAttribute('aria-live','polite');video.setAttribute('aria-describedby',status.id);
  const track=el('track');track.kind='captions';track.srclang='es';track.label='Español';track.default=false;track.src=safeLocalURL(book.captions||`media/${id}/subtitulos.vtt`);video.append(track);
  videoPanel.append(video,status);grid.after(videoPanel);
  const info=group(el('div','format-information')),links=el('div','format-links');
  for(const [label,url] of [['Fuentes del cuento',book.sources?.local_url||global.MitoMapaFormatData.sources_url],['Créditos de narración y sonidos','media/creditos-audio.html']]){const link=localLink(label,url);if(link)links.append(link);}
  const credits=el('details','format-credits');credits.append(el('summary','','Autoría y medios del cuento'));
  p(credits,'Autoría: '+(book.credits?.authors||[]).join(', ')+'.');p(credits,'Narración: '+(book.credits?.narrator||global.MitoMapaFormatData.narrator)+'.');
  if(book.credits?.illustrations)p(credits,book.credits.illustrations);if(book.credits?.license)p(credits,book.credits.license);
  info.append(links,credits);videoPanel.after(info);
  const controller={video,section,pauseBase};controllers.add(controller);mounted.set(section,controller);
  function selectMode(value){
   const next=normalizeMode(value);if(mode===next)return;
   if(mode!==undefined){pauseBase();stopOwnedMedia();}
   mode=next;section.dataset.contentFormat=mode;
   radios.forEach(r=>{r.checked=r.value===mode;});
   const showVideo=mode==='video';
   grid.hidden=showVideo;
   support.hidden=showVideo;
   videoPanel.hidden=!showVideo;
   if(mode==='video'&&!video.hasAttribute('src'))video.src=safeLocalURL(book.video);
  }
  video.addEventListener('play',()=>{if(mode!=='video'||!section.classList.contains('active')){pausePreservingPosition(video);return;}status.textContent='';pauseBase();stopOwnedMedia(video);});
  video.addEventListener('error',()=>{const message=videoFailureMessage({mode,hasSource:video.hasAttribute('src'),errorCode:video.error?.code});if(message)status.textContent=message;});
  section.querySelector('.narration-play')?.addEventListener('click',()=>stopOwnedMedia(),true);
  selectMode();return controller;
 }
 document.addEventListener('mitomapa:route-step',event=>{if(event.detail?.step!=='cuento')pauseAll();});
 global.addEventListener('hashchange',pauseAll);global.addEventListener('pagehide',pauseAll);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pauseAll();});
 global.MitoMapaFormats=Object.freeze({enhance,stopOwnedMedia});
})(typeof window==='object'?window:globalThis);
