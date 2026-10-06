#!/usr/bin/env python3
"""Package web sources without ELPX archives and refresh public checksums."""

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parent.parent
CHECKSUMS = ROOT / "SHA256SUMS.txt"


def main() -> None:
    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    archive_name = (
        "downloads/MitoMapa_fuentes_web_v"
        + version["web_version"].replace(".", "_")
        + ".zip"
    )
    names = []
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        _, separator, name = line.partition("  ")
        if not separator:
            raise ValueError(f"Invalid checksum entry: {line!r}")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or name in names:
            raise ValueError(f"Unsafe or duplicate asset path: {name!r}")
        names.append(name)
    if archive_name not in names:
        raise ValueError(f"Current source ZIP is missing from {CHECKSUMS}")

    archive_entries = [
        name
        for name in names
        if not name.startswith("downloads/MitoMapa_fuentes_web_")
        and not name.lower().endswith(".elpx")
    ]
    archive = ROOT / archive_name
    temporary = archive.with_suffix(".zip.tmp")
    with ZipFile(temporary, "w") as output:
        for name in sorted(archive_entries):
            source = ROOT / name
            if not source.is_file() or source.is_symlink():
                raise FileNotFoundError(source)
            entry = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            output.writestr(entry, source.read_bytes(), compresslevel=6)
    temporary.replace(archive)

    lines = []
    for name in names:
        source = ROOT / name
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(source)
        lines.append(f"{sha256(source.read_bytes()).hexdigest()}  {name}")
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated {archive_name} and {len(lines)} checksums")


if __name__ == "__main__":
    main()
