#!/usr/bin/env python3
"""Validate every public asset before replacing the deployment directory."""

import argparse
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from release_support import (
    MAX_ASSET_BYTES, STORY_ISLANDS, approved_release_paths, public_entries,
    source_path, story_media_inventory,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / ".deploy"
STORY_VIDEO_PART_BYTES = 1024 * 1024
HLS_TAGS = frozenset({
    "#EXTM3U", "#EXT-X-VERSION", "#EXT-X-TARGETDURATION", "#EXT-X-MEDIA-SEQUENCE",
    "#EXT-X-PLAYLIST-TYPE", "#EXT-X-INDEPENDENT-SEGMENTS", "#EXT-X-MAP",
    "#EXTINF", "#EXT-X-ENDLIST",
})
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


def check_hls_playlist(directory):
    files = list(directory.iterdir())
    if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= MAX_ASSET_BYTES for p in files):
        raise ValueError(f"Invalid or oversized HLS asset: {directory.name}")
    playlist = directory / "story.m3u8"
    lines = playlist.read_text(encoding="utf-8").splitlines()
    if (not lines or lines[0] != "#EXTM3U" or lines[-1] != "#EXT-X-ENDLIST"
            or "#EXT-X-PLAYLIST-TYPE:VOD" not in lines
            or [line for line in lines if line.startswith("#EXT-X-MAP")] != ['#EXT-X-MAP:URI="init.mp4"']):
        raise ValueError(f"Invalid HLS playlist: {directory.name}")
    segments = [line for line in lines if line and not line.startswith("#")]
    if not segments or segments != [f"seg-{index:03d}.m4s" for index in range(len(segments))]:
        raise ValueError(f"Invalid HLS segment path or sequence: {directory.name}")
    for line in lines:
        if line.startswith("#") and (line.partition(":")[0] not in HLS_TAGS
                or (not line.startswith("#EXT-X-MAP:") and re.search(r"\bURI\s*=", line, re.I))):
            raise ValueError(f"Unexpected HLS playlist tag: {directory.name}")
    if {p.name for p in files} != {"story.m3u8", "init.mp4", *segments}:
        raise ValueError(f"HLS playlist does not match its staged files: {directory.name}")


def stage_english_hls(stage, ffmpeg):
    executable = shutil.which(ffmpeg)
    if not executable:
        raise ValueError(f"FFmpeg executable not found: {ffmpeg}")
    executable = str(Path(executable).resolve())
    inventory = story_media_inventory(stage)
    for island in STORY_ISLANDS:
        name = f"en/media/{island}/story.mp4"
        if name not in inventory or not (stage / name).is_file():
            raise ValueError(f"English story video is missing from the verified stage: {name}")
        directory = stage / "en" / "video-hls" / island
        directory.mkdir(parents=True)
        subprocess.run([
            executable, "-hide_banner", "-nostdin", "-v", "error", "-xerror",
            "-protocol_whitelist", "file", "-f", "mov", "-i", str((stage / name).resolve()),
            "-map", "0:v:0", "-map", "0:a:0", "-c", "copy", "-f", "hls",
            "-hls_playlist_type", "vod", "-hls_time", "3", "-hls_flags", "independent_segments",
            "-hls_segment_type", "fmp4", "-hls_fmp4_init_filename", "init.mp4",
            "-hls_segment_filename", "seg-%03d.m4s", "story.m3u8",
        ], cwd=directory, check=True)
        check_hls_playlist(directory)


def stage_assets(root=ROOT, output=OUTPUT, *, ffmpeg=None, inventory=None):
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
        stage_story_video_parts(temporary)
        if ffmpeg is not None:
            stage_english_hls(temporary, ffmpeg)
        if output.exists():
            shutil.rmtree(output)
        temporary.replace(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", metavar="EXECUTABLE", help="also stage English HLS playback files")
    parser.add_argument("--inventory", type=Path, help="Reviewed JSON file list for a complete non-Git export")
    args = parser.parse_args()
    count = stage_assets(ffmpeg=args.ffmpeg, inventory=args.inventory)
    generated = "story video parts and English HLS" if args.ffmpeg is not None else "story video parts"
    print(f"Verified and staged {count} assets, SHA256SUMS.txt and {generated} in {OUTPUT}")


if __name__ == "__main__":
    main()
