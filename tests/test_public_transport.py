"""Public transport must be verified independently of Cloudflare API access."""
import importlib.util
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError
import unittest

ROOT = Path(__file__).resolve().parent.parent


class Reply:
    def __init__(self, status=200, headers=None):
        self.status = status
        self.headers = Message()
        for name, value in (headers or {}).items():
            self.headers.add_header(name, value)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


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
                if request.get_method() != 'HEAD' or timeout != 15:
                    raise AssertionError('Use bounded HEAD requests')
                if any(name.lower() in {'authorization', 'cookie'} for name in request.headers):
                    raise AssertionError('Public probes must not carry credentials')
                url = request.full_url
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
        self.assertEqual(len(result), 4)
        self.assertEqual(len(opener.requests), 4)
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
        self.assertEqual(len(self.module.check_transport(opener=self.opener(change))), 4)

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
        self.assertEqual(len(self.module.check_transport(opener=Redirects())), 4)


if __name__ == '__main__':
    unittest.main()
