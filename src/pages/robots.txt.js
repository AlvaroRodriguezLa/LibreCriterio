export function GET({site}){
 const origin=site?.origin||'https://alvarorodriguezla.github.io';
 const rawBase=import.meta.env.BASE_URL||'/';
 const base=rawBase.endsWith('/')?rawBase:rawBase+'/';
 return new Response('User-agent: *\nAllow: /\nDisallow: '+base+'studio/\nSitemap: '+origin+base+'sitemap-index.xml\n',{headers:{'Content-Type':'text/plain'}});
}
