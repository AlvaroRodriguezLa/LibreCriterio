export const siteConfig = {
 name: 'LIBRE CRITERIO', tagline: 'Ideas para una sociedad de personas libres.',
 description: 'Ensayos sobre libertad, mercados y límites del poder. Una mirada liberal y antiestatista con argumentos, literatura y evidencia.',
 author: 'Álvaro Rodríguez', language: 'es-ES', baseUrl: import.meta.env.PUBLIC_SITE_URL || 'https://alvarorodriguezla.github.io/LibreCriterio/',
};
export const categoryConfig = [
 {slug:'fundamentos',label:'Fundamentos',source:'Fundamentos',description:'La persona, sus derechos y las razones para limitar el poder.'},
 {slug:'mercados',label:'Mercados y conocimiento',source:'Mercados',description:'Precios, descubrimiento, capital y coordinación sin director.'},
 {slug:'poder',label:'Democracia y poder',source:'Poder',description:'Los incentivos de quienes gobiernan y los límites de la mayoría.'},
 {slug:'fiscalidad',label:'Fiscalidad y bienestar',source:'Fiscalidad',description:'El recorrido del dinero: de la nómina al presupuesto y sus beneficiarios.'},
 {slug:'instituciones',label:'Instituciones y alternativas',source:'Instituciones',description:'Competencia, ayuda mutua y reglas para cooperar.'},
 {slug:'debates',label:'Debates abiertos',source:'Debates',description:'Las objeciones que una defensa seria de la libertad debe responder.'},
];
export function categorySlug(category:string) { return categoryConfig.find(c=>c.source===category||c.label===category||c.slug===category)?.slug || 'debates'; }
export function categoryLabel(category:string) { return categoryConfig.find(c=>c.slug===categorySlug(category))?.label || category; }
