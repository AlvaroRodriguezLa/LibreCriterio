import {readFile,readdir,stat} from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';
const root=path.resolve('dist');const base=process.env.BASE_PATH||'';const files=[];
async function walk(dir){for(const entry of await readdir(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())await walk(file);else if(file.endsWith('.html'))files.push(file);}}
await walk(root);assert.ok(files.length>=27,'El build está vacío o incompleto');let checked=0;
for(const file of files){const html=await readFile(file,'utf8');for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){let url=match[1].split('#')[0].split('?')[0];if(!url||/^(https?:|data:|mailto:|tel:)/.test(url))continue;if(base&&(url===base||url.startsWith(base+'/')))url=url.slice(base.length)||'/';if(url.startsWith('/api/')){await stat(path.resolve('api',url.slice(5)+'.mjs'));continue;}let target=url.startsWith('/')?path.join(root,url):path.resolve(path.dirname(file),url);if(target.endsWith(path.sep)||url.endsWith('/'))target=path.join(target,'index.html');try{await stat(target);}catch{throw new Error(path.relative(root,file)+' → enlace o recurso inexistente: '+url);}checked++;}assert.doesNotMatch(html,/language-oneshot/,'Bloque sin renderizar en '+file);}
console.log(files.length+' páginas HTML; '+checked+' enlaces y recursos locales comprobados');

const robots=await readFile(path.join(root,'robots.txt'),'utf8');assert.ok(robots.includes(base+'/sitemap-index.xml'),'Sitemap con prefijo inválido en robots');

const parts=JSON.parse(await readFile('src/data/routes.json','utf8'));
const {buildBook}=await import('../src/lib/reading-book.mjs');const chapters=buildBook(parts);
const bookIndex=await readFile(path.join(root,'rutas/index.html'),'utf8');
for(const part of parts)assert.ok(bookIndex.includes('id="ruta-'+part.id+'"'),'Parte sin ancla');
for(const chapter of chapters){
 const html=await readFile(path.join(root,'articulos',chapter.slug,'index.html'),'utf8');
 assert.ok(bookIndex.includes('id="capitulo-'+chapter.slug+'"'),'Capítulo fuera del índice');
 assert.ok(html.includes('data-reader-number="'+chapter.number+'"'),'Posición de lectura ausente');
 assert.ok(html.includes('aria-label="Continuar el libro"'),'Continuación ausente');
 for(const neighbor of [chapter.previous,chapter.next].filter(Boolean))assert.ok(html.includes('href="'+base+'/articulos/'+neighbor+'/"'),'Continuidad perdida: '+chapter.slug+' → '+neighbor);
 assert.ok(html.includes('class="chapter-sources"'),'Referencias sin desplegable: '+chapter.slug);
 assert.ok(html.includes('id="book-manifest"'),'Índice del lector ausente');
 if(!chapter.next)assert.ok(html.includes('Has terminado el recorrido.'),'Final del libro ausente');
 assert.doesNotMatch(html,/documento maestro|pptLIB/i,'Procedencia de trabajo expuesta');
}
console.log('Libro publicado: '+chapters.length+' capítulos con avance global, retroceso, fuentes plegables e índice');

const dossier=JSON.parse(await readFile('src/data/political-cases.json','utf8'));
const dossierHtml=await readFile(path.join(root,'expedientes/index.html'),'utf8');
const dossierIds=[...dossierHtml.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(dossierIds).size,dossierIds.length,'Anclas duplicadas en expediente');
for(const entry of dossier.cases)assert.ok(dossierIds.includes('caso-'+entry.id),'Ficha no publicada: '+entry.id);
assert.ok(dossierIds.includes('ceuta'),'Cronología sin ancla');
assert.doesNotMatch(dossierHtml,/agente principal|acceso web inicial/i,'Nota de trabajo expuesta');
console.log('Expediente publicado: '+dossier.cases.length+' fichas y anclas únicas verificadas');
