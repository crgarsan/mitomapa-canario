"""Download approved media without replacing existing files with bad data."""
from email.message import Message
from io import BytesIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import BaseHandler
from urllib.response import addinfourl

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

    def test_redirects_are_rejected_before_any_follow_on_request(self):
        target = self.root / self.name
        target.parent.mkdir(parents=True)
        initial_url = 'https://crgarsan.github.io/mitomapa-canario/' + self.name
        for code in [300, 301, 302, 303, 304, 305, 306, 307, 308, 399]:
            for destination in [
                    'http://127.0.0.1:9/', 'https://127.0.0.1:9/',
                    'https://169.254.169.254/latest/meta-data/', 'https://10.0.0.1/',
                    'https://other.example/media.mp4', initial_url + '.redirected',
                    '/media/elsewhere.mp4']:
                with self.subTest(code=code, destination=destination):
                    target.write_bytes(b'old media')
                    seen = []
                    payload = self.payload

                    class MediaTransport(BaseHandler):
                        handler_order = 1

                        def https_open(self, request):
                            seen.append(request.full_url)
                            headers = Message()
                            headers['Location'] = destination
                            response = addinfourl(BytesIO(payload), headers, request.full_url,
                                                  code if len(seen) == 1 else 200)
                            response.msg = 'Redirect' if len(seen) == 1 else 'OK'
                            return response
                        http_open = https_open

                    error = None
                    # Replace only network I/O; retain the real urllib redirect stack.
                    with patch('urllib.request._opener', None), \
                            patch('urllib.request.HTTPSHandler', MediaTransport):
                        try:
                            download_media(self.root)
                        except (HTTPError, ValueError) as caught:
                            error = caught
                            if isinstance(error, HTTPError):
                                error.close()
                    self.assertEqual(seen, [initial_url], 'A redirect must never issue another request')
                    self.assertIsInstance(error, HTTPError)
                    self.assertEqual(error.code, code)
                    self.assertEqual(target.read_bytes(), b'old media')
                    self.assertEqual(list(target.parent.iterdir()), [target])

    def test_default_transport_installs_pinned_bytes_from_direct_https_mirror(self):
        seen = []
        payload = self.payload

        class MediaTransport(BaseHandler):
            handler_order = 1

            def https_open(self, request):
                seen.append(request.full_url)
                response = addinfourl(BytesIO(payload), Message(), request.full_url, 200)
                response.msg = 'OK'
                return response

        with patch('urllib.request._opener', None), \
                patch('urllib.request.HTTPSHandler', MediaTransport):
            self.assertEqual(download_media(self.root, base_url='https://mirror.example/stories/'), 1)
        self.assertEqual(seen, ['https://mirror.example/stories/' + self.name])
        self.assertEqual((self.root / self.name).read_bytes(), self.payload)

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
