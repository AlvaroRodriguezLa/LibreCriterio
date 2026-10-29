import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {buildBook,getBookChapter,readingWords,estimateReadingTime} from '../src/lib/reading-book.mjs';
const parts=JSON.parse(await readFile('src/data/routes.json','utf8'));
const bridges=JSON.parse(await readFile('src/data/chapter-bridges.json','utf8'));
const chapters=buildBook(parts);
assert.equal(parts.length,5);assert.ok(chapters.length>=29);
assert.equal(new Set(chapters.map(c=>c.slug)).size,chapters.length);
assert.deepEqual(new Set(chapters.map(c=>c.slug+'.md')),new Set((await readdir('src/content/articles')).filter(f=>f.endsWith('.md'))),'Cada ensayo aparece exactamente una vez');
for(const [index,chapter] of chapters.entries()){
 assert.equal(chapter.number,index+1);assert.equal(chapter.total,chapters.length);
 assert.equal(chapter.previous,chapters[index-1]?.slug||null);assert.equal(chapter.next,chapters[index+1]?.slug||null);
 assert.equal(getBookChapter(parts,chapter.slug).number,index+1);
 assert.ok(bridges[chapter.slug]?.length>40,'Falta transición hacia el siguiente capítulo');
 if(chapter.next)assert.equal(getBookChapter(parts,chapter.next).previous,chapter.slug);
}
assert.equal(getBookChapter(parts,'no-existe'),null);
for(let i=0;i<parts.length-1;i++){assert.equal(getBookChapter(parts,parts[i].slugs.at(-1)).next,parts[i+1].slugs[0],'Continuidad entre partes');}
const fence=String.fromCharCode(96).repeat(3);
const prose='Un argumento en cinco palabras.';
assert.equal(readingWords(prose),5);
assert.equal(readingWords(prose+'\n'+fence+'oneshot\n'+JSON.stringify({many:'values with words'})+'\n'+fence+'\n## Lecturas y fuentes\nMuchísimas notas que no son parte del tiempo de lectura.'),5);
assert.equal(estimateReadingTime('palabra '.repeat(401)),3);
console.log('Libro: Capítulos únicos, cinco partes, continuidad global y tiempo sin notas ni JSON comprobados');
