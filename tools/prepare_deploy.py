#!/usr/bin/env python3
"""Validate every public asset before replacing the deployment directory."""

from hashlib import sha256
from pathlib import Path
import shutil
import tempfile

from release_support import STORY_ISLANDS, public_entries, story_media_inventory


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / ".deploy"
STORY_VIDEO_PART_BYTES = 1024 * 1024
STORY_VIDEOS = (
    *(f"media/{island}/cuento.mp4" for island in STORY_ISLANDS),
    *(f"en/media/{island}/story.mp4" for island in STORY_ISLANDS),
)


def stage_story_video_parts(stage):
    inventory = story_media_inventory(stage)
    for name in STORY_VIDEOS:
        details = inventory.get(name)
        if details is None:
            continue
        folder = stage / "_story_video_parts" / details["sha256"]
        folder.mkdir(parents=True, exist_ok=True)
        hasher = sha256()
        with (stage / name).open("rb") as movie:
            for index, chunk in enumerate(iter(lambda: movie.read(STORY_VIDEO_PART_BYTES), b"")):
                hasher.update(chunk)
                (folder / f"{index}.bin").write_bytes(chunk)
            if movie.tell() != details["bytes"] or hasher.hexdigest() != details["sha256"]:
                raise ValueError(f"Staged story video differs from its pinned metadata: {name}")


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
        stage_story_video_parts(temporary)
        if output.exists():
            shutil.rmtree(output)
        temporary.replace(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return len(entries)


def main():
    count = stage_assets()
    print(f"Verified and staged {count} assets, SHA256SUMS.txt and story video parts in {OUTPUT}")


if __name__ == "__main__":
    main()
