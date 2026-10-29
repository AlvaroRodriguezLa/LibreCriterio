# Biblioteca audiovisual local

El 29 de octubre de 2026 se comprobó el acceso a la lista pública Lib: 72 vídeos de cuatro canales, incluidos los 41 enlaces distintos indicados en la conversación. El inventario guarda título, URL, canal e ID; los resultados y el avance real se consultan en knowledge/youtube/status.json. No se confunde recuperar una transcripción con revisar su contenido ni con verificar sus cifras.

## Usarla en este ordenador

Desde la carpeta del proyecto, en PowerShell:

~~~powershell
./tools/Youtube-Library.ps1 -Action Status
./tools/Youtube-Library.ps1 -Action Open
~~~

Open sirve la biblioteca privada en http://127.0.0.1:4333/ y mantiene la terminal ocupada. Abre esa dirección en el navegador; Ctrl+C cierra únicamente el visor. Puedes filtrar por canal o estado, buscar títulos e ideas, consultar las fichas y abrir su evidencia en el minuto del vídeo. La transcripción completa se despliega bajo cada ficha. La página es una instantánea: recarga después de que el lote termine otro vídeo.

~~~powershell
./tools/Youtube-Library.ps1 -Action Start
./tools/Youtube-Library.ps1 -Action Stop
~~~

Start inicia una sola cola oculta y reanudable. No instala una tarea programada ni necesita que el chat siga abierto, pero sí que el ordenador esté encendido y pueda acceder a la red. Si ya hay una cola del proyecto activa, no crea otra. Stop solicita detener también el proceso de transcripción en curso; conserva los vídeos terminados. Start retoma los que faltan. Una transcripción interrumpida puede tener que comenzar de nuevo; no se promete reanudación dentro del audio.

La cola intenta subtítulos públicos y, si faltan o están temporalmente bloqueados, puede transcribir el audio público con faster-whisper base en CPU int8. Respeta las pausas registradas y no utiliza cookies, cuentas, proxies ni desactiva TLS. Si solo quieres subtítulos, inicia con -WithoutAsr. Un fallo queda registrado; no se presenta como éxito. Al terminar el recorrido, complete significa transcripciones recuperadas, no análisis semánticos completos; needs_attention indica entradas que aún requieren atención.

El reconocimiento local no requiere una API de pago. Consume descargas, almacenamiento y tiempo de CPU. El modelo base es un primer borrador: nombres, cifras, negaciones y citas necesitan contraste. No se ha instalado diarización: las voces sin identificación fiable permanecen sin nombre, también cuando el canal pertenece a una persona conocida.

## Qué se guarda

- knowledge/youtube/catalog.json: título, enlace, canal, posición, temas solicitados y estado por vídeo.
- knowledge/youtube/videos/ID/: metadata.json, transcript.original.json, transcript.json, transcript.txt y, cuando se utiliza ASR, audio y asr-run.json.
- knowledge/youtube/channels.json: agrupaciones por canal. El catálogo conserva además el ID estable del canal.
- knowledge/youtube/analysis/ID.json: argumentos, ejemplos, analogías, cifras, críticas y casos con evidencia temporal; se distingue lo conservado, lo matizado, lo rechazado y lo pendiente de contraste.
- knowledge/youtube/batch-control.json y worker.log: fase actual, errores y registro del lote.
- knowledge/models/: caché del modelo local.

La carpeta knowledge y el entorno .venv-youtube están excluidos de Git. Los audios y transcripciones completos se conservan para trabajo local, no se publican en la web.

## Revisar sin inventar atribuciones

~~~powershell
./.venv-youtube/Scripts/python.exe tools/youtube_review.py pack
./.venv-youtube/Scripts/python.exe tools/youtube_review.py validate
./.venv-youtube/Scripts/python.exe tools/youtube_review.py build
~~~

pack prepara fragmentos de lectura con IDs y tiempos. No genera por sí solo una interpretación. La revisión de argumentos se realiza siguiendo tools/YOUTUBE_REVIEW_PROTOCOL.md. validate comprueba la huella de la transcripción y que las evidencias existan: no demuestra que una atribución o cifra sea verdadera. build actualiza el visor con las fichas validadas.

Para distinguir un debate de un vídeo de reacción hay que separar voz, identidad, autor de una cita y postura del presentador. Una revisión textual completa sigue marcada transcript_only hasta que se coteje el audiovisual. El canal no identifica automáticamente a quien pronuncia cada frase. No se ha instalado un modelo local que automatice esta evaluación semántica.

## Preparar otra instalación

Requiere Python 3.11 o posterior y un Node compatible con yt-dlp. Este proyecto se ejecutó con Python 3.12 y Node 22. Desde la raíz:

~~~powershell
py -3 -m venv .venv-youtube
./.venv-youtube/Scripts/python.exe -m pip install -r tools/requirements-youtube-asr.txt
./.venv-youtube/Scripts/python.exe tools/youtube_collect.py inventory
./tools/Youtube-Library.ps1 -Action Start
~~~

La primera ejecución del reconocimiento descarga los pesos del modelo. En este ordenador se usa la caché knowledge/models. Las versiones del archivo de requisitos se probaron juntas; av se fija en 17.1.0 por una incompatibilidad observada con la versión 19. No se requiere instalar FFmpeg para decodificar el contenedor de audio elegido mediante PyAV; otras conversiones sí pueden necesitarlo.

## Verificación y límites

Las pruebas offline se ejecutan con ./.venv-youtube/Scripts/python.exe -m unittest discover -s tests -p 'test_youtube*.py' -v. Cubren conservación de palabras y cifras, deduplicación de ventanas solapadas, ausencia de sobrescritura, errores de audio y modelos, metadatos, evidencias inventadas y huellas obsoletas. No miden precisión de reconocimiento ni identifican voces.

La guía TRANSCRIPCION_GRATUITA.md conserva la investigación de opciones. Este documento describe la implementación y su ejecución efectiva. El análisis de los seis vídeos prioritarios está en ANALISIS_VIDEOS_PRIORITARIOS.md; los números de cobertura se consultan en el registro vivo, no se deducen del número de archivos creados.
