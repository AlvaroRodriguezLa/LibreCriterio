# Verificación de Una vida propia

Fecha: 28 de octubre de 2026.

## Aplicación y publicación

- Astro check: 61 archivos, cero errores, advertencias o sugerencias.
- Pruebas del proyecto: bloques y fuentes plegables, contenido de 29 capítulos, secuencia global en cinco partes, publicador con Git simulado, autenticación por código, expediente político y nueve pruebas de estado del lector.
- Compilación estática con BASE_PATH=/LibreCriterio y PUBLIC_SITE_URL=https://alvarorodriguezla.github.io: correcta.
- Verificador de salida: 47 archivos HTML, 2.184 enlaces o recursos locales válidos; avance y retroceso globales de los 29 capítulos; 17 fichas políticas y anclas únicas.
- Las referencias completas se conservan en desplegables cerrados; el argumento queda fuera. Los tiempos excluyen bibliografía y JSON de cuadros.

## Navegador integrado

Comprobaciones realizadas en la vista previa local mediante la interfaz de la aplicación:

- Lectura en escritorio y anchos de 390 y 320 CSSpx, con 20 y 24px de cuerpo; sin desbordamiento horizontal de página en los capítulos revisados.
- Tamaño, familia serif/sans, fondos papel/claro/oscuro y concentración; preferencias conservadas al cambiar de capítulo.
- Índice en diálogo: parte actual abierta, capítulo identificado, cierre con Escape y foco de vuelta al enlace Índice.
- Marca explícita de capítulo completado. Retomar desde el índice ofrece el capítulo siguiente después de completar el anterior.
- Avance desde el capítulo 4 al 5: cambia de primera a segunda parte sin detener la lectura.
- Reanudación por sección: entrar sin ancla mantiene el comienzo y ofrece Retomar; al pulsarlo, enfoca la sección guardada. Se corrigió un margen doble que podía guardar la sección anterior.
- Enlaces a notas: abren las fuentes; la guía del documental contiene quince pasos explicados. El porcentaje llega al 100% del argumento sin exigir leer la bibliografía.
- Las tarjetas sanitarias se adaptan a una columna en móvil, incluso con fondo oscuro y texto grande.

El texto y las direcciones de continuación son HTML estático. Su presencia se verifica en la compilación; no se ha realizado una sesión adicional con JavaScript desactivado. Los controles que dependen de scripts se ocultan hasta estar listos. El almacenamiento bloqueado o corrupto se cubre con pruebas unitarias; no se han alterado las preferencias de privacidad reales del navegador para simularlo.

## Contraste

Se calcularon 18 combinaciones de cuerpo, secundario y acento sobre papel y superficie en los tres temas. La menor relación es 4,90:1. No equivale a una certificación WCAG completa: quedan fuera una auditoría exhaustiva con tecnologías de apoyo y todas las combinaciones posibles de estilos impuestos por el usuario.

## Edición y cobertura

La [auditoría](AUDITORIA_COBERTURA.md) contrasta 55 temas con las secciones efectivas de los 29 capítulos: 52 desarrollados y tres exclusiones justificadas. Enumera también 21 peticiones previas, el lugar de los desarrollos y sus límites. El documental se desarrolla en notas enlazadas; no se cuenta como parte obligatoria de los minutos del capítulo.

La [investigación de lectura](INVESTIGACION_LECTURA.md) distingue observación de mercado, consejo de oficio, pedagogía, estudio empírico y decisiones de diseño inferidas. No se ha realizado una prueba de comprensión o persuasión con lectores ajenos al proyecto.

Los expedientes políticos mantienen su revisión y fecha del 28 de octubre de 2026. Esta edición no convierte investigaciones en condenas ni afirma haber recopilado toda controversia. Las cifras económicas conservan su periodo y sus condiciones.

## Límites de otros servicios

El Studio se conserva local, sin base de datos o servicios de pago requeridos. Sus operaciones Git se prueban simuladas. No se han probado credenciales ni correo de una nueva instalación remota en Vercel. No se modifica el alcance de las comprobaciones históricas del mapa interactivo: la validación técnica anterior tuvo un límite en el cierre del Chrome temporal, y no se reetiqueta como una certificación completada.
