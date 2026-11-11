"""Small shared checks for the public release and its deployment allowlist."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import PurePosixPath
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


MAX_ASSET_BYTES = 25 * 1024 * 1024
MAX_EXPANDED_BYTES = 512 * 1024 * 1024
DIGEST = re.compile(r"[0-9a-f]{64}")
PINTADERA_MANIFEST = 'PINTADERAS_3D.json'
PINTADERA_DIRECTORY = 'downloads/pintaderas-3d'
PINTADERA_GROUPS = ('recreaciones', 'sellos')
PINTADERA_STL = re.compile(r'downloads/pintaderas-3d/(recreaciones|sellos)/(pintadera_[a-z_]+\.stl)')


VASIJA_STL = "downloads/vasija/vasija_canaria.stl"
VASIJA_ASSETS = frozenset({
    VASIJA_STL,
    "vasija-visor.js",
    "assets/vasija/ficha.json",
    "assets/vasija/vistas.webp",
})


VASIJA_COLLECTION_IDS = ('gran-canaria', 'la-palma', 'lanzarote', 'fuerteventura', 'la-gomera', 'el-hierro')
VASIJA_COLLECTION_ZIP = 'downloads/vasijas/coleccion.zip'
VASIJA_COLLECTION_MODELS = {
    f'MitoMapa_{slug}.stl': f'downloads/vasijas/{slug}.stl' for slug in VASIJA_COLLECTION_IDS
}
VASIJA_COLLECTION_ASSETS = frozenset({
    VASIJA_COLLECTION_ZIP,
    'assets/vasijas/coleccion.json',
    *VASIJA_COLLECTION_MODELS.values(),
    *(f'assets/vasijas/{slug}.webp' for slug in VASIJA_COLLECTION_IDS),
})


def vasija_assets(root):
    """Include each set of models and companion files as a unit."""
    return frozenset().union(*(
        group for group in (VASIJA_ASSETS, VASIJA_COLLECTION_ASSETS)
        if any((root / name).exists() for name in group)
    ))


def check_vasija_collection(root, assets):
    if VASIJA_COLLECTION_ZIP not in assets:
        return
    packed = read_zip(source_path(root, VASIJA_COLLECTION_ZIP).read_bytes())
    expected = {
        member: metadata(source_path(root, model).read_bytes())
        for member, model in VASIJA_COLLECTION_MODELS.items()
    }
    if {member: metadata(data) for member, data in packed.items()} != expected:
        raise ValueError('Vasija ZIP does not match its six individual STL files')


def safe_name(name):
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name
            or name.startswith("/") or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError(f"Unsafe asset path: {name!r}")
    return PurePosixPath(name)


def source_path(root, name):
    relative = safe_name(name)
    path = root.joinpath(*relative.parts)
    if (not path.is_file() or any(root.joinpath(*relative.parts[:i]).is_symlink()
                                for i in range(1, len(relative.parts) + 1))):
        raise FileNotFoundError(f"Missing or symbolic-link asset: {name}")
    return path


def digest(payload):
    return sha256(payload).hexdigest()


def metadata(payload):
    return {"sha256": digest(payload), "bytes": len(payload)}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def parse_sums(text):
    entries = {}
    for line in text.splitlines():
        expected, separator, name = line.partition("  ")
        if not separator or not DIGEST.fullmatch(expected):
            raise ValueError(f"Invalid checksum entry: {line!r}")
        safe_name(name)
        if name in entries:
            raise ValueError(f"Duplicate checksum asset: {name}")
        entries[name] = expected
    if not entries:
        raise ValueError("Empty checksum inventory")
    return entries


def sums_bytes(files):
    return "".join(f"{digest(payload)}  {name}\n" for name, payload in sorted(files.items())).encode()


def verify_sums(files, manifest_name="SHA256SUMS.txt"):
    entries = parse_sums(files[manifest_name].decode("utf-8"))
    if set(entries) != set(files) - {manifest_name}:
        raise ValueError(f"Incomplete {manifest_name} inventory")
    for name, expected in entries.items():
        if digest(files[name]) != expected:
            raise ValueError(f"Checksum mismatch: {name}")


def verify_manifest(files, manifest, excluded=()):
    if set(manifest) != set(files) - set(excluded):
        raise ValueError("Incomplete archive asset manifest")
    for name, details in manifest.items():
        safe_name(name)
        if details != metadata(files[name]):
            raise ValueError(f"Archive manifest mismatch: {name}")


def read_zip(payload):
    with ZipFile(BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP members")
        for item in archive.infolist():
            safe_name(item.filename.rstrip("/") if item.is_dir() else item.filename)
        if sum(item.file_size for item in archive.infolist()) > MAX_EXPANDED_BYTES:
            raise ValueError("Archive expands beyond the validation limit")
        bad = archive.testzip()
        if bad:
            raise ValueError(f"Damaged ZIP member: {bad}")
        return {item.filename: archive.read(item) for item in archive.infolist() if not item.is_dir()}


def zip_bytes(files):
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        for name, payload in sorted(files.items()):
            safe_name(name)
            entry = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, payload, compresslevel=9)
    return output.getvalue()


def public_entries(root, *, verify=True):
    entries = parse_sums((root / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    paths = {}
    for name, expected in entries.items():
        source = source_path(root, name)
        if source.stat().st_size > MAX_ASSET_BYTES:
            raise ValueError(f"Public asset exceeds the 25 MiB limit: {name}")
        if verify and digest(source.read_bytes()) != expected:
            raise ValueError(f"Checksum mismatch: {name}")
        paths[name] = source
    return paths


def pintadera_inventory(root):
    """Return the paired, explicitly listed printable models and ZIPs."""
    if not (root / PINTADERA_MANIFEST).exists():
        return {}
    path = source_path(root, PINTADERA_MANIFEST)
    if path.stat().st_size > 32 * 1024:
        raise ValueError('Pintadera inventory is too large')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('version') != 1 or not isinstance(manifest.get('files'), dict):
        raise ValueError('Invalid pintadera inventory')
    files = manifest['files']
    groups = {group: set() for group in PINTADERA_GROUPS}
    zip_paths = {f'{PINTADERA_DIRECTORY}/{group}.zip' for group in groups}
    for name, details in files.items():
        if name not in zip_paths:
            match = PINTADERA_STL.fullmatch(name)
            if not match:
                raise ValueError('Unexpected pintadera download: ' + name)
            groups[match[1]].add(match[2])
        if (not isinstance(details, dict) or set(details) != {'sha256', 'bytes'}
                or not isinstance(details['sha256'], str) or not DIGEST.fullmatch(details['sha256'])
                or type(details['bytes']) is not int or not 0 < details['bytes'] <= MAX_ASSET_BYTES):
            raise ValueError('Invalid pintadera file metadata: ' + name)
    if not zip_paths <= files.keys() or len(groups['sellos']) != 10 or groups['sellos'] != groups['recreaciones']:
        raise ValueError('Expected two complete collections of ten matching pintadera designs')
    return files


def story_media_inventory(root):
    """Read bounded metadata; it may precede a source user's media download."""
    manifest_path = root / 'MEDIA_MANIFEST.json'
    if not manifest_path.exists():
        return {}
    manifest_path = source_path(root, 'MEDIA_MANIFEST.json')
    if manifest_path.stat().st_size > 512 * 1024:
        raise ValueError('Story media inventory is too large')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or manifest.get('version') != 1
            or not isinstance(manifest.get('files'), dict)
            or not 1 <= len(manifest['files']) <= 160):
        raise ValueError('Invalid story media inventory')
    approved = {}
    total = 0
    allowed = {'.mp4', '.pdf', '.vtt', '.webp', '.mp3', '.m4a', '.txt', '.html'}
    for name, details in manifest['files'].items():
        path = safe_name(name)
        if (not re.fullmatch(r'media/[A-Za-z0-9][A-Za-z0-9._/-]*', name)
                or path.suffix.lower() not in allowed):
            raise ValueError('Story media must stay inside the media directory')
        if (not isinstance(details, dict) or set(details) != {'sha256', 'bytes'}
                or not isinstance(details['sha256'], str) or not DIGEST.fullmatch(details['sha256'])
                or type(details['bytes']) is not int or details['bytes'] < 1):
            raise ValueError('Invalid story media metadata')
        if details['bytes'] > MAX_ASSET_BYTES:
            raise ValueError('Story media exceeds the 25 MiB limit: ' + name)
        total += details['bytes']
        if total > MAX_EXPANDED_BYTES:
            raise ValueError('Story media collection exceeds the validation limit')
        approved[name] = details
    return approved


def pinned_story_media(root):
    """Return explicitly approved story files after size, path and hash checks."""
    approved = story_media_inventory(root)
    for name, details in approved.items():
        source = source_path(root, name)
        if source.stat().st_size != details['bytes'] or digest(source.read_bytes()) != details['sha256']:
            raise ValueError('Story media metadata mismatch: ' + name)
    return approved
