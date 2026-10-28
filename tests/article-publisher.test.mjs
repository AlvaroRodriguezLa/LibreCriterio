import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,rm} from 'node:fs/promises';
import os from 'node:os';import path from 'node:path';
import {saveLocalArticle,loadLocalDraft,listLocalDrafts,parseLocalArticle} from '../studio/article-store.mjs';
import {demoArticle} from '../src/lib/article-blocks/demo.mjs';
const root=await mkdtemp(path.join(os.tmpdir(),'libre-publisher-'));
try{
 await mkdir(path.join(root,'src/content/articles'),{recursive:true});
 const form=new FormData();for(const [k,v] of Object.entries({title:demoArticle.title,text:demoArticle.text,existingImage:'/images/editorial-placeholder.svg',category:'Fundamentos',date:'2026-10-28',action:'draft'}))form.set(k,v);
 const draft=await saveLocalArticle(form,{root});assert.equal(draft.ok,true,JSON.stringify(draft));
 const loaded=await loadLocalDraft(root,draft.slug);assert.equal(loaded.text,demoArticle.text.trim());assert.equal(loaded.draft,true);
 assert.deepEqual((await listLocalDrafts(root)).map(x=>x.slug),[draft.slug]);
 const calls=[];form.set('slug',draft.slug);form.set('action','publish');
 const published=await saveLocalArticle(form,{root,shouldPublish:true,runGit:async args=>{calls.push(args);return {stdout:'',stderr:''}},getGitConfig:async key=>({'user.name':'Test','user.email':'test@example.invalid','remote.origin.url':'mock://local-only'}[key]||'')});
 assert.equal(published.pushed,true,JSON.stringify(published));assert.ok(calls.some(c=>c[0]==='push'));assert.deepEqual(calls.find(c=>c[0]==='add').slice(2),[path.join('src','content','articles',draft.slug+'.md')]);
 const saved=parseLocalArticle(await readFile(path.join(root,'src/content/articles',draft.slug+'.md'),'utf8'));assert.equal(saved.draft,false);assert.equal(saved.text,demoArticle.text.trim());
 await assert.rejects(loadLocalDraft(root,draft.slug),/Solo se pueden reabrir borradores/);assert.equal((await saveLocalArticle(form,{root})).status,409);
 form.set('slug','../../escape');const invalid=await saveLocalArticle(form,{root});assert.equal(invalid.ok,false);
 form.set('slug','otro');form.set('text','```oneshot\n{"type":"no-existe"}\n```');await assert.rejects(saveLocalArticle(form,{root}),/Tipo de bloque desconocido/);
 console.log('Publicador: guardar, reabrir, publicar con Git simulado y rechazar rutas inválidas');
}finally{await rm(root,{recursive:true,force:true});}
