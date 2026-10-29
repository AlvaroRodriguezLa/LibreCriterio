"""Fallback ASR local para audios accesibles. No identifica personas ni verifica cifras."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import sys
from pathlib import Path

import youtube_collect as collect

REVIEW = ['names', 'numbers', 'speaker_attribution', 'quoted_or_reproduced_speech']


def valid_video_id(value):
    if not collect.VIDEO_ID.fullmatch(value):
        raise argparse.ArgumentTypeError('El ID de vídeo debe contener 11 caracteres válidos.')
    return value


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--video-id', required=True, type=valid_video_id)
    source = cli.add_mutually_exclusive_group(required=True)
    source.add_argument('--audio', type=Path, help='Archivo local; no se descarga audio.')
    source.add_argument('--download-audio', action='store_true', help='Descarga opcional con yt-dlp, sin cookies ni proxies.')
    cli.add_argument('--output', type=Path, default=collect.DEFAULT_OUT)
    cli.add_argument('--model', choices=['base', 'small'], default='small')
    cli.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    cli.add_argument('--compute-type', choices=['int8', 'int8_float16', 'float16', 'float32', 'auto'], default='int8')
    cli.add_argument('--language', default='es', help='Idioma original, o auto para detección.')
    cli.add_argument('--local-files-only', action='store_true', help='Usa solo pesos ya disponibles en la caché.')
    return cli


def catalog_row(out, video_id):
    catalog = collect.load(out / 'catalog.json', [])
    row = next((r for r in catalog if r['id'] == video_id), None)
    if row is None:
        row = collect.load(out / 'videos' / video_id / 'metadata.json')
    if row is not None:
        if row.get('id') != video_id:
            raise ValueError('Los metadatos no corresponden al ID solicitado.')
        return copy.deepcopy(row)
    return {'id': video_id, 'url': f'https://www.youtube.com/watch?v={video_id}',
            'title': None, 'channel': {'id': None, 'name': None, 'url': None},
            'duration': None, 'metadata': {'status': 'pending'}, 'topicsRequested': [],
            'requestContexts': [], 'priority': 'normal', 'transcriptStatus': 'pending',
            'analysisStatus': 'pending', 'speakers': []}


def update_catalog(out,row):
    catalog=collect.update_row(out,row)
    collect.report(out,catalog)


def download_audio(out, row):
    """Descarga el audio original sin convertirlo ni debilitar TLS."""
    collect.enable_tls()
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError('yt-dlp no está instalado en este intérprete.') from exc
    folder = (out / 'videos' / row['id']).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    options = collect.youtube_options()
    for key in ('cookiefile', 'cookiesfrombrowser', 'username', 'password', 'proxy'):
        options.pop(key, None)
    options.update({'skip_download': False, 'format': 'bestaudio/best', 'noplaylist': True,
                    'outtmpl': str(folder / 'audio.%(ext)s'), 'writeinfojson': True,
                    'nocheckcertificate': False})
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(row['url'], download=True)
        if not isinstance(info, dict) or info.get('id') != row['id']:
            raise ValueError('La descarga no devolvió el ID de vídeo solicitado.')
        raw_path = next((d.get('filepath') for d in info.get('requested_downloads', [])
                         if d.get('filepath')), None) or downloader.prepare_filename(info)
    audio = Path(raw_path).resolve()
    if not audio.is_relative_to(folder) or not audio.is_file():
        raise ValueError('No se encontró el audio dentro de la carpeta de este vídeo.')
    fresh = collect.metadata(info, 'yt-dlp:audio')
    if fresh:
        for key in ('title', 'duration', 'availability', 'metadata'):
            if fresh.get(key) is not None:
                row[key] = fresh[key]
        row['channel'] = {**(row.get('channel') or {}),
                          **{key: value for key, value in (fresh.get('channel') or {}).items() if value is not None}}
    return audio


def audio_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def raw_segments(segments):
    """Conserva tiempos y palabras sin corregir nombres, cifras o atribuciones."""
    raw = []
    for item in segments:
        start, end = float(item.start), float(item.end)
        if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end < start:
            raise ValueError('ASR produjo un intervalo de tiempo inválido.')
        text = str(item.text)
        if not text.strip():
            continue
        row = {'start': start, 'end': end, 'duration': end - start, 'text': text}
        for name in ('id', 'seek', 'tokens', 'avg_logprob', 'no_speech_prob', 'compression_ratio'):
            value = getattr(item, name, None)
            if value is not None:
                row[name] = value
        raw.append(row)
    if not raw:
        raise ValueError('ASR no produjo voz transcrita; no se registra como éxito.')
    return raw


def transcribe(args, out, row, audio):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError('faster-whisper no está instalado. Este complemento es opcional.') from exc
    collect.enable_tls()
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type,
                         local_files_only=args.local_files_only)
    requested_language = None if args.language == 'auto' else args.language
    segments, info = model.transcribe(str(audio), language=requested_language, beam_size=5, vad_filter=True)
    raw = raw_segments(segments)  # La iteración ejecuta y termina el generador de faster-whisper.
    language = getattr(info, 'language', None) or requested_language or 'und'
    try:
        version = importlib.metadata.version('faster-whisper')
    except importlib.metadata.PackageNotFoundError:
        version = None
    run = {'at': collect.now(), 'method': 'local_asr', 'model': args.model,
           'device': args.device, 'computeType': args.compute_type, 'tool': 'faster-whisper',
           'toolVersion': version, 'languageRequested': args.language, 'languageDetected': language,
           'localFilesOnly': args.local_files_only, 'audioSource': 'yt-dlp:audio' if args.download_audio else 'local_file',
           'audioPath': str(audio), 'audioSha256': audio_hash(audio), 'diarizationPerformed': False,
           'speakerNamesVerified': False, 'namesVerified': False, 'numbersVerified': False,
           'requiresReview': REVIEW}
    transcript = collect.store_transcript(out, row, raw, language, True, 'local_asr')
    folder = out / 'videos' / row['id']
    for filename, value in (('transcript.json', transcript),
                            ('transcript.original.json', collect.load(folder / 'transcript.original.json'))):
        value.update({'asr': run, 'namesVerified': False, 'numbersVerified': False,
                      'diarizationPerformed': False, 'requiresReview': REVIEW})
        collect.save(folder / filename, value)
    row['transcript'].update({'namesVerified': False, 'numbersVerified': False,
                              'speakerNamesVerified': False, 'diarizationPerformed': False})
    row['asrStatus'] = 'completed'
    row['asr'] = run
    row.pop('asrError', None)
    if row.get('error'):
        row['previousCollectionError'] = row.pop('error')
    collect.save(folder / 'asr-run.json', run)
    collect.save(folder / 'metadata.json', row)
    update_catalog(out, row)
    return {'id': row['id'], 'status': 'downloaded', 'method': 'local_asr',
            'words': transcript['wordCount'], 'segments': len(transcript['segments']),
            'requiresReview': REVIEW}


def main(argv=None):
    args = parser().parse_args(argv)
    out = args.output.resolve()
    row = catalog_row(out, args.video_id)
    existing = collect.load(out / 'videos' / args.video_id / 'transcript.json')
    if existing and existing.get('segments'):
        print(json.dumps({'id': args.video_id, 'status': 'skipped_existing',
                          'message': 'Se conserva la transcripción existente. Use otra carpeta --output para comparar ASR.'}, ensure_ascii=False))
        return 0
    try:
        if args.audio:
            audio = args.audio.resolve()
            if not audio.is_file():
                raise FileNotFoundError('No existe el archivo de audio local indicado.')
        else:
            audio = download_audio(out, row)
        result = transcribe(args, out, row, audio)
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return 0
    except Exception as exc:
        row['asrStatus'] = 'error'
        row['asrError'] = {'type': type(exc).__name__, 'message': str(exc)[:800], 'at': collect.now()}
        update_catalog(out, row)
        print(json.dumps({'id': args.video_id, 'status': 'asr_error', 'error': row['asrError']}, ensure_ascii=False),
              file=sys.stderr, flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
