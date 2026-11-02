"""Download approved media without replacing existing files with bad data."""
from io import BytesIO
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from release_support import json_bytes, metadata
from fetch_story_media import download_media


class Response(BytesIO):
    def __init__(self, payload, url='https://mitomapacanario.org/media/isla/cuento.mp4'):
        super().__init__(payload)
        self.url = url

    def geturl(self):
        return self.url


class FetchStoryMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = 'media/isla/cuento.mp4'
        self.payload = b'approved movie bytes'
        (self.root / 'MEDIA_MANIFEST.json').write_bytes(json_bytes({
            'version': 1, 'files': {self.name: metadata(self.payload)}}))

    def test_valid_download_is_installed_with_exact_pinned_bytes(self):
        calls = []
        def opener(request, timeout):
            calls.append(request.full_url)
            return Response(self.payload)
        self.assertEqual(download_media(self.root, opener=opener), 1)
        self.assertEqual((self.root / self.name).read_bytes(), self.payload)
        self.assertEqual(calls, ['https://crgarsan.github.io/mitomapa-canario/' + self.name])

    def test_bad_hash_preserves_existing_media_and_removes_temporary_file(self):
        target = self.root / self.name
        target.parent.mkdir(parents=True)
        target.write_bytes(b'old media')
        with self.assertRaises(ValueError):
            download_media(self.root, opener=lambda request, timeout: Response(b'x' * len(self.payload)))
        self.assertEqual(target.read_bytes(), b'old media')
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_default_source_restores_pinned_html_without_hosting_additions(self):
        name = 'media/fuentes-cuentos.html'
        payload = b'<!doctype html><title>Story sources</title>'
        (self.root / 'MEDIA_MANIFEST.json').write_bytes(json_bytes({
            'version': 1, 'files': {name: metadata(payload)}}))
        def opener(request, timeout):
            if request.full_url == 'https://crgarsan.github.io/mitomapa-canario/' + name:
                return Response(payload, request.full_url)
            return Response(payload + b'<script>hosting addition</script>', request.full_url)
        self.assertEqual(download_media(self.root, opener=opener), 1)
        self.assertEqual((self.root / name).read_bytes(), payload)

    def test_oversized_response_is_rejected_before_replacing_file(self):
        with self.assertRaises(ValueError):
            download_media(self.root, opener=lambda request, timeout: Response(self.payload + b'extra'))
        self.assertFalse((self.root / self.name).exists())

    def test_https_cannot_be_downgraded_by_base_url_or_redirect(self):
        for base in ['http://mitomapacanario.org/', 'https://user:password@example.com/']:
            with self.subTest(base=base), self.assertRaises(ValueError):
                download_media(self.root, base_url=base, opener=lambda *a, **kw: self.fail('network called'))
        with self.assertRaises(ValueError):
            download_media(self.root, opener=lambda request, timeout: Response(self.payload, 'http://example.com/file'))

    def test_symbolic_link_target_is_not_followed(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'media').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            download_media(self.root, opener=lambda *a, **kw: self.fail('network called'))
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
