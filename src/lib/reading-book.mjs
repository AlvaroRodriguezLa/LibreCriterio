/** @typedef {{id:string,title:string,lead:string,opening?:string,slugs:string[]}} BookPart */
/** @param {BookPart[]} parts */
export function buildBook(parts) {
 const chapters=parts.flatMap((part,partIndex)=>part.slugs.map((slug,index)=>({slug,partId:part.id,partNumber:partIndex+1,partTitle:part.title,partLead:part.lead,partOpening:part.opening||'',partStep:index+1,partTotal:part.slugs.length})));
 return chapters.map((chapter,index)=>({...chapter,number:index+1,total:chapters.length,previous:chapters[index-1]?.slug||null,next:chapters[index+1]?.slug||null}));
}
/** @param {BookPart[]} parts @param {string} slug */
export function getBookChapter(parts,slug){return buildBook(parts).find(chapter=>chapter.slug===slug)||null;}
/** @param {string} markdown */
export function readingWords(markdown){return markdown.split(/^## Lecturas y fuentes/m)[0].replace(/```[\s\S]*?```/g,' ').replace(/<[^>]*>/g,' ').replace(/!?\[([^\]]*)\]\([^)]*\)/g,'$1').replace(/https?:\/\/\S+/g,' ').replace(/[#*_>|]/g,' ').trim().split(/\s+/).filter(Boolean).length;}
/** @param {string} markdown @param {number} wordsPerMinute */
export function estimateReadingTime(markdown,wordsPerMinute=200){return Math.max(1,Math.ceil(readingWords(markdown)/wordsPerMinute));}
