"""Pruebas offline del fallback ASR. No descargan modelos, audio ni paquetes."""
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import youtube_asr as asr

VIDEO = 'KQ7DP7A8jLc'
OTHER = '6a2abobuKXo'


class LocalAsrTest(unittest.TestCase):
    def setUp(self):
        workspace = Path(__file__).resolve().parents[1]
        scratch = (workspace / 'tmp').resolve()
        if not scratch.is_relative_to(workspace):
            raise RuntimeError('La carpeta temporal debe permanecer dentro del proyecto.')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='youtube-asr-', dir=scratch)
        self.root = Path(self.temp.name).resolve()
        if not self.root.is_relative_to(scratch):
            raise RuntimeError('Ruta temporal inesperada.')
        self.out = self.root / 'knowledge'
        self.audio = self.root / 'audio.webm'
        self.audio.write_bytes(b'audio-fixture-no-real-voice')
        self.base = {'id': VIDEO, 'url': f'https://www.youtube.com/watch?v={VIDEO}',
                     'title': 'Título comprobado', 'channel': {'id': 'UCexample', 'name': 'Canal comprobado'},
                     'duration': 25, 'metadata': {'status': 'verified_from_source'},
                     'topicsRequested': ['dinero'], 'requestContexts': ['Contexto solicitado'],
                     'priority': 'high', 'transcriptStatus': 'blocked', 'analysisStatus': 'pending',
                     'speakers': [], 'position': 1, 'error': {'type': 'IpBlocked'}}
        self.other = {'id': OTHER, 'url': f'https://www.youtube.com/watch?v={OTHER}',
                      'title': 'Otro vídeo', 'channel': {'id': 'UCother', 'name': 'Otro canal'},
                      'transcriptStatus': 'pending', 'analysisStatus': 'pending', 'position': 2}
        asr.collect.save(self.out / 'catalog.json', [self.base, self.other])
        self.stdout, self.stderr = io.StringIO(), io.StringIO()

    def tearDown(self):
        if not self.root.resolve().is_relative_to((Path(__file__).resolve().parents[1] / 'tmp').resolve()):
            raise RuntimeError('No se elimina una carpeta fuera del espacio de pruebas.')
        self.temp.cleanup()

    def args(self, *extra):
        return ['--video-id', VIDEO, '--audio', str(self.audio), '--output', str(self.out),
                '--model', 'small', '--device', 'cpu', '--compute-type', 'int8', '--local-files-only', *extra]

    def fake_module(self, segments):
        model = MagicMock()
        model.transcribe.return_value = (segments, types.SimpleNamespace(language='es'))
        module = types.ModuleType('faster_whisper')
        module.WhisperModel = MagicMock(return_value=model)
        return module, model

    def run_main(self, args):
        with redirect_stdout(self.stdout), redirect_stderr(self.stderr):
            return asr.main(args)

    def test_local_audio_preserves_words_metadata_and_unknown_speakers(self):
        consumed = []
        def segments():
            consumed.append('started')
            yield types.SimpleNamespace(id=0, start=0.25, end=1.75,
                                        text=' Huerta de Soto: 15.000 € y 2 % ', tokens=[1, 2], no_speech_prob=0.01)
            yield types.SimpleNamespace(id=1, start=1.75, end=3.0, text='No es un dato verificado.')
            consumed.append('finished')
        module, model = self.fake_module(segments())
        with patch.dict(sys.modules, {'faster_whisper': module}), patch.object(asr.collect, 'enable_tls'), \
             patch.object(asr.collect, 'store_transcript', wraps=asr.collect.store_transcript) as store:
            self.assertEqual(self.run_main(self.args()), 0)
        self.assertEqual(consumed, ['started', 'finished'])
        module.WhisperModel.assert_called_once_with('small', device='cpu', compute_type='int8', local_files_only=True)
        model.transcribe.assert_called_once_with(str(self.audio.resolve()), language='es', beam_size=5, vad_filter=True)
        self.assertEqual(store.call_args.args[-1], 'local_asr')
        folder = self.out / 'videos' / VIDEO
        original = asr.collect.load(folder / 'transcript.original.json')
        normalized = asr.collect.load(folder / 'transcript.json')
        self.assertEqual(original['segments'][0]['text'], ' Huerta de Soto: 15.000 € y 2 % ')
        self.assertEqual(original['segments'][0]['tokens'], [1, 2])
        self.assertEqual(original['segments'][0]['duration'], 1.5)
        self.assertEqual(normalized['segments'][0]['text'], 'Huerta de Soto: 15.000 € y 2 %')
        self.assertEqual(normalized['method'], 'local_asr')
        self.assertTrue(normalized['isGenerated'])
        self.assertFalse(normalized['numbersVerified'])
        self.assertFalse(normalized['namesVerified'])
        self.assertFalse(normalized['speakerNamesVerified'])
        self.assertFalse(normalized['diarizationPerformed'])
        self.assertTrue(all(s['speaker'] is None and s['attribution'] == 'unreviewed' for s in normalized['segments']))
        run = asr.collect.load(folder / 'asr-run.json')
        self.assertEqual(run['audioSha256'], hashlib.sha256(self.audio.read_bytes()).hexdigest())
        catalog = asr.collect.load(self.out / 'catalog.json')
        self.assertEqual(catalog[1], self.other)
        self.assertEqual(catalog[0]['title'], self.base['title'])
        self.assertEqual(catalog[0]['channel'], self.base['channel'])
        self.assertEqual(catalog[0]['topicsRequested'], ['dinero'])
        self.assertEqual(catalog[0]['asrStatus'], 'completed')
        self.assertEqual(catalog[0]['previousCollectionError']['type'], 'IpBlocked')
        self.assertEqual(catalog[0]['analysisStatus'], 'pending')
        self.assertTrue((folder / 'transcript.txt').read_text(encoding='utf-8').startswith('[s00001 | 00:00:00]'))

    def test_existing_transcript_is_preserved_without_model_or_download(self):
        existing = {'segments': [{'text': 'Pista ya disponible'}], 'method': 'youtube-transcript-api'}
        path = self.out / 'videos' / VIDEO / 'transcript.json'
        asr.collect.save(path, existing)
        with patch.dict(sys.modules, {'faster_whisper': None}), patch.object(asr, 'download_audio') as download:
            self.assertEqual(self.run_main(self.args()), 0)
        self.assertEqual(asr.collect.load(path), existing)
        download.assert_not_called()
        self.assertEqual(json.loads(self.stdout.getvalue())['status'], 'skipped_existing')

    def test_missing_audio_does_not_create_success_or_fake_transcript(self):
        self.audio.unlink()
        with patch.dict(sys.modules, {'faster_whisper': None}):
            self.assertEqual(self.run_main(self.args()), 2)
        row = asr.collect.load(self.out / 'catalog.json')[0]
        self.assertEqual(row['transcriptStatus'], 'blocked')
        self.assertEqual(row['asrStatus'], 'error')
        self.assertEqual(row['asrError']['type'], 'FileNotFoundError')
        self.assertFalse((self.out / 'videos' / VIDEO / 'transcript.json').exists())

    def test_missing_optional_dependency_reports_error_without_installing(self):
        with patch.dict(sys.modules, {'faster_whisper': None}):
            self.assertEqual(self.run_main(self.args()), 2)
        self.assertIn('faster-whisper no está instalado', self.stderr.getvalue())
        self.assertFalse((self.out / 'videos' / VIDEO / 'transcript.json').exists())

    def test_empty_asr_output_is_not_counted_as_transcribed(self):
        module, _ = self.fake_module(iter([]))
        with patch.dict(sys.modules, {'faster_whisper': module}), patch.object(asr.collect, 'enable_tls'):
            self.assertEqual(self.run_main(self.args()), 2)
        self.assertIn('no produjo voz', self.stderr.getvalue())
        self.assertFalse((self.out / 'videos' / VIDEO / 'transcript.json').exists())

    def test_invalid_timestamp_is_rejected_before_storing(self):
        bad = types.SimpleNamespace(start=float('nan'), end=1.0, text='No inventar un tiempo.')
        with self.assertRaisesRegex(ValueError, 'intervalo'):
            asr.raw_segments([bad])
        with self.assertRaisesRegex(ValueError, 'intervalo'):
            asr.raw_segments([types.SimpleNamespace(start=4, end=3, text='No invertir el tiempo.')])

    def test_download_uses_collector_tls_options_and_preserves_request_metadata(self):
        folder = self.out / 'videos' / VIDEO
        folder.mkdir(parents=True)
        target = folder / 'audio.webm'
        target.write_bytes(b'fixture')
        info = {'id': VIDEO, 'title': 'Título recuperado', 'channel': 'Canal recuperado',
                'channel_id': 'UCrecovered', 'channel_url': 'https://www.youtube.com/channel/UCrecovered',
                'duration': 123, 'requested_downloads': [{'filepath': str(target)}]}
        downloader = MagicMock()
        downloader.extract_info.return_value = info
        module = types.ModuleType('yt_dlp')
        module.YoutubeDL = MagicMock()
        module.YoutubeDL.return_value.__enter__.return_value = downloader
        row = asr.catalog_row(self.out, VIDEO)
        base_options = {'quiet': True, 'skip_download': True, 'retries': 1,
                        'js_runtimes': {'node': {'path': 'node.exe'}}, 'cookiefile': 'not-used', 'proxy': 'not-used'}
        with patch.dict(sys.modules, {'yt_dlp': module}), patch.object(asr.collect, 'enable_tls') as tls, \
             patch.object(asr.collect, 'youtube_options', return_value=base_options):
            actual = asr.download_audio(self.out, row)
        self.assertEqual(actual, target.resolve())
        tls.assert_called_once()
        options = module.YoutubeDL.call_args.args[0]
        self.assertFalse(options['skip_download'])
        self.assertFalse(options['nocheckcertificate'])
        self.assertTrue(options['noplaylist'])
        self.assertEqual(options['format'], 'bestaudio/best')
        self.assertEqual(options['js_runtimes'], {'node': {'path': 'node.exe'}})
        self.assertNotIn('cookiefile', options)
        self.assertNotIn('proxy', options)
        downloader.extract_info.assert_called_once_with(row['url'], download=True)
        self.assertEqual(row['title'], 'Título recuperado')
        self.assertEqual(row['channel']['id'], 'UCrecovered')
        self.assertEqual(row['topicsRequested'], ['dinero'])
        self.assertEqual(row['metadata']['source'], 'yt-dlp:audio')

    def test_partial_download_metadata_does_not_erase_known_channel_or_title(self):
        folder = self.out / 'videos' / VIDEO
        folder.mkdir(parents=True)
        target = folder / 'audio.webm'
        target.write_bytes(b'fixture')
        module = types.ModuleType('yt_dlp')
        downloader = MagicMock()
        downloader.extract_info.return_value = {'id': VIDEO, 'requested_downloads': [{'filepath': str(target)}]}
        module.YoutubeDL = MagicMock()
        module.YoutubeDL.return_value.__enter__.return_value = downloader
        row = asr.catalog_row(self.out, VIDEO)
        with patch.dict(sys.modules, {'yt_dlp': module}), patch.object(asr.collect, 'enable_tls'):
            asr.download_audio(self.out, row)
        self.assertEqual(row['title'], self.base['title'])
        self.assertEqual(row['channel'], self.base['channel'])
        self.assertEqual(row['requestContexts'], ['Contexto solicitado'])

    def test_download_rejects_mismatched_id_and_audio_outside_its_folder(self):
        module = types.ModuleType('yt_dlp')
        downloader = MagicMock()
        module.YoutubeDL = MagicMock()
        module.YoutubeDL.return_value.__enter__.return_value = downloader
        downloader.extract_info.return_value = {'id': OTHER}
        with patch.dict(sys.modules, {'yt_dlp': module}), patch.object(asr.collect, 'enable_tls'):
            with self.assertRaisesRegex(ValueError, 'ID'):
                asr.download_audio(self.out, self.base.copy())
            downloader.extract_info.return_value = {'id': VIDEO, 'requested_downloads': [{'filepath': str(self.audio)}]}
            with self.assertRaisesRegex(ValueError, 'carpeta'):
                asr.download_audio(self.out, self.base.copy())

    def test_unknown_video_keeps_channel_and_title_unverified(self):
        new_id = 'ECioYubkBpo'
        row = asr.catalog_row(self.out, new_id)
        self.assertEqual(row['id'], new_id)
        self.assertIsNone(row['title'])
        self.assertIsNone(row['channel']['name'])
        self.assertEqual(row['metadata']['status'], 'pending')
        self.assertEqual(row['speakers'], [])

    def test_cli_requires_safe_id_and_exactly_one_source(self):
        for args in (['--video-id', '../escape', '--audio', str(self.audio)],
                     ['--video-id', VIDEO],
                     ['--video-id', VIDEO, '--audio', str(self.audio), '--download-audio']):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                asr.parser().parse_args(args)
        args = asr.parser().parse_args(['--video-id', VIDEO, '--download-audio', '--model', 'base', '--device', 'cuda'])
        self.assertTrue(args.download_audio)
        self.assertEqual(args.compute_type, 'int8')


if __name__ == '__main__':
    unittest.main()
