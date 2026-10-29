import assert from 'node:assert/strict';import {readFile,readdir,stat} from 'node:fs/promises';import {parse} from 'yaml';import {validateArticleBlocks} from '../public/article-blocks.mjs';
const files=(await readdir('src/content/articles')).filter(f=>f.endsWith('.md'));assert.ok(files.length>=17);
const slugs=new Set();const entries=[];
for(const file of files){
 const source=await readFile('src/content/articles/'+file,'utf8');const m=source.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);assert.ok(m,file);
 const data=parse(m[1]);assert.ok(!slugs.has(data.slug),'Slug duplicado');slugs.add(data.slug);if(data.draft)continue;entries.push({data,body:m[2]});
 assert.equal(data.draft,false);if(data.masterPages)assert.ok(m[2].includes('## Lecturas y fuentes'),file+' sin bibliografía');
 if(data.masterPages)assert.ok(m[2].split(/\s+/).length>500,file+' demasiado breve');await stat('public'+data.image);
 for(const {block} of validateArticleBlocks(m[2])){if(block.type==='stat-cards')for(const s of block.stats)assert.ok(s.source,file+' cifra sin fuente');}
}
for(const {data,body} of entries){for(const slug of data.related||[])assert.ok(slugs.has(slug),'Relacionado inexistente '+slug);assert.doesNotMatch(body,/turn\d+(search|view)|utm_source=chatgpt|TODO|lorem ipsum/);}
const routes=JSON.parse(await readFile('src/data/routes.json','utf8'));for(const route of routes)for(const slug of route.slugs)assert.ok(slugs.has(slug),'Ruta inexistente '+slug);
assert.ok(entries.some(e=>e.data.featured));
assert.ok(Math.abs(58.6/1.21-48.429752)<.00001);assert.ok(Math.abs(100/1.03**10-74.409391)<.00001);
for(const {body} of entries){assert.doesNotMatch(body,/documento maestro|pptLIB|el maestro|texto satélite/i,'Referencia de trabajo expuesta');assert.ok(body.includes('## Lecturas y fuentes'),'Ensayo sin fuentes');assert.ok(body.split(/\s+/).length>500,'Ensayo demasiado breve');}
console.log('Contenido: '+entries.length+' ensayos, fuentes, portadas, rutas y relaciones coherentes');

// Las fuentes audiovisuales se mantienen en bibliografía, no como referencia al proceso de transcripción dentro del ensayo.
const requestedVideos=JSON.parse(await readFile('tools/youtube-sources.json','utf8')).videos;
for(const video of requestedVideos){assert.ok(entries.some(({body})=>(body.split('## Lecturas y fuentes')[1]||'').includes('watch?v='+video.id)),'Falta fuente audiovisual '+video.id);}
for(const {body} of entries){const prose=body.split('## Lecturas y fuentes')[0];assert.doesNotMatch(prose,/transcripci[oó]n|en (?:este|el) v[ií]deo|gu[ií]a del documental/i,'Referencia al proceso audiovisual dentro del ensayo');}
console.log('Fuentes audiovisuales: '+requestedVideos.length+' enlaces localizados en bibliografía; prosa sin referencias al proceso de transcripción');
