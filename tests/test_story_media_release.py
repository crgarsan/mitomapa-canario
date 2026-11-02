"""Public story media must be pinned without bloating the source-code archive."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from release_support import MAX_ASSET_BYTES, digest, json_bytes, metadata, parse_sums, read_zip
from update_release import check_release, update_release
from prepare_deploy import stage_assets
import test_release_pipeline as release_fixtures


class StoryPdfSourceTests(unittest.TestCase):
    def test_pdf_source_links_match_published_pages_and_island_anchors(self):
        data = (ROOT / 'formatos-data.js').read_text()
        books = json.loads(data.split('=', 1)[1].strip().rstrip(';'))['books']

        class PageIds(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = set()

            def handle_starttag(self, tag, attributes):
                self.ids.update(value for key, value in attributes if key == 'id')

        def unescape(match):
            value = match.group(1)
            return bytes([int(value, 8)]) if value.isdigit() else value

        self.assertEqual(len(books), 8)
        for book in books:
            with self.subTest(island=book['slug']):
                target = book['sources']['full_source_url']
                url = urlsplit(target)
                self.assertEqual(url.scheme, 'https')
                self.assertEqual(url.netloc, 'mitomapacanario.org')
                self.assertEqual(url.path, '/FUENTES_CUENTOS.html')
                self.assertEqual(url.fragment, 'fuentes-' + book['slug'])
                page = ROOT / url.path.lstrip('/')
                parser = PageIds()
                parser.feed(page.read_text())
                self.assertIn(url.fragment, parser.ids)

                # These published PDFs keep their URI actions in literal strings.
                # Decode PDF octal escapes as well as ordinary ASCII URLs.
                pdf = (ROOT / book['pdf']).read_bytes()
                strings = re.findall(rb'/URI\s*\(((?:\\.|[^\\()])*)\)', pdf)
                uris = [re.sub(rb'\\([0-7]{1,3}|.)', unescape, value).decode('ascii')
                        for value in strings]
                self.assertIn(target, uris)
                self.assertFalse(any('/documentacion/FUENTES_CUENTOS.html' in uri for uri in uris))


class StoryMediaReleaseTests(unittest.TestCase):
    def setUp(self):
        self.fixture = release_fixtures.ReleasePipelineTests('test_packages_preserve_history_and_check_is_read_only')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.version = self.fixture.version

    def add_media(self):
        self.payload = b'public story movie fixture'
        self.name = 'media/la-palma/cuento.mp4'
        self.fixture.write(self.name, self.payload)
        self.manifest = {'version': 1, 'files': {self.name: metadata(self.payload)}}
        self.fixture.write('MEDIA_MANIFEST.json', json_bytes(self.manifest))

    def test_pinned_media_is_published_and_source_archive_explains_separate_download(self):
        self.add_media()
        update_release(self.root)
        public = parse_sums((self.root / 'SHA256SUMS.txt').read_text())
        self.assertIn(self.name, public)
        self.assertEqual(public[self.name], digest(self.payload))
        self.assertIn('MEDIA_MANIFEST.json', public)
        stage_assets(self.root, self.root / '.deploy')
        self.assertEqual((self.root / '.deploy' / self.name).read_bytes(), self.payload)
        sources = read_zip((self.root / self.version['source_archive']['path']).read_bytes())
        self.assertIn('MEDIA_MANIFEST.json', sources)
        self.assertNotIn(self.name, sources)
        self.assertIn('medios', sources['FUENTES_WEB_LEEME.txt'].decode().lower())
        self.assertIn('fetch_story_media.py', sources['FUENTES_WEB_LEEME.txt'].decode())
        check_release(self.root)

    def test_unlisted_drafts_are_not_published(self):
        self.add_media()
        self.fixture.write('media/la-palma/draft.wav', b'not approved')
        update_release(self.root)
        self.assertNotIn('media/la-palma/draft.wav', parse_sums((self.root / 'SHA256SUMS.txt').read_text()))

    def test_source_archive_includes_backup_recovery_instructions(self):
        self.add_media()
        self.fixture.write('docs/RESPALDO.md', b'Independent recovery instructions')
        update_release(self.root)
        sources = read_zip((self.root / self.version['source_archive']['path']).read_bytes())
        self.assertEqual(sources['docs/RESPALDO.md'], b'Independent recovery instructions')

    def test_stale_media_hash_stops_release_before_writing(self):
        self.add_media()
        self.fixture.write(self.name, b'changed movie')
        before = self.fixture.snapshot()
        with self.assertRaises(ValueError):
            update_release(self.root)
        self.assertEqual(self.fixture.snapshot(), before)

    def test_traversal_in_media_manifest_is_rejected(self):
        self.add_media()
        self.manifest['files'] = {'media/../index.html': metadata((self.root / 'index.html').read_bytes())}
        self.fixture.write('MEDIA_MANIFEST.json', json_bytes(self.manifest))
        with self.assertRaises(ValueError):
            update_release(self.root)

    def test_declared_oversize_media_is_rejected(self):
        self.add_media()
        self.manifest['files'][self.name]['bytes'] = MAX_ASSET_BYTES + 1
        self.fixture.write('MEDIA_MANIFEST.json', json_bytes(self.manifest))
        with self.assertRaises(ValueError):
            update_release(self.root)

    def test_manifest_cannot_publish_files_outside_media(self):
        self.add_media()
        self.manifest['files'] = {'index.html': metadata((self.root / 'index.html').read_bytes())}
        self.fixture.write('MEDIA_MANIFEST.json', json_bytes(self.manifest))
        with self.assertRaises(ValueError):
            update_release(self.root)


if __name__ == '__main__':
    unittest.main()
