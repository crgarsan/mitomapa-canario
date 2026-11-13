#!/usr/bin/env python3
"""Validate every public asset before replacing the deployment directory."""

import argparse
from pathlib import Path
import shutil
import tempfile

from release_support import approved_release_paths, public_entries, source_path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / ".deploy"


def stage_assets(root=ROOT, output=OUTPUT, *, inventory=None):
    # Complete validation before deleting or writing the existing stage. The
    # provider's per-file limit also applies to historical public downloads.
    entries = public_entries(root, approved=approved_release_paths(root, inventory))
    temporary = Path(tempfile.mkdtemp(prefix=".deploy-", dir=root))
    try:
        for name, source in entries.items():
            destination = temporary / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        shutil.copy2(source_path(root, "SHA256SUMS.txt"), temporary / "SHA256SUMS.txt")
        if output.exists():
            shutil.rmtree(output)
        temporary.replace(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="Reviewed JSON file list for a complete non-Git export")
    args = parser.parse_args()
    count = stage_assets(inventory=args.inventory)
    print(f"Verified and staged {count} assets plus SHA256SUMS.txt in {OUTPUT}")


if __name__ == "__main__":
    main()
