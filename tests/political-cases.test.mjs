import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
const data=JSON.parse(await readFile('src/data/political-cases.json','utf8'));
assert.doesNotMatch(JSON.stringify(data),/agente principal|acceso web inicial|no presentarla como|no editar la frase|Debe conservarse el contexto/i,'Notas de trabajo expuestas');
const ids=new Set();
for(const c of data.cases){assert.ok(!ids.has(c.id),'Identificador de caso duplicado');ids.add(c.id);assert.ok(c.fact&&c.status&&c.scope,'Ficha incompleta');assert.ok(c.date<=data.checked,'Fecha posterior a revisión');assert.ok(c.sources.length>=1,'Caso sin fuente');for(const source of c.sources){assert.equal(new URL(source.url).protocol,'https:');assert.ok(source.title);}}
for(const p of data.promises){assert.ok(p.beforeDate<p.afterDate,'Contraste fuera de orden');assert.ok(p.sources.length>=2,'Falta contraste de ambas posiciones');assert.ok(p.context);}
assert.ok(data.ceuta.length>=1);for(const item of data.ceuta){assert.equal(new URL(item.source).protocol,'https:');assert.ok(item.date<=data.checked);}
for(const id of ['abalos-koldo','begona-gomez','david-sanchez','santos-cerdan','leire-diez','biedma','garcia-ortiz','delcy','plus-ultra','dana','toledo','ceuta','air-europa','adamuz','covid'])assert.ok(ids.has(id),'Petición sin ficha: '+id);
console.log('Expediente: '+data.cases.length+' casos con fuentes, estados y alcance; '+data.promises.length+' contrastes documentados');
