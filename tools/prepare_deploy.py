#!/usr/bin/env python3
"""Verify and stage only the static files listed in SHA256SUMS.txt."""

from hashlib import sha256
from pathlib import Path, PurePosixPath
import shutil


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / ".deploy"
CHECKSUMS = ROOT / "SHA256SUMS.txt"


def main() -> None:
    entries: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        if not separator or len(digest) != 64:
            raise ValueError(f"Invalid checksum entry: {line!r}")
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or name in seen:
            raise ValueError(f"Unsafe or duplicate asset path: {name!r}")
        source = ROOT.joinpath(*relative.parts)
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(source)
        actual = sha256(source.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"Checksum mismatch: {name}")
        entries.append((name, source))
        seen.add(name)

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name, source in entries:
        destination = OUTPUT / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    shutil.copy2(CHECKSUMS, OUTPUT / CHECKSUMS.name)
    print(f"Verified and staged {len(entries)} assets plus SHA256SUMS.txt in {OUTPUT}")


if __name__ == "__main__":
    main()
