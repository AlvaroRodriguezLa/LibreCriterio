import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {getReadingSteps,selectReadingRoute} from '../src/lib/reading-routes.mjs';
const routes=JSON.parse(await readFile('src/data/routes.json','utf8'));
const ids=new Set();
for(const route of routes){
 assert.ok(!ids.has(route.id),'Identificador de ruta duplicado');ids.add(route.id);
 assert.equal(new Set(route.slugs).size,route.slugs.length,'Paso duplicado');
 for(const [index,slug] of route.slugs.entries()){
  const current=selectReadingRoute(getReadingSteps(routes,slug),route.id);
  assert.equal(current.step,index+1);assert.equal(current.total,route.slugs.length);
  assert.equal(current.previous,route.slugs[index-1]||null);
  assert.equal(current.next,route.slugs[index+1]||null);
  if(current.next){const next=selectReadingRoute(getReadingSteps(routes,current.next),route.id);assert.equal(next.previous,slug,'La ruta debe poder recorrerse en ambas direcciones');}
 }
}
const first=getReadingSteps(routes,routes[0].slugs[0]);
assert.equal(first[0].next,'un-contrato-que-nadie-puede-rechazar');
assert.equal(selectReadingRoute(first,'ruta-inexistente'),first[0]);
assert.equal(selectReadingRoute([],null),null);
const shared=[{id:'01',title:'Una',slugs:['inicio','compartido','fin']},{id:'02',title:'Otra',slugs:['compartido','otro-final']}];
assert.equal(selectReadingRoute(getReadingSteps(shared,'compartido'),'02').next,'otro-final','Una entrada compartida debe conservar el recorrido elegido');
console.log('Rutas: avance, retroceso, final y contexto válido e inválido comprobados');
