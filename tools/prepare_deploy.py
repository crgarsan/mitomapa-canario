#!/usr/bin/env python3
"""Validate every public asset before replacing the deployment directory."""

from pathlib import Path
import shutil
import tempfile

from release_support import public_entries


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / ".deploy"


def stage_assets(root=ROOT, output=OUTPUT):
    # Complete validation before deleting or writing the existing stage. The
    # provider's per-file limit also applies to historical public downloads.
    entries = public_entries(root)
    temporary = Path(tempfile.mkdtemp(prefix=".deploy-", dir=root))
    try:
        for name, source in entries.items():
            destination = temporary / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        shutil.copy2(root / "SHA256SUMS.txt", temporary / "SHA256SUMS.txt")
        if output.exists():
            shutil.rmtree(output)
        temporary.replace(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return len(entries)


def main():
    count = stage_assets()
    print(f"Verified and staged {count} assets plus SHA256SUMS.txt in {OUTPUT}")


if __name__ == "__main__":
    main()
