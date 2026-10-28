import assert from 'node:assert/strict';
import test from 'node:test';
import {
 READER_PREFERENCES_KEY, READER_PROGRESS_KEY, DEFAULT_PREFERENCES,
 normalizePreferences, parsePreferences, normalizeManifest, normalizeProgress, parseProgress,
 sanitizeHeadingId, mergeCompleted, hasExplicitHash, shouldOfferResume, buildResumeHref,
 calculateChapterProgress, readStorageValue, writeStorageValue, removeStorageValue,
} from '../src/lib/reader-state.mjs';

const chapters=normalizeManifest([
 {slug:'vida-propia',title:'Una vida propia',number:1,url:'/LibreCriterio/articulos/vida-propia/',partId:'01'},
 {slug:'un-acuerdo',title:'Un acuerdo',number:2,url:'/LibreCriterio/articulos/un-acuerdo/?lectura=libro',partId:'01'},
 {slug:'muchas-salidas',title:'Muchas salidas',number:3,url:'/LibreCriterio/articulos/muchas-salidas/',partId:'02'},
]);
const bookmark={slug:'vida-propia',headingId:'el-no-también-es-una-opción',ratio:.4,updatedAt:1770000000000};

test('corrupt or unavailable preferences leave a usable reader',()=>{
 for(const value of [null,undefined,'{','null','[]','"dark"','x'.repeat(70000)])assert.deepEqual(parsePreferences(value),DEFAULT_PREFERENCES);
 assert.deepEqual(normalizePreferences({size:'999px;background:url(https://example.test)',theme:'other',font:'remote-font',focus:'true'}),DEFAULT_PREFERENCES);
 assert.deepEqual(parsePreferences('{"size":24,"font":"sans","theme":"dark","focus":true}'),{size:'24',font:'sans',theme:'dark',focus:true});
});

test('only the trusted book manifest can supply resume destinations',()=>{
 const manifest=normalizeManifest([
  ...chapters,
  {slug:'vida-propia',title:'Duplicate',number:4,url:'/elsewhere',partId:'01'},
  {slug:'external',title:'Bad',number:4,url:'//evil.example/book',partId:'01'},
  {slug:'javascript',title:'Bad',number:4,url:'javascript:alert(1)',partId:'01'},
  {slug:'escaped',title:'Bad',number:4,url:'/\\evil.example/book',partId:'01'},
  {slug:'white-space',title:'Bad',number:4,url:'/book\nevil',partId:'01'},
  {slug:'bad/slug',title:'Bad',number:4,url:'/book',partId:'01'},
 ]);
 assert.deepEqual(manifest,chapters);
 assert.deepEqual(normalizeManifest({slug:'vida-propia'}),[]);
 const state=normalizeProgress({bookmark:{...bookmark,url:'https://evil.example/'},completedSlugs:[]},chapters);
 assert.equal(buildResumeHref(state.bookmark,chapters),'/LibreCriterio/articulos/vida-propia/#el-no-tambi%C3%A9n-es-una-opci%C3%B3n');
 assert.equal(buildResumeHref({...bookmark,slug:'deleted-chapter'},chapters),null);
});

test('unknown chapters and duplicate completions never inflate progress',()=>{
 const state=normalizeProgress({bookmark:{...bookmark,slug:'deleted-chapter'},completedSlugs:['un-acuerdo','un-acuerdo','deleted-chapter','vida-propia',null,42]},chapters);
 assert.equal(state.bookmark,null);
 assert.deepEqual(state.completedSlugs,['vida-propia','un-acuerdo']);
 assert.deepEqual(mergeCompleted(chapters,['un-acuerdo'],['muchas-salidas','un-acuerdo'],['unknown']),['un-acuerdo','muchas-salidas']);
});

test('bookmark positions are finite, bounded and independent of completions',()=>{
 for(const [input,output] of [[-3,0],[3,1],[.25,.25],[NaN,0],[Infinity,0],['.5',0]]){
  const state=normalizeProgress({bookmark:{...bookmark,ratio:input},completedSlugs:[]},chapters);
  assert.equal(state.bookmark.ratio,output);
  assert.deepEqual(state.completedSlugs,[],'Reaching an endpoint is not an explicit completion');
 }
 const state=normalizeProgress({bookmark:{...bookmark,updatedAt:'yesterday'}},chapters);
 assert.equal(state.bookmark.updatedAt,0);
 assert.deepEqual(parseProgress('{broken',chapters),{bookmark:null,completedSlugs:[]});
});

test('section identifiers preserve Spanish headings without accepting markup or navigation',()=>{
 assert.equal(sanitizeHeadingId('qué-significa-vivir'), 'qué-significa-vivir');
 assert.equal(sanitizeHeadingId('qué-significa-vivir'),'qué-significa-vivir');
 for(const value of ['#section','../chapter','section?query','section with space','"><script>','section%23bad','section\nother','x'.repeat(181),null])assert.equal(sanitizeHeadingId(value),'');
 const state=normalizeProgress({bookmark:{...bookmark,headingId:'"><script>'}},chapters);
 assert.equal(buildResumeHref(state.bookmark,chapters),'/LibreCriterio/articulos/vida-propia/');
});

test('an explicit link target always wins over the saved reading place',()=>{
 assert.equal(hasExplicitHash('#section'),true);
 assert.equal(hasExplicitHash('#'),false);
 assert.equal(shouldOfferResume(bookmark,'vida-propia',''),true);
 assert.equal(shouldOfferResume(bookmark,'vida-propia','#another-section'),false);
 assert.equal(shouldOfferResume(bookmark,'un-acuerdo',''),false);
 assert.equal(shouldOfferResume({...bookmark,ratio:0},'vida-propia',''),false);
 assert.equal(shouldOfferResume(null,'vida-propia',''),false);
 assert.equal(buildResumeHref({...bookmark,slug:'un-acuerdo'},chapters),'/LibreCriterio/articulos/un-acuerdo/?lectura=libro#el-no-tambi%C3%A9n-es-una-opci%C3%B3n');
});

test('chapter progress excludes any later sources, next chapter or footer',()=>{
 // Main argument: y=100..2100; sources and footer may extend the page to y=9000.
 assert.equal(calculateChapterProgress(0,500,100,2100),0);
 assert.equal(calculateChapterProgress(100,500,100,2100),0);
 assert.equal(calculateChapterProgress(850,500,100,2100),.5);
 assert.equal(calculateChapterProgress(1600,500,100,2100),1);
 assert.equal(calculateChapterProgress(850,500,100,9000)<.1,true,'Using document height would hide real chapter progress');
 assert.equal(calculateChapterProgress(9000,500,100,2100),1);
 for(const args of [[0,0,0,100],[0,500,100,100],[NaN,500,0,100]])assert.equal(calculateChapterProgress(...args),0);
 assert.equal(calculateChapterProgress(300,600,600,900),1,'A short argument can fit wholly in the viewport');
});

test('blocked storage does not prevent reading or applying in-memory state',()=>{
 const blocked=()=>{throw new Error('Storage disabled');};
 assert.equal(readStorageValue(blocked,READER_PREFERENCES_KEY),null);
 assert.equal(writeStorageValue(blocked,READER_PROGRESS_KEY,{bookmark}),false);
 assert.equal(removeStorageValue(blocked,READER_PROGRESS_KEY),false);
 const quota=()=>({getItem:()=>null,setItem:()=>{throw new Error('Quota exceeded');},removeItem:()=>{throw new Error('Blocked');}});
 assert.equal(writeStorageValue(quota,READER_PROGRESS_KEY,{bookmark}),false);
 assert.equal(removeStorageValue(quota,READER_PROGRESS_KEY),false);
});

test('reset removes only this book progress and leaves preferences and unrelated storage alone',()=>{
 const values=new Map([[READER_PROGRESS_KEY,'old progress'],[READER_PREFERENCES_KEY,'my preferences'],['another-app','private data']]);
 const getStorage=()=>({getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value),removeItem:key=>values.delete(key)});
 assert.equal(removeStorageValue(getStorage,READER_PROGRESS_KEY),true);
 assert.equal(values.has(READER_PROGRESS_KEY),false);
 assert.equal(values.get(READER_PREFERENCES_KEY),'my preferences');
 assert.equal(values.get('another-app'),'private data');
 assert.equal(writeStorageValue(getStorage,READER_PROGRESS_KEY,{bookmark,completedSlugs:['vida-propia']}),true);
 assert.deepEqual(parseProgress(readStorageValue(getStorage,READER_PROGRESS_KEY),chapters),{bookmark,completedSlugs:['vida-propia']});
});
