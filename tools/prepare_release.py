#!/usr/bin/env python3
"""Prepare a reviewable, commit-pinned delivery; never publish, tag or rebuild.

The source must be a clean Git checkout at the explicitly supplied full commit.
Verification also uses that trusted checkout, so rehashed false metadata cannot
substitute a different release. ZIP/ELPX bytes are copied verbatim after bounded
recursive structure, size and CRC validation.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from harden_jspdf_exports import ArchiveBudget, DeliveryFiles, read_archive
from release_support import (
    MAX_ASSET_BYTES, PINTADERA_DIRECTORY, PINTADERA_GROUPS, VASIJA_COLLECTION_ZIP,
    approved_release_paths, json_bytes, parse_sums,
    require_approved, safe_name, sums_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
COMMIT = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
# Product metadata uses language, optional script and region BCP 47 tags.
# Preserve their spelling and the helper's slash-separated multilingual form.
LANGUAGE_TAG = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z]{4})?(?:-(?:[A-Za-z]{2}|[0-9]{3}))?")
MANIFEST = "RELEASE_MANIFEST.json"
SUMS = "SHA256SUMS.txt"
NOTES = "RELEASE_NOTES.md"
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
EXPECTED_ARCHIVES = 8
ARCHIVE_SUFFIXES = {".zip", ".elpx"}
UNVERSIONED_COLLECTIONS = frozenset({
    VASIJA_COLLECTION_ZIP, *(f"{PINTADERA_DIRECTORY}/{group}.zip" for group in PINTADERA_GROUPS),
})


def metadata_outputs(root, version):
    from release_metadata import document_outputs
    return document_outputs(root, version)


def metadata_products(root, version):
    from release_metadata import product_rows
    return product_rows(root, version)


def current_paths(root, version):
    from historical_releases import current_archive_paths
    return current_archive_paths(root, version)


def validate_historical(root, version):
    from historical_releases import check_catalog
    check_catalog(root, version=version)


def validate_readiness(root, version):
    """Run the four maintained, read-only validators against the selected tree."""
    for script in ("sync_current_elpx.py", "update_release.py", "harden_jspdf_exports.py",
                   "harden_drawing_archives.py"):
        result = subprocess.run([sys.executable, str(root / "tools" / script), "--check"],
                                cwd=root, capture_output=True, text=True)
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()[-4000:]
            raise ValueError(f"Readiness check failed ({script}): {detail}")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("A readable Git checkout is required for release provenance") from error


def _without_links(path):
    """Reject every existing symlink component, including a symlinked parent."""
    path = Path(os.path.abspath(path))
    for component in (*reversed(path.parents), path):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        _require(not stat.S_ISLNK(info.st_mode), f"Symbolic-link path is not allowed: {component}")
    return path


def _source(root, expected_commit):
    _require(isinstance(expected_commit, str) and COMMIT.fullmatch(expected_commit),
             "Supply the exact lowercase 40-character source commit")
    root = _without_links(root)
    _require(root.is_dir(), "Source root must be a Git checkout directory")
    top = Path(os.fsdecode(_git(root, "rev-parse", "--show-toplevel").rstrip(b"\n")))
    _require(top.resolve() == root.resolve(), "Source root must be the Git worktree root")
    head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    _require(head == expected_commit, "Source HEAD differs from the requested source commit")
    _require(not _git(root, "status", "--porcelain=v1", "--untracked-files=all").strip(),
             "Source checkout must be clean, including staged and untracked files")
    return root


def _archive_crc(payload, *, budget=None, depth=0):
    budget = ArchiveBudget() if budget is None else budget
    _, files, _ = read_archive(payload, budget=budget, depth=depth)
    for name, data in files.items():
        if Path(name).suffix.lower() in ARCHIVE_SUFFIXES and not name.endswith("/"):
            _archive_crc(data, budget=budget, depth=depth + 1)


def _product(row, name, payload, web_version):
    """Normalize product identity without inventing a version for 3D collections."""
    actual_hash = sha256(payload).hexdigest()
    if row is None:
        _require(name in UNVERSIONED_COLLECTIONS, "Missing current product metadata: " + name)
        return {"path": name, "product": "model_collection", "language": "und", "version": None,
                "baseVersion": None, "webVersionReference": web_version,
                "bytes": len(payload), "sha256": actual_hash, "crcValid": True}
    _require(row.get("bytes") == len(payload) and row.get("sha256") == actual_hash,
             "Product metadata identity differs from the committed archive: " + name)
    product, language, version = (row.get(key) for key in ("product", "language", "version"))
    _require(isinstance(product, str) and 0 < len(product) <= 100 and not any(c in product for c in "\r\n\0"),
             "Invalid product identity: " + name)
    language_tags = language.split("/") if isinstance(language, str) else []
    _require(bool(language_tags) and all(LANGUAGE_TAG.fullmatch(tag) for tag in language_tags)
             and len({tag.casefold() for tag in language_tags}) == len(language_tags),
             "Invalid product language: " + name)
    _require(isinstance(version, str) and VERSION.fullmatch(version), "Invalid product version: " + name)
    base_version = row.get("base_version")
    _require(base_version is None or isinstance(base_version, str) and VERSION.fullmatch(base_version),
             "Invalid base product version: " + name)
    return {"path": name, "product": product, "language": language, "version": version,
            "baseVersion": base_version, "webVersionReference": web_version,
            "bytes": len(payload), "sha256": actual_hash, "crcValid": True}


def _notes(manifest):
    lines = ["# Entrega de MitoMapa para revisión", "", f"Commit de origen: `{manifest['sourceCommit']}`.",
             f"Etiqueta propuesta: `{manifest['proposedTag']}`.", "",
             "Esta preparación no crea etiquetas, releases ni despliegues. Los ZIP/ELPX conservan los bytes validados del commit.",
             "Las versiones de cada producto son independientes. Las colecciones 3D sin versión propia solo indican la web de referencia.",
             "", "| Producto | Idioma | Versión | Ruta |", "| --- | --- | --- | --- |"]
    for item in manifest["files"]:
        lines.append(f"| {item['product']} | {item['language']} | {item['version'] or 'Sin versión propia'} | `{item['path']}` |")
    lines += ["", "Las identidades, tamaños y SHA-256 constan en RELEASE_MANIFEST.json. SHA256SUMS.txt cubre los archivos de entrega, el manifiesto y estas notas; se excluye a sí mismo.", ""]
    return "\n".join(lines).encode("utf-8")


def _collect(root, expected_commit, *, validate=True):
    root = _source(root, expected_commit)
    approved = approved_release_paths(root)
    require_approved({"VERSION.json", "SHA256SUMS.txt"}, approved)
    tree = {}
    for record in filter(None, _git(root, "ls-tree", "-r", "--full-tree", "-z", expected_commit).split(b"\0")):
        info, name = record.split(b"\t", 1)
        mode, kind, object_id = info.split()
        if mode in {b"100644", b"100755"} and kind == b"blob":
            tree[os.fsdecode(name)] = object_id.decode()
    with DeliveryFiles(root) as source:
        def committed(name):
            payload = source.read(name)
            object_id = sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            _require(tree.get(name) == object_id, "Source bytes differ from the requested Git commit: " + name)
            return payload

        version = json.loads(committed("VERSION.json"))
        web_version = version.get("web_version")
        _require(isinstance(web_version, str) and VERSION.fullmatch(web_version), "Invalid web version for proposed tag")
        names = set(current_paths(root, version))
        _require(len(names) == EXPECTED_ARCHIVES, "Expected exactly eight current ZIP/ELPX archives")
        for name in names:
            safe_name(name)
            _require(Path(name).suffix.lower() in ARCHIVE_SUFFIXES, "Current delivery contains a nonarchive: " + name)
        require_approved(names, approved)
        public = parse_sums(committed("SHA256SUMS.txt").decode("utf-8"))
        _require(names <= public.keys(), "Current delivery is missing public SHA-256 pins")
        outputs = metadata_outputs(root, version)
        require_approved(outputs, approved)
        for name, expected in outputs.items():
            _require(committed(name) == expected, "Generated product documentation is stale: " + name)
        rows = {}
        for row in metadata_products(root, version):
            if row.get("path") in names:
                _require(row["path"] not in rows, "Duplicate current product path: " + row["path"])
                rows[row["path"]] = row
        archives = {}
        records = []
        total = 0
        for name in sorted(names):
            payload = committed(name)
            _require(0 < len(payload) <= MAX_ASSET_BYTES, "Current archive exceeds the public size limit: " + name)
            total += len(payload)
            _require(total < MAX_TOTAL_BYTES, "Delivery exceeds the total byte limit")
            _require(sha256(payload).hexdigest() == public[name], "Public archive SHA-256 mismatch: " + name)
            _archive_crc(payload)
            archives[name] = payload
            records.append(_product(rows.get(name), name, payload, web_version))
    if validate:
        validate_readiness(root, version)
        validate_historical(root, version)
    # A check or concurrent editor must not move or dirty the source while the
    # trusted bytes and metadata are collected.
    _source(root, expected_commit)
    manifest = {"schemaVersion": 1, "sourceCommit": expected_commit, "webVersion": web_version,
                "proposedTag": f"web-v{web_version}-{expected_commit[:12]}",
                "publicationStatus": "prepared_for_review", "files": records}
    files = {**archives, MANIFEST: json_bytes(manifest), NOTES: _notes(manifest)}
    files[SUMS] = sums_bytes(files)
    return root, manifest, files


def _bundle_names(directory):
    """An exact inventory, including empty directories and nonregular entries."""
    names, directories = set(), set()
    for parent, folders, files in os.walk(directory, followlinks=False):
        for name in folders:
            path = Path(parent) / name
            _require(stat.S_ISDIR(path.lstat().st_mode) and not path.is_symlink(),
                     "Delivery contains a symbolic link or special directory")
            directories.add(path.relative_to(directory).as_posix())
        for name in files:
            path = Path(parent) / name
            _require(stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(),
                     "Delivery contains a symbolic link or special file")
            names.add(path.relative_to(directory).as_posix())
    return names, directories


def _verify_files(output, files):
    output = _without_links(output)
    with DeliveryFiles(output) as delivery:
        names, directories = _bundle_names(output)
        _require(names == set(files), "Delivery file inventory differs from the trusted manifest")
        expected_directories = {parent.as_posix() for name in files for parent in Path(name).parents if parent != Path(".")}
        _require(directories == expected_directories, "Delivery contains unlisted directories")
        for name, expected in files.items():
            payload = delivery.read(name)
            _require(payload == expected, "Delivery bytes or metadata differ from the trusted source: " + name)
            if Path(name).suffix.lower() in ARCHIVE_SUFFIXES:
                _archive_crc(payload)


def verify_bundle(output, expected_commit, *, root=ROOT):
    """Verify exact files, bytes, metadata and every nested CRC against trusted Git."""
    _, manifest, files = _collect(root, expected_commit, validate=False)
    _verify_files(Path(output), files)
    return manifest


def prepare_bundle(root=ROOT, *, expected_commit, output=None, check=False):
    """Validate without writing, or create an immutable, deterministic delivery."""
    _require(not (check and output is not None), "--check cannot write an output directory")
    _require(check or output is not None, "Preparation requires an explicit output directory")
    root, manifest, files = _collect(root, expected_commit)
    if check:
        return manifest
    output = _without_links(output)
    _require(not output.is_relative_to(root), "Place the delivery outside the source checkout")
    _require(output.parent.is_dir(), "The output parent directory must already exist")
    if output.exists():
        # Only a complete identical delivery is ours. Never adopt or overwrite
        # even an empty caller-owned directory.
        _verify_files(output, files)
        return manifest
    _write_new_output(output, files)
    _source(root, expected_commit)
    _verify_files(output, files)
    return manifest


def _write_new_output(output, files):
    """Claim a new directory and write exclusively through no-follow descriptors.

    Every component is opened relative to a retained directory descriptor. A
    concurrent pathname replacement cannot redirect a writer into another tree.
    Existing destinations and files are never overwritten.
    """
    _require(os.open in os.supports_dir_fd and os.mkdir in os.supports_dir_fd
             and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
             "Release preparation requires descriptor-relative no-follow file support")
    descriptors = []
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        parent = os.open(output.anchor, flags)
        descriptors.append(parent)
        for part in output.parent.parts[1:]:
            parent = os.open(part, flags, dir_fd=parent)
            descriptors.append(parent)
        os.mkdir(output.name, dir_fd=parent)
        destination = os.open(output.name, flags, dir_fd=parent)
        descriptors.append(destination)
        identity = os.fstat(destination)
        opened = {(): destination}
        for name, payload in files.items():
            parts = safe_name(name).parts
            current = destination
            for index, part in enumerate(parts[:-1], 1):
                prefix = parts[:index]
                if prefix not in opened:
                    os.mkdir(part, dir_fd=current)
                    opened[prefix] = os.open(part, flags, dir_fd=current)
                    descriptors.append(opened[prefix])
                current = opened[prefix]
            descriptor = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o644, dir_fd=current)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
        _require(os.path.samestat(identity, os.stat(output.name, dir_fd=parent, follow_symlinks=False)),
                 "Output directory changed during preparation")
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-commit", required=True, help="Exact lowercase 40-character Git HEAD")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Read-only readiness validation")
    mode.add_argument("--output", type=Path, help="New delivery directory, or a byte-identical existing delivery")
    mode.add_argument("--verify-output", type=Path, help="Verify delivery against the trusted source checkout")
    args = parser.parse_args(argv)
    try:
        if args.verify_output is not None:
            manifest = verify_bundle(args.verify_output, args.source_commit, root=args.root)
            mode_name = "verified"
        else:
            manifest = prepare_bundle(args.root, expected_commit=args.source_commit,
                                      output=args.output, check=args.check)
            mode_name = "checked" if args.check else "prepared"
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        print(f"Release preparation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"mode": mode_name, "sourceCommit": manifest["sourceCommit"],
                      "proposedTag": manifest["proposedTag"], "archives": len(manifest["files"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
