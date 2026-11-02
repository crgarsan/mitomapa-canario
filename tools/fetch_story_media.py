#!/usr/bin/env python3
"""Restore separately distributed story media with normal HTTPS and pinned hashes."""
import argparse
import hashlib
from pathlib import Path
import tempfile
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from release_support import story_media_inventory

ROOT = Path(__file__).resolve().parent.parent
# The independent static host serves the pinned HTML without edge-injected scripts.
PUBLIC_URL = 'https://crgarsan.github.io/mitomapa-canario/'


def secure_base(value):
    parts = urlsplit(value)
    if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment):
        raise ValueError('The media source must be an HTTPS URL without credentials, query or fragment')
    return value.rstrip('/') + '/'


def download_media(root=ROOT, base_url=PUBLIC_URL, opener=urlopen):
    base_url = secure_base(base_url)
    media = story_media_inventory(root)
    count = 0
    for name, expected in sorted(media.items()):
        target = root.joinpath(*name.split('/'))
        relative = target.relative_to(root)
        if any(root.joinpath(*relative.parts[:i]).is_symlink() for i in range(1, len(relative.parts)+1)):
            raise ValueError('Media destination cannot contain a symbolic link')
        if target.is_file() and target.stat().st_size == expected['bytes']:
            with target.open('rb') as existing:
                if hashlib.file_digest(existing, 'sha256').hexdigest() == expected['sha256']:
                    continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            request = Request(urljoin(base_url, name), headers={'User-Agent': 'MitoMapa-media-download'})
            with opener(request, timeout=30) as response:
                secure_base(response.geturl())
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.media-', delete=False) as output:
                    temporary = Path(output.name)
                    digest = hashlib.sha256()
                    size = 0
                    while True:
                        block = response.read(min(256 * 1024, expected['bytes'] - size + 1))
                        if not block:
                            break
                        size += len(block)
                        if size > expected['bytes']:
                            raise ValueError('Media response exceeds its pinned size: ' + name)
                        digest.update(block)
                        output.write(block)
            if size != expected['bytes'] or digest.hexdigest() != expected['sha256']:
                raise ValueError('Media response differs from its pinned size or SHA-256: ' + name)
            temporary.replace(target)
            count += 1
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default=PUBLIC_URL,
                        help='Verified HTTPS website from which to retrieve the pinned media')
    args = parser.parse_args()
    print(f'Restored {download_media(base_url=args.base_url)} story media files with verified hashes.')


if __name__ == '__main__':
    main()
