# Libre Criterio

Publicación independiente sobre liberalismo, mercados y límites del poder, adaptada de la base Astro de ONE SHOT.

- Web pública: https://alvarorodriguezla.github.io/LibreCriterio/
- Código: https://github.com/AlvaroRodriguezLa/LibreCriterio
- Expediente con 17 casos documentados, seis contrastes de declaraciones y cronología de Ceuta.
- 38 capítulos en cinco partes, 26 lecturas comentadas, 24 conceptos, cuatro modelos interactivos y una agenda de doce investigaciones.
- Documento maestro: pptLIB.pdf, 75 páginas. Los Word son satélites; no se suben a Git ni a la web.

## Abrir el proyecto

Requiere Node.js 22.12 o posterior dentro de la rama 22, o una versión compatible con Astro.

1. npm ci
2. npm run dev
3. Abre http://127.0.0.1:4331/

## Publicar desde el ordenador

1. npm run studio
2. Abre http://127.0.0.1:4332/
3. Introduce el código temporal que imprime la terminal.
4. Escribe o importa Markdown. Puedes usar la portada conceptual predeterminada.
5. Guarda un borrador o publica con el botón de Git. El despliegue de Pages se ejecuta tras el push a main.

El Studio escucha en localhost por defecto. Para acceso desde tu Wi-Fi, define STUDIO_HOST=0.0.0.0 antes de iniciarlo; conserva el código temporal y usa solo una red de confianza.

En GitHub Pages no se ejecutan las API del Studio. La ruta /studio/ explica cómo abrir el editor local. La variante de Studio remoto para Vercel se conserva preparada, pero necesita un proyecto y credenciales propios; no se han copiado los de ONE SHOT.

## Añadir y editar ensayos

Los textos están en src/content/articles/*.md. Las portadas son SVG locales. La biblioteca, el orden del libro, la agenda y el glosario se editan en src/data/.

Cada ensayo conserva masterPages, thesis, related, level y order. Al editar un artículo manualmente, mantén esos campos. La API remota preserva los campos de un artículo existente.

Bloques: usa cercas oneshot con objetos concept-flow, stat-cards, editorial-callout, source-note o chart-block. El Studio puede insertarlos y previsualizarlos. Véase docs/PUBLICACION.md.

## Comprobar

- npm run check
- npm test
- npm run build
- node scripts/verify-build.mjs

Para comprobar las rutas de Pages localmente, compila con BASE_PATH=/LibreCriterio y PUBLIC_SITE_URL=https://alvarorodriguezla.github.io. Usa BASE_PATH también en el verificador.

## Publicación gratuita

El workflow .github/workflows/deploy.yml instala, comprueba, prueba y compila antes de desplegar dist. El repositorio público permite usar GitHub Pages con GitHub Free, sujeto a los límites del servicio. No hay base de datos, analítica, publicidad ni servicios de pago requeridos.

Fuente del alojamiento: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Documentación editorial

- docs/ESTUDIO_EDITORIAL.md: análisis del maestro, satélites, mapa de artículos y correcciones.
- docs/PUBLICACION.md: cómo trabajar con los bloques y el Studio.
- docs/VERIFICACION.md: alcance de las comprobaciones y límites.

## Libro web

Una vida propia tiene un orden canónico en src/data/routes.json. El avance atraviesa las partes; chapter-bridges.json contiene el enlace narrativo entre capítulos. El lector ofrece tamaño, fuente, temas, concentración y posición local por sección. Las fuentes se despliegan al pie; su contenido se incluye al imprimir.

- [Investigación de mercado, escritura y lectura](docs/INVESTIGACION_LECTURA.md).
- [Auditoría de cobertura de la edición anterior](docs/AUDITORIA_COBERTURA.md).
- [Ampliación de 41 temas solicitados](docs/AUDITORIA_AMPLIACION_2026-10-29.md).
- [Integración de los 87 argumentos de los seis vídeos prioritarios](docs/INTEGRACION_VIDEOS_PRIORITARIOS.md).

Al añadir un capítulo al libro, incorpora su slug en routes.json y su transición en chapter-bridges.json, y conserva las pruebas de continuidad y cobertura del índice. La secuencia y el artículo se publican juntos para evitar capítulos sin lugar en el índice.

## Fuentes audiovisuales

Recopilador gratuito y reanudable de la lista Lib: metadatos, subtítulos y reconocimiento local de audio cuando es necesario. El visor privado permite buscar por canal, consultar transcripciones y revisar argumentos con marcas de tiempo. Consulta [la guía de ejecución](docs/YOUTUBE_EN_MARCHA.md), [la investigación de herramientas](docs/TRANSCRIPCION_GRATUITA.md) y [el análisis de los seis vídeos prioritarios](docs/ANALISIS_VIDEOS_PRIORITARIOS.md). Los originales y audios permanecen en knowledge/, excluidos de Git.
