"""Exercise the public backup artifact with a complete, small release fixture."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / 'tools/prepare_backup.py'


class BackupStageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        self.stage = self.root / '.backup'
        self.files = {
            'index.html': '<html><head><title>MitoMapa</title></head><body><h1>MitoMapa Canario</h1><video src="/media/isla/cuento.mp4"></video><a href="downloads/current.elpx">Actual</a><a href="downloads/historical.elpx">Anterior</a><script src="/app.js"></script></body></html>',
            'app.js': 'const film="/media/isla/cuento.mp4";const old="../downloads/historical.elpx";',
            'style.css': 'body{background:url(/assets/picture.webp)}',
            'assets/picture.webp': b'preserved-image',
            'media/isla/cuento.mp4': b'preserved-aac-and-pixels',
            'media/isla/cuento.pdf': b'preserved-pdf',
            'media/fuentes.html': b'<a href="/assets/picture.webp">Fuente</a>',
            'downloads/current.elpx': b'current-rea',
            'downloads/sharing.zip': b'current-sharing',
            'downloads/source.zip': b'current-sources',
            'downloads/Cuaderno_de_ruta_MitoMapa.html': '<html>Cuaderno actual</html>',
            'downloads/Pauta_de_revision_MitoMapa.html': '<html>Pauta actual</html>',
            'downloads/Pauta_de_revision_MitoMapa.csv': 'criterio,observaciones\nDialoga,\n',
            'downloads/historical.elpx': b'private-historical-copy',
            'tools/secret.py': 'not public',
            'tests/example.json': '{}',
            'QA/report.json': '{}',
            '.old/index.html': 'old version',
            '.env': 'TOKEN=must-not-publish',
            'credentials.json': '{"token":"must-not-publish"}',
        }
        self.files['VERSION.json'] = json.dumps({
            'web_version': '4.9.2', 'rea_exelearning_version': '4.8.8',
            'download': {'path': 'downloads/current.elpx'},
            'sharing_archive': {'path': 'downloads/sharing.zip'},
            'source_archive': {'path': 'downloads/source.zip'},
            'presets': [{'path': 'downloads/historical.elpx'}],
        })
        self.files['formatos.js'] = (SCRIPT.parent.parent / 'formatos.js').read_text()
        self.files['MEDIA_MANIFEST.json'] = json.dumps({'version': 1, 'files': {
            name: {'sha256': sha256(payload).hexdigest(), 'bytes': len(payload)}
            for name, payload in self.files.items() if name.startswith('media/')
        }})
        self.write_fixture()

    def write_fixture(self):
        for name, payload in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload.encode() if isinstance(payload, str) else payload)
        sums = ''.join(f'{sha256((self.root / name).read_bytes()).hexdigest()}  {name}\n' for name in sorted(self.files))
        (self.root / 'SHA256SUMS.txt').write_text(sums)

    def run_stage(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
            '--output', str(self.stage), '--primary-url', 'https://primary.example/',
            '--base-path', '/backup-repo/', '--source-commit', 'a'*40, *extra],
            text=True, capture_output=True)

    def test_stage_excludes_history_and_private_files_but_keeps_runtime_media(self):
        # Regressions caught: copying all downloads or rewriting media to primary.
        original = (self.root / 'index.html').read_bytes()
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.stage / 'media/isla/cuento.mp4').read_bytes(), b'preserved-aac-and-pixels')
        self.assertEqual((self.stage / 'media/isla/cuento.pdf').read_bytes(), b'preserved-pdf')
        downloads = sorted(p.name for p in (self.stage / 'downloads').iterdir())
        self.assertEqual(downloads, ['Cuaderno_de_ruta_MitoMapa.html', 'Pauta_de_revision_MitoMapa.csv',
            'Pauta_de_revision_MitoMapa.html', 'current.elpx', 'sharing.zip', 'source.zip'])
        for private in ['tools', 'tests', 'QA', '.old', '.env', 'credentials.json']:
            self.assertFalse((self.stage / private).exists(), private)
        html = (self.stage / 'index.html').read_text()
        self.assertIn('src="/backup-repo/media/isla/cuento.mp4"', html)
        self.assertIn('href="https://primary.example/downloads/historical.elpx"', html)
        self.assertIn('href="downloads/current.elpx"', html)
        self.assertIn('Copia de respaldo', html)
        self.assertNotIn('http-equiv="refresh"', html)
        self.assertIn('"/backup-repo/media/isla/cuento.mp4"', (self.stage / 'app.js').read_text())
        self.assertIn('"https://primary.example/downloads/historical.elpx"', (self.stage / 'app.js').read_text())
        self.assertIn('url(/backup-repo/assets/picture.webp)', (self.stage / 'style.css').read_text())
        self.assertEqual((self.root / 'index.html').read_bytes(), original)

    def test_backup_inventory_checksums_cover_the_actual_rewritten_artifact(self):
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.stage / 'BACKUP_MANIFEST.json').read_text())
        self.assertEqual(manifest['source_commit'], 'a'*40)
        self.assertEqual(manifest['primary_url'], 'https://primary.example/')
        self.assertEqual(manifest['web_version'], '4.9.2')
        self.assertEqual(len(manifest['current_downloads']), 3)
        entries = dict(line.split('  ', 1)[::-1] for line in (self.stage / 'SHA256SUMS.txt').read_text().splitlines())
        actual = {p.relative_to(self.stage).as_posix() for p in self.stage.rglob('*') if p.is_file()}
        self.assertEqual(set(entries), actual - {'SHA256SUMS.txt'})
        for name, expected in entries.items():
            self.assertEqual(sha256((self.stage / name).read_bytes()).hexdigest(), expected, name)

    def test_media_mismatch_fails_before_replacing_an_existing_backup(self):
        self.stage.mkdir(); (self.stage / 'previous.txt').write_text('keep me')
        self.files['media/isla/cuento.mp4'] = b'tampered-media'
        self.write_fixture()  # Main sums match, but independent media pin does not.
        result = self.run_stage()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('media', result.stderr.lower())
        self.assertEqual((self.stage / 'previous.txt').read_text(), 'keep me')

    def test_size_limit_fails_without_leaving_a_partial_backup(self):
        result = self.run_stage('--max-bytes', '100')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('size', result.stderr.lower())
        self.assertFalse(self.stage.exists())

    def test_symlink_cannot_escape_the_release_root(self):
        target = self.root / 'assets/picture.webp'; target.unlink()
        secret = Path(self.temp.name) / 'outside'; secret.write_bytes(b'preserved-image')
        target.symlink_to(secret)
        result = self.run_stage()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symbolic', result.stderr.lower())
        self.assertFalse(self.stage.exists())

    def test_http_probe_is_rejected_without_network_access(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--verify-url', 'http://example.invalid/'], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('https', result.stderr.lower())

    def test_staged_media_manifest_matches_a_rebased_media_html_page(self):
        # Regressions caught: rebase a pinned media HTML file but leave stale pins.
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        page = (self.stage / 'media/fuentes.html').read_bytes()
        self.assertIn(b'/backup-repo/assets/picture.webp', page)
        manifest = json.loads((self.stage / 'MEDIA_MANIFEST.json').read_text())
        self.assertEqual(manifest['files']['media/fuentes.html'], {
            'sha256': sha256(page).hexdigest(), 'bytes': len(page)})

    def test_output_symlink_never_replaces_an_unrelated_directory(self):
        outside = Path(self.temp.name) / 'unrelated'; outside.mkdir()
        (outside / 'keep.txt').write_text('untouched')
        self.stage.symlink_to(outside, target_is_directory=True)
        result = self.run_stage()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symbolic', result.stderr.lower())
        self.assertEqual((outside / 'keep.txt').read_text(), 'untouched')

    def test_https_probe_requires_artifact_identity_before_contacting_the_network(self):
        # A self-consistent replacement page must not certify itself as our build.
        sys.path.insert(0, str(SCRIPT.parent))
        import prepare_backup
        with patch.object(prepare_backup, 'urlopen', side_effect=AssertionError('network must not run')):
            with self.assertRaisesRegex(ValueError, 'Expected.*commit.*manifest'):
                prepare_backup.verify_publication('https://example.invalid/')

    def test_http_200_block_page_cannot_pass_expected_content_verification(self):
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        sys.path.insert(0, str(SCRIPT.parent))
        import prepare_backup
        manifest = (self.stage / 'BACKUP_MANIFEST.json').read_bytes()
        def response(request, timeout):
            payload = manifest if request.full_url.endswith('/BACKUP_MANIFEST.json') else b'<html>Access blocked</html>'
            stream = BytesIO(payload)
            stream.status = 200
            stream.url = request.full_url
            return stream
        # Only the HTTP boundary is replaced; real manifest and content hashes run.
        with patch.object(prepare_backup, 'urlopen', side_effect=response):
            with self.assertRaisesRegex(ValueError, 'content mismatch: index.html'):
                prepare_backup.verify_publication('https://backup.example/backup-repo/',
                    expected_commit='a'*40, expected_manifest_sha=sha256(manifest).hexdigest())

    def test_current_teacher_materials_remain_included_and_linked_locally(self):
        names = ['downloads/Cuaderno_de_ruta_MitoMapa.html',
                 'downloads/Pauta_de_revision_MitoMapa.html',
                 'downloads/Pauta_de_revision_MitoMapa.csv']
        self.files['index.html'] += ''.join('<a href="' + name + '">Material docente</a>' for name in names)
        self.write_fixture()
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = (self.stage / 'index.html').read_text()
        for name in names:
            self.assertTrue((self.stage / name).is_file(), name)
            self.assertEqual((self.stage / name).read_bytes(), (self.root / name).read_bytes())
            self.assertIn('href="' + name + '"', staged)
            self.assertNotIn('href="https://primary.example/' + name + '"', staged)

    def test_pintadera_viewer_keeps_relative_paths_under_the_pages_prefix(self):
        name = 'pintaderas-visor.js'
        module = (SCRIPT.parent.parent / name).read_bytes()
        self.files[name] = module
        self.write_fixture()
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.stage / name).read_bytes(), module)

    def test_pintadera_downloads_stay_on_the_independent_backup(self):
        prefix = 'downloads/pintaderas-3d'
        slugs = ('chevron', 'circulos', 'dentada', 'doble_triangulo', 'espiral_cuadrada',
                 'rombos', 'roseta', 'seis_triangulos', 'sol', 'triangulo')
        models = {}
        for group in ('recreaciones', 'sellos'):
            models[f'{prefix}/{group}.zip'] = b'example archive for staging'
            for slug in slugs:
                models[f'{prefix}/{group}/pintadera_{slug}.stl'] = f'{group} {slug}'.encode()
        self.files.update(models)
        self.files['PINTADERAS_3D.json'] = json.dumps({'version': 1, 'files': {
            name: {'sha256': sha256(payload).hexdigest(), 'bytes': len(payload)}
            for name, payload in models.items()
        }})
        self.files['index.html'] += ''.join(f'<a href="{name}" download>Descargar</a>' for name in models)
        self.write_fixture()
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = (self.stage / 'index.html').read_text()
        for name, payload in models.items():
            self.assertEqual((self.stage / name).read_bytes(), payload)
            self.assertIn(f'href="{name}" download', staged)

    def test_vasija_download_and_viewer_stay_local_under_the_pages_prefix(self):
        model = 'downloads/vasija/vasija_canaria.stl'
        unrelated = 'downloads/vasija/otro_modelo.stl'
        viewer = 'vasija-visor.js'
        module = (SCRIPT.parent.parent / viewer).read_bytes()
        self.files.update({
            model: b'example binary model',
            unrelated: b'not selected for release',
            viewer: module,
            'pintaderas-visor.css': b'/* viewer layout */',
            'assets/vasija/ficha.json': '{}',
            'assets/vasija/vistas.webp': b'example fallback image',
        })
        collection = {'downloads/vasijas/coleccion.zip': b'example collection archive'}
        for slug in ('gran-canaria', 'la-palma', 'lanzarote', 'fuerteventura', 'la-gomera', 'el-hierro'):
            collection[f'downloads/vasijas/{slug}.stl'] = slug.encode()
            self.files[f'assets/vasijas/{slug}.webp'] = b'example fallback image'
        self.files['assets/vasijas/coleccion.json'] = '[]'
        self.files.update(collection)
        self.files['downloads/vasijas/otro_modelo.stl'] = b'not selected for release'
        self.files['index.html'] += ''.join(
            f'<a href="{name}" download>Descargar</a>' for name in (model, *collection)
        )
        self.write_fixture()

        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.stage / model).read_bytes(), self.files[model])
        self.assertEqual((self.stage / viewer).read_bytes(), module)
        self.assertIn(f'href="{model}" download', (self.stage / 'index.html').read_text())
        for name, payload in collection.items():
            self.assertEqual((self.stage / name).read_bytes(), payload)
            self.assertIn(f'href="{name}" download', (self.stage / 'index.html').read_text())
        self.assertFalse((self.stage / unrelated).exists())
        self.assertFalse((self.stage / 'downloads/vasijas/otro_modelo.stl').exists())

    def test_staged_safe_local_url_preserves_slash_splitting_and_rejects_traversal(self):
        node = shutil.which('node')
        if node is None:
            bundled = Path(sys.executable).resolve().parents[2] / 'node/bin/node'
            node = str(bundled) if bundled.is_file() else None
        self.assertIsNotNone(node, 'Node.js is required by this repository security regression test')
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = self.stage / 'formatos.js'
        self.assertIn("decoded.split('/')", staged.read_text())
        probe = "const f=require(process.argv[1]);process.stdout.write(JSON.stringify(['media/isla/cuento.mp4','media/../bad.mp4','media/%2e%2e/bad.mp4'].map(f.safeLocalURL)));"
        result = subprocess.run([node, '-e', probe, str(staged)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ['media/isla/cuento.mp4', '', ''])


if __name__ == '__main__':
    unittest.main()
