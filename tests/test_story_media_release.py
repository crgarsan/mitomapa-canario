"""Public story media must be pinned without bloating the source-code archive."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from release_support import MAX_ASSET_BYTES, digest, json_bytes, metadata, parse_sums, read_zip
from update_release import check_release, update_release
from prepare_deploy import stage_assets
import test_release_pipeline as release_fixtures


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
