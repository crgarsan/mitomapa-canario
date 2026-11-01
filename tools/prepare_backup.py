#!/usr/bin/env python3
"""Build a verified, independent Pages copy from the public release inventory."""
from hashlib import sha256
import argparse
import html
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen

from release_support import parse_sums, safe_name, source_path


ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 1_000_000_000
MAX_FILE_BYTES = 25 * 1024 * 1024
PRIVATE_PARTS = {'qa', 'tests', 'tools', 'work', 'outputs', 'node_modules', '__pycache__', 'secrets', 'credentials'}
TEXT_SUFFIXES = {'.html', '.htm', '.css', '.js', '.json', '.txt', '.xml', '.svg', '.md', '.webmanifest', '.csv'}
STATIC_SUFFIXES = TEXT_SUFFIXES | {'.png', '.webp', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.otf', '.mp3', '.m4a', '.mp4', '.vtt', '.pdf', '.wav', '.zip', '.elpx'}
TEACHER_MATERIALS = frozenset({
    'downloads/Cuaderno_de_ruta_MitoMapa.html',
    'downloads/Pauta_de_revision_MitoMapa.html',
    'downloads/Pauta_de_revision_MitoMapa.csv',
})
HISTORICAL_URL = re.compile(r'''(?<![A-Za-z0-9_:/.-])((?:/|(?:\.\./)+|\./)?downloads/[A-Za-z0-9_%+./-]+(?:[?#][^\s"'<>`)]*)?)''')
# Require a named URL path. The standalone '/' is also a JavaScript separator
# (notably decoded.split('/')), so changing it would break traversal rejection.
QUOTED_ROOT = re.compile(r'''(["'])(/(?!/)[A-Za-z0-9][^"'<>\s]*)\1''')
CSS_ROOT = re.compile(r'''url\(\s*(/(?!/)[^\s)'"<>]+)\s*\)''')


def file_hash(path):
    result = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def json_payload(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def https_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('A plain HTTPS base URL with a verified certificate is required')
    return value.rstrip('/') + '/'


def base_path(value):
    if not value.startswith('/') or '//' in value or any(p in {'.', '..'} for p in value.split('/')):
        raise ValueError('Invalid Pages base path')
    return value.rstrip('/') + '/' if value != '/' else '/'


def public_static(name):
    parts = safe_name(name).parts
    if any(p.startswith('.') or p.lower() in PRIVATE_PARTS or p.lower().endswith(('.old', '.bak', '.tmp')) for p in parts):
        return False
    if Path(parts[-1]).stem.lower() in {'credentials', 'secrets', 'private', 'token', 'tokens'}:
        return False
    if name in {'CNAME', '_headers', '_redirects', 'SHA256SUMS.txt'}:
        return False
    if Path(name).suffix.lower() not in STATIC_SUFFIXES and name not in {'LICENSE', 'COPYING'}:
        return False
    return True


def download_paths(version):
    result = set()
    for key in ('download', 'sharing_archive', 'source_archive'):
        name = version.get(key, {}).get('path')
        if not isinstance(name, str) or safe_name(name).parts[0] != 'downloads':
            raise ValueError('VERSION.json must identify exactly three current downloads')
        result.add(name)
    if len(result) != 3:
        raise ValueError('VERSION.json must identify exactly three distinct current downloads')
    return result


def inventory(root):
    sums = parse_sums(source_path(root, 'SHA256SUMS.txt').read_text(encoding='utf-8'))
    version = json.loads(source_path(root, 'VERSION.json').read_text(encoding='utf-8'))
    current = download_paths(version)
    retained_downloads = current | TEACHER_MATERIALS
    selected = {name: value for name, value in sums.items() if public_static(name) and (not name.startswith('downloads/') or name in retained_downloads)}
    for required in {'index.html', 'VERSION.json', 'MEDIA_MANIFEST.json'} | retained_downloads:
        if required not in selected:
            raise ValueError('Required public asset is not pinned in SHA256SUMS.txt: ' + required)
    media_path = source_path(root, 'MEDIA_MANIFEST.json')
    if media_path.stat().st_size > 1024 * 1024:
        raise ValueError('Media inventory is too large')
    media = json.loads(media_path.read_text(encoding='utf-8'))
    if not isinstance(media, dict) or media.get('version') != 1 or not isinstance(media.get('files'), dict) or not media['files']:
        raise ValueError('Invalid media inventory')
    for name, details in media['files'].items():
        if (not isinstance(name, str) or not name.startswith('media/') or not public_static(name)
                or not isinstance(details, dict) or set(details) != {'sha256', 'bytes'}
                or not isinstance(details['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', details['sha256'])
                or type(details['bytes']) is not int or details['bytes'] < 1):
            raise ValueError('Invalid media inventory entry')
        source = source_path(root, name)
        if source.stat().st_size != details['bytes'] or file_hash(source) != details['sha256']:
            raise ValueError('Pinned media mismatch: ' + name)
        if name in selected and selected[name] != details['sha256']:
            raise ValueError('Public and media inventories disagree: ' + name)
        selected[name] = details['sha256']
    paths = {}
    for name, expected in selected.items():
        path = source_path(root, name)
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Public asset size exceeds 25 MiB: ' + name)
        if file_hash(path) != expected:
            raise ValueError('Checksum mismatch: ' + name)
        paths[name] = path
    historical = sorted(name for name in sums if name.startswith('downloads/') and name not in retained_downloads)
    return paths, version, current, historical


def adapt_text(text, primary, prefix, current):
    def historical(match):
        raw = match.group(1)
        path = unquote(urlsplit(raw).path)
        name = path[path.index('downloads/'):]
        return raw if name in current else primary + raw[raw.index('downloads/'):]
    text = HISTORICAL_URL.sub(historical, text)
    def local(url):
        return url if prefix == '/' or url.startswith(prefix) else prefix + url.lstrip('/')
    text = QUOTED_ROOT.sub(lambda m: m.group(1) + local(m.group(2)) + m.group(1), text)
    return CSS_ROOT.sub(lambda m: 'url(' + local(m.group(1)) + ')', text)


def banner(text, primary):
    notice = ('<aside id="backup-notice" role="note" style="padding:.45rem 1rem;'
              'background:#f3efe5;color:#292a25;text-align:center;font-size:.875rem">'
              'Copia de respaldo · <a href="' + html.escape(primary, quote=True) +
              '" style="color:inherit">Ir a la web principal</a></aside>')
    if not re.search(r'<body\b[^>]*>', text, re.I):
        raise ValueError('The backup needs the actual MitoMapa HTML body')
    return re.sub(r'(<body\b[^>]*>)', lambda m: m.group(1) + notice, text, count=1, flags=re.I)


def git_identity(root, supplied):
    if supplied:
        if not re.fullmatch('[0-9a-f]{40}', supplied):
            raise ValueError('Source commit must be a full Git commit ID')
        return supplied, False
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True).strip())
    return commit, dirty


def stage_backup(root=ROOT, output=None, *, primary='https://mitomapacanario.org/', prefix='/mitomapa-canario/', commit=None, max_bytes=MAX_BYTES):
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / '.backup'
    if output.is_symlink():
        raise ValueError('Backup output cannot be a symbolic link')
    output = output.resolve()
    if output == root or output in root.parents:
        raise ValueError('Backup output cannot replace the repository or an ancestor')
    primary, prefix = https_url(primary), base_path(prefix)
    if not 0 < max_bytes <= MAX_BYTES:
        raise ValueError('Backup size limit must be positive and no greater than 1 GB')
    paths, version, current, historical = inventory(root)
    source_commit, dirty = git_identity(root, commit)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.backup-stage-', dir=output.parent))
    try:
        assets = {}
        for name, source in sorted(paths.items()):
            destination = temporary / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix.lower() in TEXT_SUFFIXES:
                text = adapt_text(source.read_text(encoding='utf-8'), primary, prefix, current | TEACHER_MATERIALS)
                if name == 'index.html':
                    text = banner(text, primary)
                destination.write_text(text, encoding='utf-8')
            else:
                shutil.copyfile(source, destination)
            assets[name] = {'sha256': file_hash(destination), 'bytes': destination.stat().st_size}
        media_destination = temporary / 'MEDIA_MANIFEST.json'
        staged_media = json.loads(media_destination.read_text(encoding='utf-8'))
        for name in staged_media['files']:
            staged_media['files'][name] = assets[name]
        media_destination.write_bytes(json_payload(staged_media))
        assets['MEDIA_MANIFEST.json'] = {'sha256': file_hash(media_destination), 'bytes': media_destination.stat().st_size}
        manifest = {
            'schema_version': 1, 'primary_url': primary, 'source_commit': source_commit,
            'source_worktree_dirty': dirty, 'web_version': version.get('web_version'),
            'rea_exelearning_version': version.get('rea_exelearning_version'), 'base_path': prefix,
            'hosting': 'GitHub Pages, independent of the primary Cloudflare hostname',
            'current_downloads': sorted(current), 'current_teacher_materials': sorted(TEACHER_MATERIALS),
            'historical_downloads_on_primary': [primary + n for n in historical],
            'media_manifest_sha256': assets['MEDIA_MANIFEST.json']['sha256'], 'files': assets,
        }
        (temporary / 'BACKUP_MANIFEST.json').write_bytes(json_payload(manifest))
        sums = ''.join(f'{file_hash(p)}  {p.relative_to(temporary).as_posix()}\n' for p in sorted(temporary.rglob('*')) if p.is_file())
        (temporary / 'SHA256SUMS.txt').write_text(sums, encoding='utf-8')
        files = [p for p in temporary.rglob('*') if p.is_file()]
        total = sum(p.stat().st_size for p in files)
        # Include conservative tar header/padding overhead in the 1 GB guard.
        tar_bound = sum(512 + 512 * math.ceil(p.stat().st_size / 512) for p in files) + 10240 + sum(512 for p in temporary.rglob('*') if p.is_dir())
        if max(total, tar_bound) > max_bytes:
            raise ValueError(f'Backup size exceeds the {max_bytes}-byte limit: {total} bytes, tar bound {tar_bound}')
        if output.exists():
            if output.is_symlink() or not output.is_dir():
                raise ValueError('Existing backup output must be a normal directory')
            shutil.rmtree(output)
        temporary.replace(output)
        return {'output': str(output), 'files': len(files), 'bytes': total, 'tar_bound_bytes': tar_bound, 'source_commit': source_commit, 'backup_manifest_sha256': file_hash(output / 'BACKUP_MANIFEST.json')}
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def verify_publication(base, *, expected_commit=None, expected_manifest_sha=None):
    base = https_url(base)
    if (not isinstance(expected_commit, str) or not re.fullmatch('[0-9a-f]{40}', expected_commit)
            or not isinstance(expected_manifest_sha, str) or not re.fullmatch('[0-9a-f]{64}', expected_manifest_sha)):
        raise ValueError('Expected full source commit and backup manifest SHA-256 are required')
    def fetch(name, limit):
        request = Request(urljoin(base, name), headers={'User-Agent': 'MitoMapa-backup-verification'})
        # Standard urllib TLS validation is retained; no insecure context or -k.
        with urlopen(request, timeout=30) as response:
            final = urlsplit(response.url)
            if response.status != 200 or final.scheme != 'https' or final.netloc != urlsplit(base).netloc:
                raise ValueError('Expected HTTPS content was not served from the backup host')
            payload = response.read(limit + 1)
            if len(payload) > limit:
                raise ValueError('Unexpectedly large verification response')
            return payload
    payload = fetch('BACKUP_MANIFEST.json', 2 * 1024 * 1024)
    if expected_manifest_sha and sha256(payload).hexdigest() != expected_manifest_sha:
        raise ValueError('Published backup manifest differs from the built artifact')
    manifest = json.loads(payload)
    if expected_commit and manifest.get('source_commit') != expected_commit:
        raise ValueError('Published backup commit is stale or unexpected')
    for name in ('index.html', 'VERSION.json', 'MEDIA_MANIFEST.json'):
        data = fetch(name, 4 * 1024 * 1024)
        if sha256(data).hexdigest() != manifest['files'][name]['sha256']:
            raise ValueError('Expected backup content mismatch: ' + name)
        if name == 'index.html' and (b'Copia de respaldo' not in data or b'MitoMapa' not in data):
            raise ValueError('The response is not the expected MitoMapa backup page')
    return {'https_certificate_validated': True, 'expected_content_verified': True, 'source_commit': manifest['source_commit'], 'base_url': base}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--primary-url', default='https://mitomapacanario.org/')
    parser.add_argument('--base-path', default='/mitomapa-canario/')
    parser.add_argument('--source-commit')
    parser.add_argument('--max-bytes', type=int, default=MAX_BYTES)
    parser.add_argument('--verify-url')
    parser.add_argument('--expected-manifest-sha')
    args = parser.parse_args()
    try:
        if args.verify_url:
            result = verify_publication(args.verify_url, expected_commit=args.source_commit, expected_manifest_sha=args.expected_manifest_sha)
        else:
            result = stage_backup(args.root, args.output, primary=args.primary_url, prefix=args.base_path, commit=args.source_commit, max_bytes=args.max_bytes)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print('Backup verification failed: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
