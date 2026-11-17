#!/usr/bin/env python3
"""Require effective public HTTPS protection independently of API permissions."""
import json
import re
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOSTNAME = 'mitomapacanario.org'
PROBE_PATHS = ('/', '/downloads/MitoMapa_canario_GobCan.elpx?transport-check=1')
VERSION_URL = 'https://' + HOSTNAME + '/VERSION.json'
DOWNLOAD_PATH = 'downloads/MitoMapa_canario_GobCan.elpx'
TIMEOUT = 15
MIN_HSTS_SECONDS = 31536000
MAX_VERSION_BYTES = 64 * 1024
SEMVER = re.compile(
    r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)'
    r'(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
    r'(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?'
    r'(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?'
)


class TransportError(Exception):
    """The fixed public transport contract could not be established."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def response_headers(opener, url):
    # No API credentials, cookies, response bodies or automatic redirect hops.
    request = Request(url, method='HEAD', headers={'User-Agent': 'MitoMapa-transport-check'})
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            return response.status, response.headers
    except HTTPError as response:
        try:
            return response.code, response.headers
        finally:
            response.close()
    except (OSError, ValueError, HTTPException):
        raise TransportError('Public transport request could not be verified.') from None


def single_header(headers, name):
    values = headers.get_all(name, [])
    if len(values) != 1 or not isinstance(values[0], str):
        raise TransportError('Expected exactly one ' + name + ' header.')
    return values[0]


def check_public_version(opener):
    # An HTTP 200 can still be a network block page; identify the actual resource.
    request = Request(VERSION_URL, method='GET', headers={
        'User-Agent': 'MitoMapa-transport-check', 'Accept': 'application/json',
    })
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            if response.status != 200 or response.geturl() != VERSION_URL:
                raise TransportError('The public version manifest must succeed without redirects.')
            content_type = single_header(response.headers, 'Content-Type')
            if content_type.split(';', 1)[0].strip().lower() != 'application/json':
                raise TransportError('The public version manifest must have JSON content type.')
            body = response.read(MAX_VERSION_BYTES)
    except HTTPError as response:
        response.close()
        raise TransportError('The public version manifest must succeed without redirects.') from None
    except (OSError, ValueError, HTTPException):
        raise TransportError('The public version manifest could not be verified.') from None
    # Reject a full buffer rather than reading one byte beyond the 64 KiB cap.
    if len(body) >= MAX_VERSION_BYTES:
        raise TransportError('The public version manifest must be smaller than 64 KiB.')
    try:
        manifest = json.loads(body.decode('utf-8'))
    except (UnicodeError, ValueError, RecursionError):
        raise TransportError('The public version manifest is not valid UTF-8 JSON.') from None
    if not isinstance(manifest, dict):
        raise TransportError('The public version manifest must identify a valid release.')
    version = manifest.get('web_version')
    download = manifest.get('download')
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise TransportError('The public version manifest must identify a valid release.')
    if (not isinstance(download, dict) or download.get('path') != DOWNLOAD_PATH
            or not isinstance(download.get('sha256'), str)
            or not re.fullmatch(r'[0-9A-Fa-f]{64}', download['sha256'])):
        raise TransportError('The public version manifest must identify the expected editable download and SHA-256.')
    return {'url': VERSION_URL, 'status': 200, 'web_version': version,
            'download_path': download['path'], 'download_sha256': download['sha256'],
            'body_bytes': len(body)}


def check_transport(opener=None):
    # Keep the configured proxy, normal TLS certificate checks and CA trust.
    opener = opener if opener is not None else build_opener(NoRedirect())
    checks = []
    for path in PROBE_PATHS:
        secure_url = 'https://' + HOSTNAME + path
        status, headers = response_headers(opener, 'http://' + HOSTNAME + path)
        if status not in (301, 308) or single_header(headers, 'Location') != secure_url:
            raise TransportError('HTTP must permanently redirect to the exact HTTPS host, path and query.')
        checks.append({'url': 'http://' + HOSTNAME + path, 'status': status, 'location': secure_url})
        status, headers = response_headers(opener, secure_url)
        if status != 200:
            raise TransportError('The HTTPS page or editable download is unavailable.')
        hsts = single_header(headers, 'Strict-Transport-Security')
        ages = [part.strip() for part in hsts.split(';') if part.strip().lower().startswith('max-age')]
        if (len(ages) != 1 or not re.fullmatch(r'max-age\s*=\s*\d+', ages[0], re.I)
                or int(ages[0].split('=', 1)[1]) < MIN_HSTS_SECONDS):
            raise TransportError('HTTPS must retain HSTS for at least one year.')
        checks.append({'url': secure_url, 'status': status, 'hsts': hsts})
    checks.append(check_public_version(opener))
    return checks


def main():
    try:
        checks = check_transport()
    except TransportError as error:
        print('::error title=Public HTTPS verification::' + str(error))
        return 1
    print(json.dumps({'hostname': HOSTNAME, 'verified': True, 'checks': checks}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
