# Transcripción gratuita para la base de ensayos

Revisión técnica inicial: 28 de octubre de 2026. Este documento conserva la investigación y las recetas de referencia de esa fase. El 29 de octubre se puso en marcha la implementación local: consulta YOUTUBE_EN_MARCHA.md y knowledge/youtube/status.json para conocer la ejecución efectiva. Las limitaciones de acceso descritas aquí no equivalen al resultado actual de la cola.

La opción adecuada es un flujo local por etapas: inventariar, obtener metadatos, recuperar subtítulos, transcribir solo lo que falte y analizar con trazabilidad. No hace falta contratar una API de pago. La palabra gratuito se refiere al software y a no exigir una suscripción: el ordenador, las descargas, el almacenamiento y el tiempo de cálculo siguen importando.

## Qué usar y para qué

| Herramienta | Función | Condición importante |
| --- | --- | --- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Inventario, título, canal, fecha y pistas de subtítulos | La lista plana puede omitir metadatos; completar cada vídeo. |
| [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | Otra vía para las pistas y sus tiempos | Puede ser bloqueada por YouTube; no interpreta ni identifica hablantes. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Transcripción local del audio cuando falte una pista útil | CPU int8 es una opción; probar un fragmento antes de procesar horas. |
| [pyannote community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) | Separar intervalos por voz | Requiere cuenta, condiciones y token para descargar; las etiquetas no son nombres. |
| [WhisperX](https://github.com/m-bain/whisperX) | Alineación por palabra y enlace con diarización | Añade complejidad; el propio proyecto reconoce fallos con solapamientos y ciertas cifras. |

No conviene empezar por reconocimiento de audio para todos los vídeos. Una pista ya disponible cuesta menos tiempo y conserva una referencia original que después se puede cotejar con el sonido. Tampoco se debe asumir que un fallo de descarga significa que no existen subtítulos. Registrar el motivo evita tratar un bloqueo como si fuera ausencia de contenido.

La [API oficial de descarga de subtítulos](https://developers.google.com/youtube/data/reference/rest/v3/captions/download) requiere permiso para editar el vídeo: no sirve como acceso universal a transcripciones de canales ajenos. La [API de listas](https://developers.google.com/youtube/data/reference/rest/v3/playlistItems/list) puede inventariar con paginación, pero es otro trámite de configuración.

## Preparación en Windows

Usar un entorno separado del de la web evita mezclar paquetes de Python con Astro. Según la documentación consultada, yt-dlp admite Python 3.11 o posterior. Comprobar primero la versión, no suponer que cualquier instalación antigua sirve. La [instalación oficial](https://github.com/yt-dlp/yt-dlp/wiki/Installation) contempla el extra default.

```powershell
py -3 --version
py -3 -m venv .venv-youtube
& "./.venv-youtube/Scripts/python.exe" -m pip install -U "yt-dlp[default]" youtube-transcript-api
```

Para el soporte actual de YouTube, [EJS](https://github.com/yt-dlp/yt-dlp/wiki/EJS) requiere un runtime JS compatible. Deno es la opción recomendada por el proyecto; Node 22 o posterior puede aprovecharse si ya está disponible, activándolo con --js-runtimes node. FFmpeg y ffprobe son necesarios para ciertas conversiones y operaciones de audio; el paquete Python llamado ffmpeg no sustituye a sus ejecutables.

## Inventario y extracción de referencia

Los comandos se ejecutan desde la carpeta del proyecto. La URL mantiene el identificador enviado por el usuario; este documento no afirma que esa lista sea accesible. El inventario se conserva aunque alguna entrada no pueda descargarse.

```powershell
$pythonExe = "./.venv-youtube/Scripts/python.exe"
$playlistUrl = "https://www.youtube.com/playlist?list=PLGndpsTZkaBk"
New-Item -ItemType Directory -Force -Path "research/youtube" | Out-Null
& $pythonExe -m yt_dlp --ignore-config --js-runtimes node --flat-playlist --dump-single-json --skip-download -- $playlistUrl | Set-Content -Encoding utf8 "research/youtube/playlist.json"
```

No confundir el inventario plano con una ficha completa. Conservar el ID como clave del vídeo y el ID del canal para la agrupación; los nombres y títulos pueden cambiar. Después obtener metadatos y pistas mediante una extracción completa:

```powershell
& $pythonExe -m yt_dlp --ignore-config --js-runtimes node --skip-download --write-info-json --write-subs --write-auto-subs --sub-langs "es.*,en.*" --sub-format "vtt/best" --sleep-requests 1 --sleep-subtitles 5 --ignore-errors --windows-filenames -o "research/youtube/raw/%(channel_id)s/%(id)s.%(ext)s" -- $playlistUrl
```

Un proceso con ignore-errors puede terminar dejando fallos. El informe final debe contar éxitos y errores por vídeo; la existencia de una carpeta o el final de un comando no equivale a una extracción completa. Guardar cada pista original antes de normalizarla. En subtítulos automáticos rodantes puede haber repeticiones entre intervalos: limpiar solapamientos sin eliminar una repetición retórica real.

## Adaptador alternativo de transcripciones

La API Python actual usa una instancia, no los antiguos ejemplos de get_transcript estático. Este ejemplo conserva información de procedencia. El título y el canal se obtienen de los metadatos del vídeo, no de esta API. [Documentación de youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api/blob/master/README.md).

```python
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

video_id = "KQ7DP7A8jLc"
result = YouTubeTranscriptApi().fetch(video_id, languages=["es", "en"])
payload = {
    "video_id": video_id,
    "language": result.language_code,
    "is_generated": result.is_generated,
    "segments": result.to_raw_data(),
}
Path("transcript.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
```

list(video_id) permite inspeccionar las pistas y seleccionar manuales o generadas. Si importa distinguir variantes o priorizar español automático frente a una traducción, hacerlo expresamente. Conservar la lengua original y no hacer pasar una traducción automática por las palabras originales. Ante RequestBlocked o IpBlocked, registrar y detener los reintentos insistentes; no se recomienda contratar proxies ni resolver automáticamente CAPTCHA.

## Audio local cuando falten subtítulos útiles

Instalar faster-whisper solo si hace falta esa segunda etapa. Su README indica Python 3.9 o posterior; para el conjunto sigue siendo conveniente el mínimo más alto de yt-dlp. PyAV incorpora las bibliotecas de decodificación de FFmpeg, de modo que faster-whisper no exige por sí mismo el ejecutable del sistema. Esto no elimina las necesidades de otros componentes. [Fuente original](https://github.com/SYSTRAN/faster-whisper).

```powershell
& $pythonExe -m pip install faster-whisper
```

Ejemplo para un archivo de audio disponible localmente; no presupone que se haya podido obtener el vídeo:

```python
import json
from pathlib import Path
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.webm", language="es", beam_size=5, vad_filter=True)
rows = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
Path("transcript-asr.json").write_text(json.dumps({
    "source": "asr_local", "language": info.language, "segments": rows,
}, ensure_ascii=False, indent=2), encoding="utf-8")
```

El modelo small es un punto de prueba, no una garantía de precisión para estos vídeos. Deben comprobarse nombres, importes, negaciones y cambios de voz en un fragmento representativo. No se trasladan los benchmarks del repositorio a este ordenador. Para GPU, la versión actual documenta CUDA 12 y cuDNN 9; no se deben instalar controladores o degradar librerías a ciegas. Los modelos descargados consumen espacio y su primera ejecución puede necesitar red.

## Diferenciar voces y atribuciones

El [modelo community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) puede trabajar localmente tras su descarga. Su acceso exige aceptar condiciones y aportar una cuenta/token: no se ha hecho desde esta investigación. El [código pyannote](https://github.com/pyannote/pyannote-audio) usa MIT; el modelo tiene CC-BY-4.0. La versión actual usa FFmpeg para la decodificación por TorchCodec. La opción de API alojada de pyannoteAI es un producto distinto y no se incluye en la recomendación gratuita.

La salida proporciona intervalos de SPEAKER_00, SPEAKER_01, etc. Hay cuatro decisiones separadas: qué voz se oye, quién es esa persona, de quién es la afirmación que cita y qué posición adopta quien presenta el vídeo. Una sola voz puede leer palabras de un rival; varias voces pueden pertenecer a un clip insertado. El propietario del canal no es automáticamente autor de todo lo dicho.

Para asignar un nombre, conservar evidencia con tiempo: presentación explícita, rótulo visible o descripción contrastada con el contenido. Si falta, mantener el nombre vacío. Para una reacción, distinguir anfitrión, invitado, clip reproducido, cita leída y atribución dudosa. Para un debate, guardar por separado tesis, objeción y respuesta. No elegir argumentos por quién habla ni por una palabra clave aislada.

## Automatizar el análisis sin inventar precisión

Un modelo local puede preparar borradores JSON mediante [salidas estructuradas de Ollama](https://docs.ollama.com/capabilities/structured-outputs). No requiere una API de pago si el modelo se ejecuta en el ordenador; el tamaño y la licencia dependen del modelo elegido. Validar un esquema comprueba la forma de los datos, no su verdad. No se ha instalado ni probado un modelo semántico en esta investigación.

El diseño recomendado divide la transcripción por turnos o fragmentos solapados y registra la cobertura de principio a fin. Cada fragmento debe quedar clasificado como argumento, ejemplo, dato, contexto, cita, repetición, promoción o tramo incierto. Resumir solo la introducción no autoriza a afirmar que se ha revisado un vídeo línea por línea.

Cada ficha de idea necesita: vídeo y tiempos; voz y evidencia del nombre; papel y postura; tesis parafraseada; premisas y conclusión; ejemplo, analogía o metáfora; objeción y respuesta; caso criticado; principio liberal implicado; cuestiones por verificar y estado editorial. Mantener una referencia al texto original evita que sucesivos resúmenes cambien lo dicho.

Cada número debe conservar unidad, fecha, población, condición y quién lo afirma. Distinguir un dato observado de una proyección, ejemplo o reducción al absurdo: pedir un salario mínimo de 15.000 euros como prueba retórica no equivale a defender esa política. Para publicar un dato, volver al audio y a la fuente primaria pertinente. La [ficha original de Whisper](https://github.com/openai/whisper/blob/main/model-card.md) recuerda que ASR puede producir errores y texto no pronunciado.

## Reanudar, revisar y utilizar

Guardar estado por vídeo y por fase permite continuar sin repetir todo el trabajo. Estados útiles: pendiente, metadatos completos, pista manual, pista automática, ASR local, privado/eliminado, sin pista, bloqueo de acceso, error de red, pendiente de hablantes y listo para revisión editorial. Conservar versión de herramienta/modelo, fecha y huella de los archivos. Limitar concurrencia y reintentos; volver después solo a los fallos recuperables.

Las transcripciones completas y el audio son material local de trabajo. Los ensayos públicos deben emplear argumentos redactados de nuevo, referencias y citas breves pertinentes, sin convertir la base en una copia indiscriminada de vídeos. El motor libre no determina la licencia de los materiales de terceros. No publicar de forma automática interpretaciones o atribuciones que aún estén en revisión.

## Licencias y alcance de esta revisión

El código fuente de [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE) es Unlicense; sus paquetes y dependencias pueden incluir otras condiciones. [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api/blob/master/LICENSE) y [faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE) tienen MIT. WhisperX se presenta actualmente con BSD-2-Clause; no reutilizar descripciones antiguas de su licencia sin revisar la versión. Las condiciones y atribución de los pesos de modelos se comprueban por separado.

La investigación inicial verificó documentación y diseñó el procedimiento. La ejecución posterior quedó registrada en el almacén local y en YOUTUBE_EN_MARCHA.md. Las tasas de error y la identificación de voces no se deducen del número de vídeos recuperados.

## Complemento ASR implementado en este proyecto

El comando tools/youtube_asr.py integra faster-whisper con el almacén del colector. Acepta un audio local y un ID válido; conserva título, canal, temas y contexto ya conocidos. Guarda segmentos originales, normalizados y texto con tiempos mediante store_transcript(), además de un registro asr-run.json con modelo, configuración y huella del audio. El método queda identificado como local_asr; nombres, cifras y atribuciones siguen sin verificar y no se ejecuta diarización.

Ejemplo para un archivo que ya tengas en el ordenador, desde la carpeta del proyecto:

```powershell
$pythonExe = "./.venv-youtube/Scripts/python.exe"
& $pythonExe tools/youtube_asr.py --audio "C:/ruta/al/audio.webm" --video-id ECioYubkBpo --model small --device cpu --compute-type int8 --local-files-only
```

El archivo del ejemplo debe sustituirse por uno real. --local-files-only pide usar pesos ya cacheados y requiere una caché completa: no instala faster-whisper ni prepara el modelo. Si quitas esa opción y faltan los pesos, el constructor puede descargarlos. Las pruebas iniciales fueron simuladas; la ejecución posterior sí instaló las dependencias y descargó el modelo base en la caché local. Consulta YOUTUBE_EN_MARCHA.md. El comando --help funciona aunque faster-whisper no esté instalado.

La descarga de audio es una opción separada y explícita:

```powershell
& $pythonExe tools/youtube_asr.py --download-audio --video-id ECioYubkBpo --model base --device cpu --compute-type int8 --local-files-only
```

Usa las opciones y la configuración TLS del colector, descarga el contenedor de audio sin convertirlo e incorpora los metadatos devueltos. No añade cookies, proxies ni credenciales ni desactiva la comprobación del certificado. Esta opción también puede fallar si YouTube bloquea el acceso; no se presenta como un modo de eludir ese bloqueo.

Para no sustituir una pista ya recuperada, si existe una transcripción con segmentos el comando informa skipped_existing y la conserva. Para comparar otro reconocimiento, utiliza una carpeta --output diferente. Un audio vacío, un error del modelo o una descarga fallida no se contabilizan como una nueva transcripción correcta.

Comprobación offline del complemento:

```powershell
python -m py_compile tools/youtube_asr.py tests/test_youtube_asr.py
python -m unittest discover -s tests -p test_youtube_asr.py -v
```

Las pruebas usan modelos y descargas simulados. Verifican el consumo completo del generador, la conservación de cifras y palabras, los hablantes sin nombre, la integración con store_transcript(), los metadatos, los errores y la ausencia de sobrescritura de pistas existentes. No acreditan la precisión de voz sobre los vídeos reales.
