"""Public transport must be verified independently of Cloudflare API access."""
import importlib.util
import io
import json
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError
import unittest

ROOT = Path(__file__).resolve().parent.parent
VERSION_URL = 'https://mitomapacanario.org/VERSION.json'
VALID_VERSION = {
    'web_version': '4.9.1',
    'download': {
        'path': 'downloads/MitoMapa_canario_GobCan.elpx',
        'sha256': 'cedaa18b42271e02547847800a8fd8a7094ccf9a021892942f5370a3dc25a477',
    },
}
VALID_BODY = json.dumps(VALID_VERSION).encode('utf-8')


class Reply:
    def __init__(self, status=200, headers=None, body=b'', url=None):
        self.status = status
        self.url = url
        self.body = io.BytesIO(body)
        self.headers = Message()
        for name, value in (headers or {}).items():
            self.headers.add_header(name, value)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def geturl(self):
        return self.url

    def read(self, size):
        if not 0 < size <= 65536:
            raise AssertionError('Manifest reads must be bounded to at most 64 KiB')
        return self.body.read(size)


class PublicTransportTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'tools/check_public_transport.py'
        self.assertTrue(path.is_file(), 'Missing mandatory public HTTPS verification')
        spec = importlib.util.spec_from_file_location('public_transport', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def opener(self, mutation=None):
        module = self.module
        class Fake:
            requests = []
            def open(self, request, timeout):
                self.requests.append(request)
                url = request.full_url
                expected_method = 'GET' if url == VERSION_URL else 'HEAD'
                if request.get_method() != expected_method or timeout != 15:
                    raise AssertionError('Use bounded HEAD probes and one fixed GET manifest request')
                if any(name.lower() in {'authorization', 'cookie'} for name in request.headers):
                    raise AssertionError('Public probes must not carry credentials')
                if url == VERSION_URL:
                    reply = Reply(200, {'Content-Type': 'application/json; charset=utf-8'}, VALID_BODY, url)
                    return mutation(url, reply) if mutation else reply
                if not any(url == scheme + path for scheme in ('http://'+module.HOSTNAME, 'https://'+module.HOSTNAME) for path in module.PROBE_PATHS):
                    raise AssertionError('Only fixed public URLs may be probed')
                reply = (Reply(301, {'Location': 'https://' + url[len('http://'):]})
                         if url.startswith('http://') else
                         Reply(200, {'Strict-Transport-Security': 'max-age=31536000'}))
                return mutation(url, reply) if mutation else reply
        return Fake()

    def test_manual_redirect_passes_without_cloudflare_api_or_credentials(self):
        opener = self.opener()
        result = self.module.check_transport(opener=opener)
        self.assertEqual(len(result), 5)
        self.assertEqual(len(opener.requests), 5)
        self.assertEqual(result[-1]['web_version'], '4.9.1', 'A valid previous release must pass before publication')
        self.assertTrue(any('?' in r.full_url and '/downloads/' in r.full_url for r in opener.requests))

    def test_http_success_is_rejected_instead_of_accepting_published_cleartext(self):
        opener = self.opener(lambda url, reply: Reply(200) if url.startswith('http://') else reply)
        with self.assertRaises(self.module.TransportError):
            self.module.check_transport(opener=opener)

    def test_redirect_must_preserve_exact_host_path_and_query(self):
        for location in ('http://mitomapacanario.org/', 'https://example.com/',
                         'https://mitomapacanario.org/', '/relative',
                         'https://mitomapacanario.org/downloads/MitoMapa_canario_GobCan.elpx',
                         'https://mitomapacanario.org.evil.invalid/',
                         'https://mitomapacanario.org@evil.invalid/'):
            with self.subTest(location=location):
                def change(url, reply):
                    if url.startswith('http://') and '/downloads/' in url:
                        return Reply(301, {'Location': location})
                    return reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

    def test_temporary_or_missing_redirect_is_rejected(self):
        for status in (200, 302, 307, 404, 500):
            with self.subTest(status=status):
                change = lambda url, reply: Reply(status, {'Location': 'https://' + url[len('http://'):]}) if url.startswith('http://') else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

    def test_permanent_308_redirect_is_accepted(self):
        def change(url, reply):
            if url.startswith('http://'):
                reply.status = 308
            return reply
        self.assertEqual(len(self.module.check_transport(opener=self.opener(change))), 5)

    def test_https_must_succeed_and_keep_host_hsts(self):
        for status, hsts in ((403, 'max-age=31536000'), (500, 'max-age=31536000'),
                             (200, ''), (200, 'max-age=0'), (200, 'max-age=-1'),
                             (200, 'max-age=31536000; max-age=0')):
            with self.subTest(status=status, hsts=hsts):
                def change(url, reply):
                    return Reply(status, {'Strict-Transport-Security': hsts}) if url.startswith('https://') else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

    def test_duplicate_location_and_hsts_headers_are_rejected(self):
        for duplicate in ('Location', 'Strict-Transport-Security'):
            def change(url, reply):
                if duplicate in reply.headers:
                    reply.headers.add_header(duplicate, reply.headers[duplicate])
                return reply
            with self.subTest(header=duplicate), self.assertRaises(self.module.TransportError):
                self.module.check_transport(opener=self.opener(change))

    def test_network_failure_fails_closed(self):
        class Broken:
            def open(self, *_args, **_kwargs):
                raise URLError('unavailable')
        with self.assertRaises(self.module.TransportError):
            self.module.check_transport(opener=Broken())

    def test_urllib_redirect_exception_is_checked_without_following(self):
        fake = self.opener()
        class Redirects:
            def open(self, req, timeout):
                reply = fake.open(req, timeout)
                if req.full_url.startswith('http://'):
                    raise HTTPError(req.full_url, reply.status, 'redirect', reply.headers, None)
                return reply
        self.assertEqual(len(self.module.check_transport(opener=Redirects())), 5)

    def test_http_200_block_page_cannot_impersonate_the_resource(self):
        for content_type in ('text/html', 'application/json'):
            with self.subTest(content_type=content_type):
                def change(url, reply):
                    return Reply(200, {'Content-Type': content_type}, b'<html>Access blocked</html>', url) if url == VERSION_URL else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

    def test_manifest_redirect_is_rejected_including_an_already_followed_response(self):
        for status, final_url in ((301, VERSION_URL), (302, VERSION_URL),
                                  (200, 'https://example.com/VERSION.json')):
            with self.subTest(status=status, final_url=final_url):
                def change(url, reply):
                    return Reply(status, {'Content-Type': 'application/json', 'Location': final_url}, VALID_BODY, final_url) if url == VERSION_URL else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

        fake = self.opener()
        class Redirects:
            def open(self, request, timeout):
                if request.full_url == VERSION_URL:
                    raise HTTPError(VERSION_URL, 302, 'redirect', Message(), None)
                return fake.open(request, timeout)
        with self.assertRaises(self.module.TransportError):
            self.module.check_transport(opener=Redirects())

    def test_manifest_must_identify_a_release_and_the_expected_editable_download(self):
        invalid = (
            [], {}, {'web_version': '4.9.1', 'download': []},
            {**VALID_VERSION, 'web_version': 'release-4.9.1'},
            {**VALID_VERSION, 'web_version': '04.9.1'},
            {**VALID_VERSION, 'web_version': 491},
            {**VALID_VERSION, 'download': {**VALID_VERSION['download'], 'path': 'https://example.com/other.elpx'}},
            {**VALID_VERSION, 'download': {**VALID_VERSION['download'], 'path': 'downloads/other.elpx'}},
            *({**VALID_VERSION, 'download': {**VALID_VERSION['download'], 'sha256': digest}}
              for digest in ('', 'a' * 63, 'g' * 64, 'a' * 65, None)),
        )
        for manifest in invalid:
            with self.subTest(manifest=manifest):
                def change(url, reply):
                    return Reply(200, {'Content-Type': 'application/json'}, json.dumps(manifest).encode(), url) if url == VERSION_URL else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))

    def test_manifest_content_type_must_be_unambiguous_json(self):
        for content_type in (None, 'text/plain', 'application/problem+json'):
            with self.subTest(content_type=content_type):
                def change(url, reply):
                    return Reply(200, {'Content-Type': content_type} if content_type else {}, VALID_BODY, url) if url == VERSION_URL else reply
                with self.assertRaises(self.module.TransportError):
                    self.module.check_transport(opener=self.opener(change))
        def duplicate(url, reply):
            if url == VERSION_URL:
                reply.headers.add_header('Content-Type', 'application/json')
            return reply
        with self.assertRaises(self.module.TransportError):
            self.module.check_transport(opener=self.opener(duplicate))

    def test_large_manifest_is_rejected_without_unbounded_reading(self):
        def change(url, reply):
            body = VALID_BODY + b' ' * (65537 - len(VALID_BODY))
            return Reply(200, {'Content-Type': 'application/json'}, body, url) if url == VERSION_URL else reply
        with self.assertRaises(self.module.TransportError):
            self.module.check_transport(opener=self.opener(change))

    def test_small_valid_manifest_and_valid_semver_are_accepted(self):
        manifest = {**VALID_VERSION, 'web_version': '4.9.1-rc.1+build.12'}
        body = json.dumps(manifest).encode()
        body += b' ' * (65535 - len(body))
        def change(url, reply):
            return Reply(200, {'Content-Type': 'application/json'}, body, url) if url == VERSION_URL else reply
        self.assertEqual(self.module.check_transport(opener=self.opener(change))[-1].get('web_version'), '4.9.1-rc.1+build.12')


if __name__ == '__main__':
    unittest.main()
