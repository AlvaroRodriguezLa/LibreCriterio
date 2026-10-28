import {
 READER_PREFERENCES_KEY, READER_PROGRESS_KEY, normalizePreferences, parsePreferences,
 normalizeManifest, parseProgress, normalizeProgress, mergeCompleted, sanitizeHeadingId,
 hasExplicitHash, shouldOfferResume, buildResumeHref, calculateChapterProgress,
 readStorageValue, writeStorageValue, removeStorageValue,
} from '../lib/reader-state.mjs';

type Preferences = {size:string; font:string; theme:string; focus:boolean};
type Chapter = {slug:string;title:string;number:number;url:string;partId:string};
type Bookmark = {slug:string;headingId:string;ratio:number;updatedAt:number};
type ReadingState = {bookmark:Bookmark|null;completedSlugs:string[]};

function startReader() {
 const html=document.documentElement;
 const storage=()=>localStorage;
 const safeRead=(key:string):string|null=>readStorageValue(storage,key);
 const safeWrite=(key:string,value:unknown)=>{const saved=writeStorageValue(storage,key,value);if(!saved){const notice=document.querySelector<HTMLElement>('[data-reader-storage]');if(notice)notice.hidden=false;}return saved;};
 const safeRemove=(key:string)=>removeStorageValue(storage,key);
 let manifest:Chapter[]=[];
 try{manifest=normalizeManifest(JSON.parse(document.querySelector('#book-manifest')?.textContent||'[]')) as Chapter[];}catch{/* Static reading works with an invalid/missing manifest. */}
 let preferences=parsePreferences(safeRead(READER_PREFERENCES_KEY)) as Preferences;
 let state=parseProgress(safeRead(READER_PROGRESS_KEY),manifest) as ReadingState;
 const article=document.querySelector<HTMLElement>('[data-reader-root]');
 const body=article?.querySelector<HTMLElement>('[data-reader-body]')||null;
 const chapter=manifest.find(item=>item.slug===article?.dataset.readerSlug)||null;
 const size=document.querySelector<HTMLSelectElement>('#reader-size');
 const font=document.querySelector<HTMLSelectElement>('#reader-font');
 const theme=document.querySelector<HTMLSelectElement>('#reader-theme');
 const focus=document.querySelector<HTMLInputElement>('#reader-focus');
 const finishButtons=Array.from(document.querySelectorAll<HTMLButtonElement>('[data-finish-chapter]'));
 finishButtons.forEach(button=>{button.hidden=false;button.dataset.readerOriginalLabel=button.textContent?.trim()||'Marcar capítulo como leído';});
 let dirty=false;
 let latestBookmark:Bookmark|null=null;
 let persistTimer:number|undefined;
 let frame=0;
 let pendingSave=false;
 let activeHeading:HTMLElement|null=null;
 const headings=body?Array.from(body.querySelectorAll<HTMLElement>('h2[id]')).filter(heading=>!heading.closest('details.chapter-sources')):[];
 const sectionLinks=Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-section-toc] a[href^="#"]'));
 const inline=document.querySelector<HTMLElement>('[data-resume-inline]');
 const initialBookmark=state.bookmark?{...state.bookmark}:null;

 function applyPreferences() {
  html.dataset.readerTheme=preferences.theme;
  html.dataset.readerFont=preferences.font;
  html.dataset.readerFocus=String(preferences.focus);
  html.style.setProperty('--reader-font-size',preferences.size+'px');
  if(size)size.value=preferences.size;
  if(font)font.value=preferences.font;
  if(theme)theme.value=preferences.theme;
  if(focus)focus.checked=preferences.focus;
 }
 function changePreferences(candidate:unknown) {
  preferences=normalizePreferences(candidate) as Preferences;
  applyPreferences();safeWrite(READER_PREFERENCES_KEY,preferences);scheduleUpdate(false);
 }
 size?.addEventListener('change',()=>changePreferences({...preferences,size:size.value}));
 font?.addEventListener('change',()=>changePreferences({...preferences,font:font.value}));
 theme?.addEventListener('change',()=>changePreferences({...preferences,theme:theme.value}));
 focus?.addEventListener('change',()=>changePreferences({...preferences,focus:focus.checked}));
 applyPreferences();

 function renderSavedState() {
  document.querySelectorAll<HTMLElement>('[data-book-progress]').forEach(element=>{
   if(manifest.length)element.textContent=state.completedSlugs.length+' de '+manifest.length+' capítulos completados';
  });
  let bookmark=state.bookmark;
  const savedIndex=bookmark?manifest.findIndex(item=>item.slug===bookmark!.slug):-1;
  if(bookmark&&state.completedSlugs.includes(bookmark.slug)){
   const nextUnread=manifest.slice(savedIndex+1).find(item=>!state.completedSlugs.includes(item.slug));
   if(nextUnread)bookmark={slug:nextUnread.slug,headingId:'',ratio:1,updatedAt:bookmark.updatedAt};
  }
  const savedChapter=bookmark?manifest.find(item=>item.slug===bookmark.slug):null;
  const href=buildResumeHref(bookmark,manifest);
  document.querySelectorAll<HTMLElement>('[data-book-chapter]').forEach(link=>{
   const slug=link.dataset.bookChapter||'';if(state.bookmark?.slug===slug)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');
   const marker=link.querySelector<HTMLElement>('[data-book-completion]');if(marker)marker.hidden=!state.completedSlugs.includes(slug);
  });
  const canResume=!!savedChapter&&!!href&&!!bookmark&&bookmark.ratio>0.02;
  document.querySelectorAll<HTMLElement>('[data-resume-card]').forEach(card=>{
   card.hidden=!canResume;
   const link=card.querySelector<HTMLAnchorElement>('[data-resume-link]');
   const title=card.querySelector<HTMLElement>('[data-resume-title]');
   if(canResume&&savedChapter&&href){if(link)link.href=href;if(title)title.textContent=savedChapter.number+'. '+savedChapter.title;}
  });
  const completed=!!chapter&&state.completedSlugs.includes(chapter.slug);
  finishButtons.forEach(button=>{
   button.disabled=completed;
   button.textContent=completed?'Capítulo completado':button.dataset.readerOriginalLabel||'Marcar capítulo como leído';
  });
 }
 renderSavedState();

 function persistProgress() {
  if(persistTimer!==undefined){clearTimeout(persistTimer);persistTimer=undefined;}
  if(!dirty)return;
  // Preserve explicit completions made in another open tab, never infer them from scroll.
  const elsewhere=parseProgress(safeRead(READER_PROGRESS_KEY),manifest) as ReadingState;
  state=normalizeProgress({bookmark:latestBookmark||state.bookmark,completedSlugs:mergeCompleted(manifest,state.completedSlugs,elsewhere.completedSlugs)},manifest) as ReadingState;
  safeWrite(READER_PROGRESS_KEY,state);dirty=false;renderSavedState();
 }
 function requestPersist(){dirty=true;if(persistTimer!==undefined)clearTimeout(persistTimer);persistTimer=window.setTimeout(persistProgress,900);}
 function updateReader(save:boolean) {
  if(!body||!chapter)return;
  const rect=body.getBoundingClientRect();
  const start=rect.top+scrollY;
  const source=body.querySelector<HTMLElement>('details.chapter-sources');
  const sourceTop=source?source.getBoundingClientRect().top+scrollY:null;
  const end=sourceTop!==null&&sourceTop>=start&&sourceTop<=rect.bottom+scrollY?sourceTop:rect.bottom+scrollY;
  const ratio=calculateChapterProgress(scrollY,innerHeight,start,end);
  const threshold=Math.min(innerHeight*.25,160);
  activeHeading=headings[0]||null;
  for(const heading of headings){if(heading.getBoundingClientRect().top<=threshold)activeHeading=heading;else break;}
  const percent=Math.round(ratio*100);
  document.querySelectorAll<HTMLElement>('[data-chapter-progress]').forEach(element=>{element.textContent=percent+' %';element.setAttribute('aria-label',percent+' % del capítulo');});
  document.querySelectorAll<HTMLElement>('[data-chapter-progress-bar]').forEach(element=>{element.style.width=percent+'%';});
  sectionLinks.forEach(link=>{
   let id='';try{id=decodeURIComponent((link.getAttribute('href')||'').slice(1));}catch{/* Ignore invalid hashes. */}
   if(activeHeading&&id===activeHeading.id)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');
  });
  if(save&&scrollY+innerHeight>start+40){latestBookmark={slug:chapter.slug,headingId:sanitizeHeadingId(activeHeading?.id||''),ratio,updatedAt:Date.now()};requestPersist();}
 }
 function scheduleUpdate(save:boolean) {
  pendingSave=pendingSave||save;
  if(frame)return;
  frame=requestAnimationFrame(()=>{frame=0;const saveNow=pendingSave;pendingSave=false;updateReader(saveNow);});
 }
 window.addEventListener('scroll',()=>scheduleUpdate(true),{passive:true});
 window.addEventListener('resize',()=>scheduleUpdate(false),{passive:true});
 function flushProgress(){if(frame&&pendingSave){cancelAnimationFrame(frame);frame=0;pendingSave=false;updateReader(true);}persistProgress();}
 window.addEventListener('pagehide',flushProgress);
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')flushProgress();});
 document.querySelectorAll<HTMLAnchorElement>('[data-book-next]').forEach(link=>link.addEventListener('click',flushProgress));
 updateReader(false);
 if(document.fonts)void document.fonts.ready.then(()=>scheduleUpdate(false));

 function revealLinkedSource(){
  if(!hasExplicitHash(location.hash))return;
  if(inline)inline.hidden=true;
  let id='';try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
  const target=document.getElementById(id);
  const source=target?.matches('details.chapter-sources')?target:target?.closest('details.chapter-sources');
  if(source instanceof HTMLDetailsElement){source.open=true;if(target)requestAnimationFrame(()=>{target.scrollIntoView({block:'start',behavior:'instant'});scheduleUpdate(false);});}
 }
 if(inline)inline.hidden=!shouldOfferResume(initialBookmark,chapter?.slug||'',location.hash);
 revealLinkedSource();window.addEventListener('hashchange',revealLinkedSource);
 document.querySelector<HTMLButtonElement>('[data-resume-here]')?.addEventListener('click',event=>{
  event.preventDefault();
  if(!body||!chapter||!initialBookmark||initialBookmark.slug!==chapter.slug||hasExplicitHash(location.hash)){if(inline)inline.hidden=true;return;}
  const candidate=initialBookmark.headingId?document.getElementById(initialBookmark.headingId):null;
  const target=candidate&&body.contains(candidate)&&!candidate.closest('details.chapter-sources')?candidate:body;
  if(!target.hasAttribute('tabindex'))target.setAttribute('tabindex','-1');
  target.focus({preventScroll:true});
  target.scrollIntoView({block:'start',behavior:typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  if(inline)inline.hidden=true;
 });
 finishButtons.forEach(button=>button.addEventListener('click',event=>{
  event.preventDefault();if(!chapter)return;
  latestBookmark={slug:chapter.slug,headingId:sanitizeHeadingId(activeHeading?.id||headings[headings.length-1]?.id||''),ratio:1,updatedAt:Date.now()};
  state={bookmark:latestBookmark,completedSlugs:mergeCompleted(manifest,state.completedSlugs,[chapter.slug])};
  dirty=true;persistProgress();renderSavedState();
 }));
 document.querySelectorAll<HTMLButtonElement>('[data-reset-reading]').forEach(button=>button.addEventListener('click',event=>{
  event.preventDefault();if(persistTimer!==undefined)clearTimeout(persistTimer);persistTimer=undefined;dirty=false;latestBookmark=null;
  state={bookmark:null,completedSlugs:[]};safeRemove(READER_PROGRESS_KEY);if(inline)inline.hidden=true;renderSavedState();
 }));
 window.addEventListener('storage',event=>{
  if(event.key===READER_PREFERENCES_KEY||event.key===null){preferences=parsePreferences(safeRead(READER_PREFERENCES_KEY)) as Preferences;applyPreferences();scheduleUpdate(false);}
  if(event.key===READER_PROGRESS_KEY||event.key===null){state=parseProgress(safeRead(READER_PROGRESS_KEY),manifest) as ReadingState;if(!state.bookmark){latestBookmark=null;dirty=false;if(persistTimer!==undefined)clearTimeout(persistTimer);persistTimer=undefined;if(inline)inline.hidden=true;}renderSavedState();}
 });

 const dialog=document.querySelector<HTMLDialogElement>('#book-dialog');
 let opener:HTMLElement|null=null;
 document.querySelectorAll<HTMLAnchorElement>('[data-open-book]').forEach(link=>link.addEventListener('click',event=>{
  if(!dialog||typeof dialog.showModal!=='function'||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  try{opener=link;if(!dialog.open)dialog.showModal();event.preventDefault();}catch{/* Keep the real index href as the fallback. */}
 }));
 document.querySelectorAll<HTMLButtonElement>('[data-close-book]').forEach(button=>button.addEventListener('click',()=>dialog?.close()));
 dialog?.addEventListener('close',()=>{if(opener?.isConnected)opener.focus({preventScroll:true});});
 dialog?.querySelectorAll<HTMLAnchorElement>('a[href]').forEach(link=>link.addEventListener('click',event=>{if(!event.defaultPrevented&&event.button===0&&!event.metaKey&&!event.ctrlKey&&!event.shiftKey&&!event.altKey)dialog.close();}));
 document.querySelectorAll<HTMLButtonElement>('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(location.href);button.textContent='Enlace copiado';}catch{button.textContent='Copia la URL del navegador';}
 }));
 let printSources:Map<HTMLDetailsElement,boolean>|null=null;
 function openPrintSources(){
  if(!printSources)printSources=new Map(Array.from(document.querySelectorAll<HTMLDetailsElement>('details.chapter-sources')).map(source=>[source,source.open]));
  printSources.forEach((_open,source)=>{source.open=true;});
 }
 function restorePrintSources(){printSources?.forEach((wasOpen,source)=>{source.open=wasOpen;});printSources=null;}
 window.addEventListener('beforeprint',openPrintSources);window.addEventListener('afterprint',restorePrintSources);
 document.querySelectorAll<HTMLButtonElement>('[data-print-reading]').forEach(button=>button.addEventListener('click',()=>{openPrintSources();try{window.print();}catch{restorePrintSources();}}));
 html.dataset.readerReady='true';
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',startReader,{once:true});else startReader();
