# Investigación de lectura y edición de Una vida propia

Revisión: 28 de octubre de 2026. Estudio aplicado al proyecto Libre Criterio.

La recomendación central es editar una obra con un hilo argumental y una continuación inequívoca. El archivo por temas, la biblioteca y los casos siguen disponibles como consulta. La investigación combina once referencias de mercado, doce fuentes de escritura, seis criterios W3C y dos fuentes sobre memoria e interfaces. No constituye una revisión sistemática de toda la literatura ni una prueba de que esta edición aumente la persuasión o la permanencia.

## Resultado aplicado

La edición del 28 de octubre reunió 29 capítulos en cinco partes: libertad y propiedad; coordinación y capital; incentivos del poder; coste de la tutela; alternativas voluntarias. Las direcciones existentes se conservan. La secuencia atraviesa las fronteras de las partes y cada final presenta el asunto que viene después.

La lectura usa una columna de hasta 65ch, 20px por defecto, interlineado 1,72 y alineación izquierda. El lector puede escoger 18, 20, 22 o 24px, serif o sans y fondo papel, blanco u oscuro. El modo de concentración recoge el argumento en una columna y mantiene el acceso al índice. La posición se ofrece para retomar por sección mediante una acción explícita; no hay salto automático. Los capítulos completados se marcan mediante un botón, nunca por haber desplazado la página. Preferencias y progreso se guardan solo en el navegador utilizado.

Las fuentes y ampliaciones se despliegan al pie. Los límites que alteran la interpretación de una cifra permanecen junto a ella. El porcentaje mide el argumento principal, no las notas ni el pie de página; el tiempo estimado excluye JSON de diagramas y bibliografía. La navegación y el texto son HTML estático y siguen funcionando sin JavaScript.

La ampliación del 29 de octubre conserva este diseño y extiende el recorrido a 38 capítulos. La cobertura de temas añadidos se documenta en AUDITORIA_AMPLIACION_2026-10-29.md. No se han repetido las comparaciones externas para presentar esa ampliación como un nuevo estudio de mercado.

## Comparación del mercado

La observación se basa en el HTML consultable y la documentación original. No se han probado visualmente todos los lectores ni se han supuesto funciones que no pudimos observar.

| Referencia | Evidencia observada | Decisión para Libre Criterio | Límite de la observación |
| --- | --- | --- | --- |
| [Butterick’s Practical Typography](https://practicaltypography.com/typography-in-ten-minutes.html) | Capítulo con ruta anterior a inicio y siguiente a Summary of key rules; Enlace al índice y a inicio de página; Cuerpo redactado en unidades cortas y enlaces para ampliar términos | Un siguiente inequívoco al final; cuerpo antes que portada; guía tipográfica como oficio, no como ensayo clínico. | Guardado de posición; Preferencias persistentes; Medidas CSS móviles |
| [The Shape of Design](https://shapeofdesignbook.com/chapters/01-how-and-why/) | Capítulos numerados y titulados por concepto; Siguiente capítulo al terminar; Índice completo repetido al pie; Notas finales separadas y opción de descarga | Un índice de obra coherente y una continuación que sigue la narración; las notas tienen su propio lugar. | Reanudación de posición; Tema nocturno; Ajustes de tamaño |
| [Econlib · The Calculus of Consent](https://www.econlib.org/library/Buchanan/buchCv3.html) | Índice de capítulos y apéndices; Selección de capítulo por enlace y query chapter_num; Controles FIRST y LAST; Metadatos bibliográficos y notas enlazadas | Representar orden y contexto de la obra como datos estables; mantener fuentes accesibles. | No se ha visto control próximo/anterior explícito en el HTML extraído; Preferencias de lectura; Guardado de progreso |
| [Online Library of Liberty](https://oll.libertyfund.org/titles/mill-on-liberty-and-the-subjection-of-women-1879-ed) | Read Now separado de Downloads; EPUB, PDF de texto y facsímil diferenciados; Categorías, autores y grupos de lectura en la biblioteca | Distinguir leer ahora de consultar/descargar; no presentar la biblioteca como única puerta de entrada. | El lector se activa mediante botón no disponible en web text extraction; Preferencias del lector; Reanudación automática |
| [Mises Institute · Human Action](https://mises.org/library/book/human-action) | HTML, EPUB, PDF y guía de estudio en la ficha; Opción español y navegación móvil nombrada; Versión HTML enlaza una acción Print | Separar formatos; una guía de estudio puede vivir como satélite sin interrumpir la obra. | La extracción de la versión HTML no expuso el cuerpo o índice; no se verificó continuidad de capítulos; Guardado de progreso; Tipografía del lector |
| [FEE · Housing Reform Can Reduce Hawaii’s Poverty](https://fee.org/articles/housing-reform-can-reduce-hawaiis-poverty/) | Título con una afirmación reconocible y subtítulo corto; Apertura va directamente a una tesis concreta; Fuentes dentro del argumento; Al final aparecen artículos del autor, no una secuencia de libro | Titular por la idea y comenzar con una proposición clara. | Preferencias y guardado; Navegación de obra no observada en este artículo aislado |
| [Gwern.net · Design Of This Website](https://gwern.net/design) | Índice jerárquico explícito; Enlace a bibliografía y notas; Página de diseño explica su propia implementación | Texto principal corto en exposición, fuentes y ampliación disponibles a demanda; progressive enhancement. | No se han accionado los popups en navegador; Medidas CSS y preferencias actuales |
| [Project Gutenberg · On Liberty](https://www.gutenberg.org/cache/epub/34901/pg34901-images.html) | Índice de capítulos con anclas; Obra continua y notas enlazadas; Marcas de páginas de la edición original | La lectura continua no necesita paginación artificial; las anclas permiten volver a un punto. | Reanudación y tema; Medidas CSS móviles |
| [Stripe Press](https://press.stripe.com/) | Biblioteca de títulos con autores, descripciones y formatos; PDFs de algunas obras y acceso a experiencias Living cover; Página individual de Poor Charlie enlazada | Presentar cada parte con identidad editorial y una promesa clara de lectura. | El lector Poor Charlie devolvió HTML sin texto; no se verifican sus funciones; Guardado, preferencias y navegación secuencial |
| [Standard Ebooks](https://standardebooks.org/about/what-makes-standard-ebooks-different) | La búsqueda sirvió la página oficial de principios; la apertura directa falló por XHTML | Tratar la obra como una edición: orden canónico, divisiones semánticas, notas y consistencia. | El lector web concreto no pudo abrirse con web tools; Funciones de reanudación pertenecen también al ereader, no demostradas para la web |
| [Crafting Interpreters](https://craftinginterpreters.com/contents.html) | Búsqueda expuso índice oficial: partes numeradas, capítulos, notas de diseño y apéndices; Notas de diseño figuran como elementos secundarios enlazados | Separar un recorrido principal de notas y apéndices; un único orden reconocible. | La apertura directa de índice/capítulo falló; navegación interior y ajustes no verificados |

## Cómo se revisa la escritura

La voz habla al lector adulto con situaciones reconocibles y acciones concretas. El argumento moral se sostiene por el respeto a la persona y a su consentimiento; una ventaja económica no concede el derecho a imponerle una finalidad. Las predicciones, ejemplos y acusaciones conservan su alcance comprobable.

| Principio de edición | Aplicación | Fundamento |
| --- | --- | --- |
| Un libro con una progresión principal | Cada capítulo resuelve una pregunta y hace necesaria la siguiente. Las partes marcan pasos del argumento; las rutas temáticas quedan como otra manera de consultar. | [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/tips-organizing-your-essay), [John McPhee](https://www.newyorker.com/magazine/2013/01/14/structure) |
| Entrar por una situación y llegar pronto a la tesis | Persona, decisión y consecuencia concreta. Presentar la afirmación central sin introducción de manual. Variar el recurso: escena breve, afirmación directa o pregunta real, no otra parábola por obligación. | [George Orwell](https://www.orwellfoundation.com/the-orwell-foundation/orwell/essays-and-other-works/politics-and-the-english-language/), [William Zinsser](https://theamericanscholar.org/writing-english-as-a-second-language/), [Steven Pinker](https://stevenpinker.com/files/pinker/files/pinker_2014_why_academics_writing_stinks.pdf), [Chip Heath y Dan Heath](https://heathbrothers.com/wp-content/uploads/resources/mts-made-to-stick-model.pdf) |
| Una aportación nueva por párrafo | Esquema inverso y recorte de repeticiones. Conservar todos los argumentos, datos y límites necesarios; reducir el rodeo que los duplica. | [The Writing Center, University of North Carolina at Chapel Hill](https://writingcenter.unc.edu/tips-and-tools/paragraphs/), [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/tips-organizing-your-essay), [George D. Gopen y Judith A. Swan](https://courses.ems.psu.edu/styleforstudents/print/c10_p6.html) |
| Separar mecanismo, dato y límite | Exponer primero el recorrido comprensible. Situar junto a la cifra sus condiciones esenciales; los detalles largos van en notas/fuentes consultables. La tesis moral no se hace depender de que un cálculo resulte favorable. | [Steven Pinker](https://stevenpinker.com/files/pinker/files/pinker_2014_why_academics_writing_stinks.pdf), [George D. Gopen y Judith A. Swan](https://courses.ems.psu.edu/styleforstudents/print/c10_p6.html), [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/counterargument) |
| Objeciones con función y respuesta | Introducir la dificultad allí donde el lector razonable la encontraría. Evitar repetir en cada capítulo que ningún modelo es perfecto. Conservar un capítulo final que recoja los problemas transversales aún abiertos. | [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/counterargument) |
| Puentes concretos y cierres que avanzan | El último párrafo dice qué puede entenderse ahora y qué problema se abre después. Evitar sucesiones de aforismos intercambiables y múltiples cierres del mismo argumento. | [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/transitions), [Harvard College Writing Center](https://writingcenter.fas.harvard.edu/conclusions), [John McPhee](https://www.newyorker.com/magazine/2013/01/14/structure) |
| Comprobar comprensión, no fabricar permanencia | Leer en voz alta y hacer una prueba con lectores reales: qué afirma el capítulo, cómo lo sostiene, qué duda queda y dónde seguirían. No prometer una web perfecta ni usar trucos de urgencia, culpa o scroll infinito. | [Steven Pinker](https://stevenpinker.com/files/pinker/files/pinker_2014_why_academics_writing_stinks.pdf), [Robert F. Lorch y Elizabeth Pugzles Lorch](https://scholars.uky.edu/en/publications/effects-of-headings-on-text-recall-and-summarization/), [William Zinsser](https://theamericanscholar.org/writing-english-as-a-second-language/) |

El esquema inverso asigna a cada párrafo una aportación: situación, afirmación, explicación, evidencia, objeción, respuesta o transición. Si dos párrafos hacen el mismo trabajo, se funden. Esto no obliga a que todos los capítulos repitan una plantilla. El horno aparece donde explica la inversión y el árbitro donde explica el arbitraje; los capítulos posteriores avanzan sobre lo aprendido.

## Bibliografía de escritura y alcance de la evidencia

### George Orwell · Politics and the English Language

[Politics and the English Language](https://www.orwellfoundation.com/the-orwell-foundation/orwell/essays-and-other-works/politics-and-the-english-language/) · 1946. Ensayo original completo.

**Tipo de evidencia:** Consejo de oficio y crítica retórica; no experimento de lectura.

**Aplicación:** Sustituir nominalizaciones por personas que hacen algo; concretar quién decide, cobra o impide. No repetir metáforas distintas para una misma conclusión.

**Límite:** Sus reglas no son leyes universales del español ni una garantía de verdad o persuasión.

### William Zinsser · Writing English as a Second Language

[Writing English as a Second Language](https://theamericanscholar.org/writing-english-as-a-second-language/) · 2009-12-01; charla 2009-08-11. Charla del autor publicada completa.

**Tipo de evidencia:** Consejo de oficio.

**Aplicación:** Leer los párrafos en voz alta. Dividir una oración cuando dos acciones o inferencias compiten. Usar palabras corrientes sin hablar al adulto como a un niño.

**Límite:** Es una charla sobre escribir en inglés; sus preferencias léxicas no se trasladan literalmente al español.

### Steven Pinker · Why Academics Stink at Writing

[Why Academics Stink at Writing](https://stevenpinker.com/files/pinker/files/pinker_2014_why_academics_writing_stinks.pdf) · 2014-09-26. Artículo del autor alojado en su web; extractos y pasajes indexados consultados.

**Tipo de evidencia:** Explicación psicolingüística y consejo de estilo, no prueba específica de esta web.

**Aplicación:** Explicar cada término en su primer uso. Agrupar reservas empíricas con los datos a los que afectan; evitar un descargo después de cada frase. Mostrar decisiones antes de nombrar categorías.

**Límite:** No se declara lectura integral de The Sense of Style. Claridad no autoriza borrar límites materiales o incertidumbre relevante.

### John McPhee · Structure

[Structure](https://www.newyorker.com/magazine/2013/01/14/structure) · 2013-01-06; edición impresa 2013-01-14. Ensayo autobiográfico original.

**Tipo de evidencia:** Método de oficio.

**Aplicación:** Asignar a cada capítulo una función nueva dentro del libro y decidir qué debe dejar resuelto antes de enlazar el siguiente.

**Límite:** Relato de una práctica personal, no un formato obligatorio ni experimento.

### Chip Heath y Dan Heath · Made to Stick: resumen del modelo por los autores

[Made to Stick: resumen del modelo por los autores](https://heathbrothers.com/wp-content/uploads/resources/mts-made-to-stick-model.pdf) · 2008 (copyright del recurso). Hoja de síntesis oficial; no lectura integral del libro.

**Tipo de evidencia:** Modelo práctico de comunicación.

**Aplicación:** Conservar un ejemplo dominante por capítulo y estadísticas con escala humana. Evitar convertir cada apartado en otra metáfora o una nueva pregunta sin resolver.

**Límite:** No demuestra que aplicar una fórmula persuada a toda audiencia. No se adoptan ganchos artificiales, sobresaltos ni presión emocional.

### Harvard College Writing Center · Tips for Organizing Your Essay

[Tips for Organizing Your Essay](https://writingcenter.fas.harvard.edu/tips-organizing-your-essay) · s.f.; acceso 2026-10-28. Guía institucional completa.

**Tipo de evidencia:** Pedagogía de escritura.

**Aplicación:** Etiquetar cada párrafo con su aportación: escena, tesis, mecanismo, evidencia, objeción, respuesta o enlace. Fusionar los que no añaden una función.

**Límite:** El esquema sirve para revisar; no tiene que aparecer como plantilla visible ni imponer cinco párrafos.

### Harvard College Writing Center · Transitions

[Transitions](https://writingcenter.fas.harvard.edu/transitions) · s.f.; acceso 2026-10-28. Guía institucional.

**Tipo de evidencia:** Pedagogía de escritura.

**Aplicación:** El cierre recupera lo aprendido y nombra el problema siguiente. La apertura del capítulo siguiente retoma ese objeto, sin recapitular todo el libro.

**Límite:** No todas las frases necesitan un conector ni una recapitulación.

### Harvard College Writing Center · Counterargument

[Counterargument](https://writingcenter.fas.harvard.edu/counterargument) · s.f.; acceso 2026-10-28. Guía institucional.

**Tipo de evidencia:** Pedagogía de argumentación.

**Aplicación:** Una objeción principal por mecanismo cuando sea necesaria. Distinguir la objeción a una tesis moral de un límite a una predicción económica, sin hacer pasar la segunda por refutación de la primera.

**Límite:** No usar una batería ritual de cautelas ni dejar al final una objeción importante sin respuesta.

### Harvard College Writing Center · Conclusions

[Conclusions](https://writingcenter.fas.harvard.edu/conclusions) · s.f.; acceso 2026-10-28. Guía institucional.

**Tipo de evidencia:** Pedagogía de escritura.

**Aplicación:** Terminar cada capítulo con una consecuencia específica y un puente al siguiente, no con otra versión de la misma consigna moral.

**Límite:** La longitud del cierre depende del recorrido de la pieza; no existe una cifra universal.

### The Writing Center, University of North Carolina at Chapel Hill · Paragraphs

[Paragraphs](https://writingcenter.unc.edu/tips-and-tools/paragraphs/) · s.f.; acceso 2026-10-28. Guía institucional completa.

**Tipo de evidencia:** Pedagogía de escritura.

**Aplicación:** Un párrafo desarrolla una acción o inferencia. Tras el panadero o el árbitro, explicar exactamente qué ilustra y continuar el argumento, sin dejar al lector deducir el puente.

**Límite:** No reducir todos los párrafos a una frase ni fijar un mínimo de cinco.

### Robert F. Lorch y Elizabeth Pugzles Lorch · Effects of headings on text recall and summarization

[Effects of headings on text recall and summarization](https://scholars.uky.edu/en/publications/effects-of-headings-on-text-recall-and-summarization/) · 1996-07. Resumen original en repositorio institucional de los autores; no texto íntegro.

**Tipo de evidencia:** Estudio empírico: dos experimentos.

**Aplicación:** Usar subtítulos que identifiquen el paso argumental y un mapa de capítulos comprensible para un lector nuevo.

**Límite:** No prueba un aumento universal de retención, tiempo en página o convicción; no se transfiere sin más de tareas educativas a ensayos políticos.

### George D. Gopen y Judith A. Swan · The Science of Scientific Writing

[The Science of Scientific Writing](https://courses.ems.psu.edu/styleforstudents/print/c10_p6.html) · 1990-11/12. Reimpresión íntegra autorizada del artículo original de American Scientist.

**Tipo de evidencia:** Método retórico basado en expectativas del lector.

**Aplicación:** Cambiar construcciones como la necesidad de la financiación por quién necesita qué y quién paga. Dar al final de la frase el énfasis que importa.

**Límite:** No trasladar mecánicamente sintaxis inglesa al español ni presentar el artículo como ensayo experimental de este corpus.

## Lectura digital y accesibilidad

| Fuente | Criterio consultado | Aplicación y alcance |
| --- | --- | --- |
| [W3C · visual-presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation) · AAA | Mecanismo para alcanzar ancho no mayor de 80 caracteres, texto no justificado, elección de colores y separación. La página aclara que esos valores no tienen que ser el estilo predeterminado. | Usar ancho de lectura con ch y ofrecer preferencias sencillas; no vender una certificación AAA por adoptar una cifra. |
| [W3C · text-spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) · AA | No perder contenido o función si el usuario impone interlineado 1.5, separación tras párrafo 2em, tracking .12em y espacios .16em. No exige esos valores predeterminados ni controles propios. | Evitar alturas fijas en texto, controles y tarjetas; permitir que el contenido crezca. |
| [W3C · reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) · AA | Lectura vertical a ancho equivalente a 320 CSSpx sin scroll de dos dimensiones, salvo contenido que lo exige como ciertas tablas o diagramas. | Probar 320 y 390px, zoom y preferencias de texto; las tablas pueden ir en contenedor propio sin desbordar la página. |
| [W3C · contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · AA | 4.5:1 para texto normal y 3:1 para texto grande, con excepciones delimitadas. | Calcular contrastes de cuerpo, texto secundario, acento y todos los temas; no comprobar solo el negro sobre papel. |
| [W3C · target](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) · AA | 24x24 CSSpx mínimo o separación suficiente; excepciones para enlaces en texto, controles del agente y otras condiciones. Controles importantes pueden aspirar a tamaño mayor. | Objetivo de diseño 44px para preferencias, índice y continuar; no afirmar que 44 sea el mínimo AA. |
| [W3C · focus](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) · AA | El control enfocado no debe quedar totalmente oculto por contenido del autor, con condiciones. | Barras fijas y paneles no deben cubrir párrafos ni foco; scroll-padding y botones de cierre accesibles. |

65ch es una elección tipográfica de esta edición, no una garantía de 65 caracteres exactos en toda fuente. Los controles principales aspiran a 44px de altura por comodidad. El mínimo AA de tamaño de objetivo es 24px bajo las condiciones y excepciones del criterio; no se confunden ambos valores. No se declara certificación WCAG completa.

- [Risko y Gilbert, Cognitive Offloading (2016)](https://discovery.ucl.ac.uk/id/eprint/1508770/): Mostrar capítulo, parte y punto de reanudación reduce lo que el lector necesita recordar para volver. Es una aplicación editorial razonada, no un efecto cuantificado por ese artículo. Examina el uso de acciones y apoyos externos para reducir exigencias cognitivas y sus consecuencias; no estudia específicamente esta web.
- [NN/g, Memory Recognition and Recall in User Interfaces (2024)](https://www.nngroup.com/articles/recognition-and-recall/): Índice contextual, título del siguiente capítulo y continuar lectura con un título reconocible. Las pistas visibles, el contexto y los elementos visitados facilitan reconocer opciones y reanudar tareas frente a recordar nombres desde cero.

## Criterio editorial del conjunto

1. La primera parte establece persona, propiedad, consentimiento y límite de la mayoría.
2. La segunda explica cómo personas que no comparten fines coordinan conocimiento, precios, ahorro e inversión.
3. La tercera aplica incentivos y límites al aparato político, a su selección, su continuidad y sus lealtades.
4. La cuarta sigue el dinero y la dependencia: impuestos, redistribución y pensiones.
5. La quinta desarrolla proveedores, educación, sanidad, justicia, seguridad, ayuda mutua y vivienda; termina con dificultades que deben resolverse sin conceder a una persona pacífica a un poder ajeno.

La biblioteca, el glosario, los expedientes y las notas no son otros recorridos que compiten en cada final de capítulo. El índice temático permite entrar por interés y la secuencia principal siempre permite volver al hilo.

## Revisión con lectores: siguiente contraste útil

Falta una prueba con personas que no hayan participado en la edición. Se propone pedirles que lean un capítulo sin explicación previa y respondan: qué afirma, qué ejemplo lo sostiene, qué objeción responde, qué les ha resultado confuso y dónde continuarían. Después, comprobar que pueden volver a su lugar desde un móvil. Registrar errores de comprensión y navegación sirve más que perseguir minutos en página. La presente revisión no ha medido esa comprensión ni un aumento de convicción.

La evidencia de los encabezados corresponde a tareas concretas de recuerdo y resumen; no demuestra que un esquema persuada por sí mismo. Los ensayos de oficio orientan decisiones, no establecen leyes universales de longitud o estilo. La adaptación al español requiere juicio editorial.

## Verificación técnica y de cobertura

Los resultados ejecutados y sus límites se registran en [VERIFICACION.md](VERIFICACION.md). El contraste temático con los materiales de partida y las peticiones se registra en [AUDITORIA_COBERTURA.md](AUDITORIA_COBERTURA.md).
