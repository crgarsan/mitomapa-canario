#!/usr/bin/env python3
"""Verify byte-range delivery of the eight published story videos over HTTPS."""

from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from check_public_transport import HOSTNAME, NoRedirect


DEPLOY = Path(__file__).resolve().parent.parent / '.deploy'
TIMEOUT = 15
ISLANDS = (
    'el-hierro',
    'fuerteventura',
    'gran-canaria',
    'la-gomera',
    'la-graciosa',
    'la-palma',
    'lanzarote',
    'tenerife',
)
PROBE_BYTES = 64
# Reproduce the Safari media probe against the public service, including its
# request classification at the edge.
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/18.0 Safari/605.1.15'
)


class VideoRangeError(Exception):
    """A public video did not return the expected bytes."""


def probe_range(opener, url, range_header, start, end, size, expected):
    request = Request(url, headers={
        'Range': range_header,
        'Accept-Encoding': 'identity',
        'User-Agent': USER_AGENT,
    })
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            if response.status != 206 or response.geturl() != url:
                raise VideoRangeError(f'expected HTTP 206 at the requested URL, got {response.status}')
            expected_range = f'bytes {start}-{end}/{size}'
            if response.headers.get_all('Content-Range', []) != [expected_range]:
                raise VideoRangeError(f'expected exactly one Content-Range: {expected_range}')
            if response.headers.get_all('Content-Type', []) != ['video/mp4']:
                raise VideoRangeError('expected exactly one Content-Type: video/mp4')
            lengths = response.headers.get_all('Content-Length', [])
            if lengths and lengths != [str(len(expected))]:
                raise VideoRangeError(f'expected Content-Length: {len(expected)}')
            if response.headers.get_all('Content-Encoding', []) not in ([], ['identity']):
                raise VideoRangeError('expected an uncompressed byte range')
            if response.read(len(expected) + 1) != expected:
                raise VideoRangeError('response bytes differ from the staged MP4')
    except HTTPError as error:
        error.close()
        raise VideoRangeError(f'expected HTTP 206 without redirect, got {error.code}') from None
    except (OSError, ValueError, HTTPException):
        raise VideoRangeError('HTTPS request failed or exceeded its timeout') from None


def verify_videos(opener, deploy):
    failures = 0
    for island in ISLANDS:
        path = f'media/{island}/cuento.mp4'
        url = f'https://{HOSTNAME}/{path}'
        try:
            with (deploy / path).open('rb') as video:
                size = video.seek(0, 2)
                if size < 2 * PROBE_BYTES:
                    raise VideoRangeError('staged MP4 is too short for the range checks')
                middle = size // 2
                probes = (
                    ('bytes=0-1', 0, 1),
                    (f'bytes={middle}-{middle + PROBE_BYTES - 1}', middle, middle + PROBE_BYTES - 1),
                    (f'bytes=-{PROBE_BYTES}', size - PROBE_BYTES, size - 1),
                )
                for range_header, start, end in probes:
                    video.seek(start)
                    expected = video.read(end - start + 1)
                    if len(expected) != end - start + 1:
                        raise VideoRangeError('unable to read all expected staged bytes')
                    try:
                        probe_range(opener, url, range_header, start, end, size, expected)
                    except VideoRangeError as error:
                        raise VideoRangeError(f'{range_header}: {error}') from None
        except (OSError, VideoRangeError) as error:
            failures += 1
            print(f'::error title=Story video range verification::{path}: {error}', flush=True)
        else:
            print(f'{path}: HTTP 206 and exact staged bytes for initial, middle and suffix ranges.', flush=True)
    print(f'Story video range verification: {len(ISLANDS) - failures}/{len(ISLANDS)} passed.', flush=True)
    return 1 if failures else 0


def main():
    # Keep normal TLS and the configured proxy, with no credential or redirect handling.
    return verify_videos(build_opener(NoRedirect()), DEPLOY)


if __name__ == '__main__':
    raise SystemExit(main())
