import {readFile,readdir,stat} from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';
const root=path.resolve('dist');const base=process.env.BASE_PATH||'';const files=[];
async function walk(dir){for(const entry of await readdir(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())await walk(file);else if(file.endsWith('.html'))files.push(file);}}
await walk(root);assert.ok(files.length>=27,'El build está vacío o incompleto');let checked=0;
for(const file of files){const html=await readFile(file,'utf8');for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){let url=match[1].split('#')[0].split('?')[0];if(!url||/^(https?:|data:|mailto:|tel:)/.test(url))continue;if(base&&(url===base||url.startsWith(base+'/')))url=url.slice(base.length)||'/';if(url.startsWith('/api/')){await stat(path.resolve('api',url.slice(5)+'.mjs'));continue;}let target=url.startsWith('/')?path.join(root,url):path.resolve(path.dirname(file),url);if(target.endsWith(path.sep)||url.endsWith('/'))target=path.join(target,'index.html');try{await stat(target);}catch{throw new Error(path.relative(root,file)+' → enlace o recurso inexistente: '+url);}checked++;}assert.doesNotMatch(html,/language-oneshot/,'Bloque sin renderizar en '+file);}
console.log(files.length+' páginas HTML; '+checked+' enlaces y recursos locales comprobados');

const robots=await readFile(path.join(root,'robots.txt'),'utf8');assert.ok(robots.includes(base+'/sitemap-index.xml'),'Sitemap con prefijo inválido en robots');

const routes=JSON.parse(await readFile('src/data/routes.json','utf8'));
const routeIndex=await readFile(path.join(root,'rutas/index.html'),'utf8');
for(const route of routes){
 assert.ok(routeIndex.includes('id="ruta-'+route.id+'"'),'Ancla de ruta ausente');
 for(const [index,slug] of route.slugs.entries()){
  const html=await readFile(path.join(root,'articulos',slug,'index.html'),'utf8');
  assert.ok(html.includes('data-reading-route="'+route.id+'"'),'Navegación ausente en '+slug);
  for(const neighbor of [route.slugs[index-1],route.slugs[index+1]].filter(Boolean)){
   const href=base+'/articulos/'+neighbor+'/?ruta='+route.id;
   assert.ok(html.includes('href="'+href+'"'),'Continuidad de ruta perdida: '+slug+' → '+neighbor);
  }
  if(index===route.slugs.length-1)assert.ok(html.includes('Has completado esta ruta.'),'Final de ruta ausente');
  assert.doesNotMatch(html,/documento maestro|pptLIB/i,'Procedencia de trabajo expuesta');
 }
}
console.log('Rutas publicadas: '+routes.reduce((n,r)=>n+r.slugs.length,0)+' pasos mantienen avance, retroceso y prefijo de GitHub Pages');

const dossier=JSON.parse(await readFile('src/data/political-cases.json','utf8'));
const dossierHtml=await readFile(path.join(root,'expedientes/index.html'),'utf8');
const dossierIds=[...dossierHtml.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(dossierIds).size,dossierIds.length,'Anclas duplicadas en expediente');
for(const entry of dossier.cases)assert.ok(dossierIds.includes('caso-'+entry.id),'Ficha no publicada: '+entry.id);
assert.ok(dossierIds.includes('ceuta'),'Cronología sin ancla');
assert.doesNotMatch(dossierHtml,/agente principal|acceso web inicial/i,'Nota de trabajo expuesta');
console.log('Expediente publicado: '+dossier.cases.length+' fichas y anclas únicas verificadas');
