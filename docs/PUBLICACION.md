# Publicar y mantener Libre Criterio

## El flujo más corto

Ejecuta npm run studio y abre http://127.0.0.1:4332/. El servidor imprime un código temporal. No se publica ese código en la web.

Puedes escribir Markdown, importar un .md o cargar la demostración. El título y el texto son necesarios. La portada conceptual permite empezar sin preparar una imagen. Si subes una, el Studio conserva el original y genera WebP.

Guardar borrador crea un artículo con draft: true. El build público lo excluye. Publicar guarda, hace commit y push; GitHub Actions ejecuta comprobaciones y despliega.

El editor local reabre borradores. Para modificar los ensayos publicados, edita su Markdown; la variante remota conserva la edición de publicados cuando se configure en Vercel. Se bloquea sobrescribir silenciosamente un publicado por colisión de título.

## Esquema de ideas

Inserta un bloque concept-flow desde el diálogo del Studio. Cada línea contiene un título y una explicación, separados por |. Admite entre dos y seis pasos.

Ejemplo:

```oneshot
{"type":"concept-flow","title":"Un mecanismo","steps":[{"title":"Información","text":"Se observa una necesidad."},{"title":"Elección","text":"Se comparan alternativas."},{"title":"Corrección","text":"Se revisan resultados."}],"note":"Esquema conceptual, no prueba causal universal."}
```

## Tarjetas, gráficos y fuentes

Las tarjetas se guardan como stat-cards. Incluye valor, etiqueta, descripción y fuente. Añade después una nota source-note con URL, año y metodología cuando haga falta. Las cifras ilustrativas deben identificarse como supuestos.

Los tipos editorial-callout, chart-block y source-note conservan el formato de la base original. Las cercas oneshot se validan tanto al guardar como en Astro. Un JSON inválido no debe publicarse.

## Metadatos de los ensayos

- order: recorrido de la colección inicial.
- masterPages: páginas del PDF de partida.
- satellites: textos de apoyo utilizados.
- thesis: idea del margen de lectura.
- related: slugs de ensayos relacionados.
- level: Iniciación, Intermedio o Avanzado.

Los campos de procedencia son opcionales para nuevos artículos. Consérvalos al editar los diecisiete iniciales. La API remota mantiene campos desconocidos de un publicado existente, incluido su origen.

## Studio remoto opcional

El código de autenticación GitHub y código por correo se conserva en api/. No está activo en GitHub Pages. Para activarlo se necesita otro proyecto Vercel, una aplicación OAuth y las variables privadas de .env.example. Usa el callback del nuevo dominio y el repositorio LibreCriterio.

No reutilices la identidad del proyecto ONE SHOT ni publiques secretos. La configuración ausente bloquea el acceso y la publicación remota. No hace falta este servicio para usar la web ni el Studio local.

## Mantener el coste

La web pública es estática y se aloja en GitHub Pages. El Studio local no necesita base de datos ni correo. El flujo normal depende de los límites gratuitos de GitHub; no se ha activado ningún plan de pago.
