#!/usr/bin/env python3
"""Require effective public HTTPS protection independently of API permissions."""
import json
import re
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOSTNAME = 'mitomapacanario.org'
PROBE_PATHS = ('/', '/downloads/MitoMapa_canario_GobCan.elpx?transport-check=1')
TIMEOUT = 15
MIN_HSTS_SECONDS = 31536000


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
