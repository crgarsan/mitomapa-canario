#!/usr/bin/env python3
"""Prepare and verify a byte-preserving historical archive migration; never publish."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import quote
from harden_jspdf_exports import read_archive, read_archive_file

from release_support import (
    ENGLISH_DOWNLOADS, PINTADERA_DIRECTORY, PINTADERA_GROUPS,
    VASIJA_COLLECTION_ZIP, approved_release_paths, json_bytes, safe_name, source_path,
)


CATALOG_NAME = "HISTORICAL_RELEASES.json"
PUBLIC_BASE_URL = "https://mitomapacanario.org/"
RELEASE_BASE_URL = "https://github.com/crgarsan/mitomapa-canario/releases/download/"
ARCHIVE_SUFFIXES = (".zip", ".elpx")
ASSET_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,254}")
COMMIT = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")


def current_archive_paths(root, version):
    """Current ES paths come from legacy VERSION fields; companions share release constants."""
    root = Path(root)
    paths = set()
    for key in ("download", "sharing_archive", "source_archive"):
        try:
            name = version[key]["path"]
            safe_name(name)
        except (KeyError, TypeError) as error:
            raise ValueError(f"Missing current VERSION.json field: {key}.path") from error
        if not name.lower().endswith(ARCHIVE_SUFFIXES):
            raise ValueError(f"Not a current archive path: {name}")
        paths.add(name)
    if (root / "index-en.html").is_file():
        paths.update(name for name in ENGLISH_DOWNLOADS if name.lower().endswith(ARCHIVE_SUFFIXES))
    if (root / PINTADERA_DIRECTORY).exists():
        paths.update(f"{PINTADERA_DIRECTORY}/{group}.zip" for group in PINTADERA_GROUPS)
    if (root / VASIJA_COLLECTION_ZIP).exists():
        paths.add(VASIJA_COLLECTION_ZIP)
    return frozenset(paths)


def _git(root, *args, input_data=None):
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=input_data,
                              check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Cannot verify source commit provenance from this Git checkout") from error


def _archive_identity(root, name, *, expected_object=None):
    path = source_path(root, name)
    try:
        payload = read_archive_file(path)
        # Validate direct members only, matching the catalog's existing CRC scope.
        # This preflights metadata before ZipFile and bounds every decoded read.
        read_archive(payload)
    except (ValueError, RuntimeError, NotImplementedError, EOFError, OSError) as error:
        raise ValueError(f"Invalid ZIP or CRC: {name}: {error}") from error
    if expected_object is not None:
        # Git must identify the same bytes already used for CRC and SHA-256.
        # Reopening the pathname here would permit a swap after that read.
        actual_object = _git(root, "hash-object", "--no-filters", "--stdin", input_data=payload).strip()
        if actual_object != expected_object:
            raise ValueError(f"Historical archive identity differs from source commit: {name}")
    return {"bytes": len(payload), "sha256": sha256(payload).hexdigest(), "crcValid": True}


def _known_consumers(version, path):
    consumers = []

    def visit(value, key):
        if isinstance(value, dict):
            for name, nested in value.items():
                visit(nested, f"{key}.{name}" if key else name)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                visit(nested, f"{key}[{index}]")
        elif value == path:
            consumers.append(f"VERSION.json:{key}")

    visit(version, "")
    return sorted(consumers)


def _asset_names(paths):
    basenames = Counter(PurePosixPath(name).name for name in paths)
    names = {}
    for path in paths:
        basename = PurePosixPath(path).name
        # Hex-encoded UTF-8 full paths are reversible and do not flatten slash/underscore ambiguities.
        name = basename if basenames[basename] == 1 else f"path-{path.encode('utf-8').hex()}{PurePosixPath(path).suffix}"
        if not ASSET_NAME.fullmatch(name):
            raise ValueError(f"Unsafe or overlong release asset name: {name!r}")
        names[path] = name
    if len(set(names.values())) != len(names):
        raise ValueError("Duplicate proposed release asset name after collision escaping")
    return names


def build_catalog(root, *, source_commit, version=None, inventory=None):
    """Return a deterministic planned catalog, proving historical bytes match source_commit."""
    root = Path(root)
    if not isinstance(source_commit, str) or not COMMIT.fullmatch(source_commit):
        raise ValueError("sourceCommit must be a full lowercase Git commit hash")
    resolved = _git(root, "rev-parse", "--verify", f"{source_commit}^{{commit}}").decode().strip()
    if resolved != source_commit:
        raise ValueError("sourceCommit must identify its exact commit")
    version = json.loads((root / "VERSION.json").read_text(encoding="utf-8")) if version is None else version
    approved = approved_release_paths(root, inventory)
    all_archives = {name for name in approved if name.lower().endswith(ARCHIVE_SUFFIXES)}
    current = current_archive_paths(root, version)
    if current - all_archives:
        raise ValueError("Missing current archive inventory: " + ", ".join(sorted(current - all_archives)))
    current_identities = {name: _archive_identity(root, name) for name in sorted(current)}
    for key in ("download", "sharing_archive", "source_archive"):
        declared = version[key]
        actual = current_identities[declared["path"]]
        if any(field in declared and declared[field] != actual[field] for field in ("bytes", "sha256")):
            raise ValueError(f"Wrong current archive identity in VERSION.json: {key}")
    historical = sorted(all_archives - current)
    names = _asset_names(historical)
    tag = "archive-" + source_commit[:12]
    archives = []
    for name in historical:
        committed_object = _git(root, "rev-parse", "--verify", f"{source_commit}:{name}").strip()
        identity = _archive_identity(root, name, expected_object=committed_object)
        consumers = _known_consumers(version, name)
        archives.append({
            "originalPath": name,
            "originalURL": PUBLIC_BASE_URL + quote(name, safe="/"),
            "sourceCommit": source_commit,
            **identity,
            "knownConsumers": consumers,
            "requiresConsumerAdaptation": bool(consumers),
            "destination": {
                "provider": "GitHub Releases",
                "tag": tag,
                "assetName": names[name],
                "proposedURL": RELEASE_BASE_URL + tag + "/" + names[name],
                "status": "planned",
                "active": False,
            },
        })
    return {
        "schemaVersion": 1,
        "sourceCommit": source_commit,
        "migrationStatus": "planned",
        "provenance": "Historical bytes verified against the source commit; dates and versions are not inferred from paths.",
        "consumerDiscovery": "Exact path references in VERSION.json; external and unlisted consumers require review before removal.",
        "assetNamePolicy": "Unique safe basenames; collisions use path- plus the full UTF-8 path encoded as lowercase hex plus its original extension.",
        "currentArchivePaths": sorted(current),
        "archives": archives,
    }


def check_catalog(root, catalog=None, *, version=None, inventory=None):
    """Read-only check of exact inventory, identities, CRC, provenance and planned destinations."""
    root = Path(root)
    catalog = json.loads((root / CATALOG_NAME).read_text(encoding="utf-8")) if catalog is None else catalog
    if not isinstance(catalog, dict) or not isinstance(catalog.get("archives"), list):
        raise ValueError("Invalid historical catalog inventory")
    paths = []
    asset_names = []
    for item in catalog["archives"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid historical catalog inventory entry")
        name = item.get("originalPath")
        safe_name(name)
        paths.append(name)
        destination = item.get("destination")
        if not isinstance(destination, dict):
            raise ValueError(f"Invalid destination for {name}")
        asset_name = destination.get("assetName")
        if not isinstance(asset_name, str) or not ASSET_NAME.fullmatch(asset_name):
            raise ValueError(f"Unsafe release asset destination: {asset_name!r}")
        asset_names.append(asset_name)
        if destination.get("status") != "planned" or destination.get("active") is not False:
            raise ValueError(f"Historical destination must remain planned and inactive: {name}")
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate historical original path")
    if len(asset_names) != len(set(asset_names)):
        raise ValueError("Duplicate release asset destination name")
    expected = build_catalog(root, source_commit=catalog.get("sourceCommit"), version=version, inventory=inventory)
    if set(paths) != {item["originalPath"] for item in expected["archives"]}:
        raise ValueError("Historical inventory mismatch, including current archive exclusion")
    if catalog != expected:
        raise ValueError("Historical catalog identity, metadata or destination differs from the verified plan")
    return catalog


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--inventory", type=Path, help="Reviewed file inventory for a non-Git export (source provenance still requires Git)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Read-only validation of HISTORICAL_RELEASES.json")
    mode.add_argument("--source-commit", help="Build the planned catalog for this full commit hash")
    args = parser.parse_args(argv)
    try:
        if args.check:
            catalog = check_catalog(args.root, inventory=args.inventory)
        else:
            catalog = build_catalog(args.root, source_commit=args.source_commit, inventory=args.inventory)
            (args.root / CATALOG_NAME).write_bytes(json_bytes(catalog))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Historical archive check failed: {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(catalog['archives'])} planned historical archives; {len(catalog['currentArchivePaths'])} current archives excluded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
