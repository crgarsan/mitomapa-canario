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
