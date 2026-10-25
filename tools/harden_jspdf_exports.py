#!/usr/bin/env python3
"""Pin native eXeLearning PDF loaders without rebuilding exported projects.

Uses only the standard library and the reviewed dependency manifest. No download
is needed. --check is read-only; --artifact handles a fresh editor ELPX/HTML ZIP.
Reapply this tool after editor saves/exports that restore the editor's loaders.
The global mode is read-only and follows the checked public inventory. Use
--artifact explicitly when hardening a newly edited copy of one project.
"""
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
VERSION = "4.2.1"
URL = "https://cdn.jsdelivr.net/npm/jspdf@4.2.1/dist/jspdf.umd.min.js"
INTEGRITY = "sha384-qovJwSBbRDPP5cEjCp8S0UP66wrvnjaa60XMOGzTNanrThcrGfXfnZkvgY8N1KT3"
CROSS_ORIGIN = "anonymous"
UMD_BYTES = 420165
UMD_SHA256 = "e6551fcdc32f09d6853b2c5126d18d01d9447e0da618a41a11ebeee0f6c20d54"
NPM_TARBALL_INTEGRITY = "sha512-YyAXyvnmjTbR4bHQRLzex3CuINCDlQnBqoSYyjJwTP2x9jDLuKDzy7aKUl0hgx3uhcl7xzg32agn5vlie6HIlQ=="
OLD_URL = "https://cdn.jsdelivr.net/npm/jspdf/dist/jspdf.umd.min.js"
SCRIPT_PATHS = frozenset({
    "idevices/progress-report/progress-report.js",
    "idevices/checklist/checklist.js",
    "idevices/rubric/rubric.js",
})
LOADER_START = "ensureJsPDF: function (onReady, onError) {"
OLD_ASSIGNMENT = f"        s.src = '{OLD_URL}';"
ASSIGNMENTS = (
    f"        s.src = '{URL}';",
    f"        s.integrity = '{INTEGRITY}';",
    f"        s.crossOrigin = '{CROSS_ORIGIN}';",
)
NEW_ASSIGNMENTS = "\n".join(ASSIGNMENTS)
APPEND = "document.head.appendChild(s);"
JSPDF_SOURCE = re.compile(r"\b[\w.]+\.src\s*=\s*(['\"])[^'\"\n]*jspdf[^'\"\n]*\1")
ZIP_INFO_FIELDS = (
    "filename", "date_time", "compress_type", "create_system", "create_version",
    "extract_version", "external_attr", "internal_attr", "extra", "comment", "flag_bits",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def verify_dependency_manifest(path: Path = ROOT / "JSPDF_DEPENDENCY.json") -> None:
    expected = {
        "version": VERSION, "url": URL, "integrity": INTEGRITY,
        "cross_origin": CROSS_ORIGIN, "umd_bytes": UMD_BYTES, "umd_sha256": UMD_SHA256,
        "npm_tarball_integrity": NPM_TARBALL_INTEGRITY, "license": "MIT",
    }
    require(json.loads(path.read_text("utf-8")) == expected,
            "jsPDF dependency manifest differs from the reviewed release")


def loader_bounds(text: str) -> tuple[int, int]:
    require(text.count(LOADER_START) == 1, "Expected one native ensureJsPDF boundary")
    start = text.index(LOADER_START)
    end = text.find("\n    },", start)
    require(end != -1, "Missing native ensureJsPDF closing boundary")
    return start, end


def verify_loader(text: str) -> None:
    start, end = loader_bounds(text)
    loader = text[start:end]
    require(OLD_URL not in text, "Unversioned jsPDF URL remains")
    require(text.count(URL) == 1 and len(JSPDF_SOURCE.findall(text)) == 1,
            "Unexpected jsPDF source assignment")
    for property_name, assignment in zip(("src", "integrity", "crossOrigin"), ASSIGNMENTS):
        require(loader.count(assignment) == 1
                and len(re.findall(r"\bs\." + property_name + r"\s*=", loader)) == 1,
                "Missing or altered jsPDF " + property_name)
    require(loader.count(APPEND) == 1, "Expected one jsPDF script insertion")
    positions = [loader.index(assignment) for assignment in ASSIGNMENTS] + [loader.index(APPEND)]
    require(positions == sorted(positions), "jsPDF attributes must be set before insertion")


def patch_loader(text: str) -> str:
    """Replace only the exact native unversioned source line; keep other bytes."""
    start, end = loader_bounds(text)
    loader = text[start:end]
    if OLD_URL not in text:
        verify_loader(text)
        return text
    require(text.count(OLD_ASSIGNMENT) == 1 and text.count(OLD_URL) == 1
            and OLD_ASSIGNMENT in loader, "Unknown native jsPDF source variant")
    require(not re.search(r"\bs\.(?:integrity|crossOrigin)\s*=", loader),
            "Unexpected preexisting jsPDF security attributes")
    require(loader.count(APPEND) == 1 and loader.index(OLD_ASSIGNMENT) < loader.index(APPEND),
            "jsPDF source must be set before insertion")
    result = text[:start] + loader.replace(OLD_ASSIGNMENT, NEW_ASSIGNMENTS, 1) + text[end:]
    verify_loader(result)
    return result


def harden_directory(folder: Path) -> int:
    """Harden an extracted export before the builder creates its file manifest."""
    count = 0
    for name in sorted(SCRIPT_PATHS):
        path = folder / name
        if path.is_file():
            before = path.read_bytes()
            after = patch_loader(before.decode("utf-8")).encode("utf-8")
            if after != before:
                path.write_bytes(after)
            count += 1
    require(count > 0, "No native jsPDF export loaders found")
    return count


def read_archive(payload: bytes):
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        require(archive.testzip() is None, "Archive CRC validation failed")
        infos = archive.infolist()
        names = [info.filename for info in infos]
        require(len(names) == len(set(names)), "Archive has duplicate paths")
        files = {info.filename: archive.read(info) for info in infos}
        return infos, files, archive.comment


class PreservingZipFile(zipfile.ZipFile):
    """Retain editor ZIP flags/zero attributes that ZipFile normally resets.

    Some native editor exports use data descriptors even in seekable archives.
    Restoring flag 8 before the write handle closes makes ZipFile emit that
    descriptor as well. The updated local header and central directory agree.
    """

    def _open_to_write(self, info, force_zip64=False):
        flags, attributes = info.flag_bits, info.external_attr
        require(not flags & 1, "Encrypted exports are unsupported")
        handle = super()._open_to_write(info, force_zip64=force_zip64)
        info.flag_bits, info.external_attr = flags, attributes
        position = self.fp.tell()
        self.fp.seek(info.header_offset)
        self.fp.write(info.FileHeader(handle._zip64))
        require(self.fp.tell() == position, "ZIP local header size changed")
        return handle


def write_archive(infos, files, comment: bytes) -> bytes:
    buffer = BytesIO()
    with PreservingZipFile(buffer, "w") as output:
        output.comment = comment
        for info in infos:
            output.writestr(copy.copy(info), files[info.filename])
    result = buffer.getvalue()
    actual_infos, actual_files, actual_comment = read_archive(result)
    require(actual_files == files and actual_comment == comment, "Repacked archive bytes differ")
    require(all(all(getattr(before, name) == getattr(after, name) for name in ZIP_INFO_FIELDS)
                for before, after in zip(infos, actual_infos, strict=True)),
            "ZIP entry metadata changed")
    return result


def check_other_script(name: str, payload: bytes) -> None:
    if not name.lower().endswith(".js"):
        return
    text = payload.decode("utf-8")
    require(OLD_URL not in text and LOADER_START not in text and not JSPDF_SOURCE.search(text),
            "Unreviewed jsPDF loader outside native boundaries: " + name)


def patched_archive(payload: bytes) -> tuple[bytes, int, int]:
    infos, files, comment = read_archive(payload)
    before = dict(files)
    loaders = nested_elpx = 0
    allowed = set()
    for name, data in before.items():
        if name in SCRIPT_PATHS:
            files[name] = patch_loader(data.decode("utf-8")).encode("utf-8")
            loaders += 1
            allowed.add(name)
        elif name.lower().endswith((".elpx", ".zip")):
            files[name], count, nested = patched_archive(data)
            loaders += count
            nested_elpx += nested + int(name.lower().endswith(".elpx"))
            allowed.add(name)
        else:
            check_other_script(name, data)
    require(all(files[name] == before[name] for name in files if name not in allowed),
            "Unrelated native/archive member changed")
    result = write_archive(infos, files, comment) if files != before else payload
    return result, loaders, nested_elpx


def verify_archive(payload: bytes) -> tuple[int, int]:
    _, files, _ = read_archive(payload)
    loaders = nested_elpx = 0
    for name, data in files.items():
        if name in SCRIPT_PATHS:
            verify_loader(data.decode("utf-8"))
            loaders += 1
        elif name.lower().endswith((".elpx", ".zip")):
            count, nested = verify_archive(data)
            loaders += count
            nested_elpx += nested + int(name.lower().endswith(".elpx"))
        else:
            check_other_script(name, data)
    return loaders, nested_elpx


def public_archives(root: Path) -> list[Path]:
    """Resolve the current archive allowlist without trusting a release count."""
    # The explicit single-artifact tool remains standalone (stdlib + manifest).
    # Only repository-wide inventory checks need the release helper module.
    from release_support import MAX_ASSET_BYTES, parse_sums, source_path
    inventory = parse_sums((root / "SHA256SUMS.txt").read_text("utf-8"))
    names = {name for name in inventory
             if name.startswith("downloads/") and Path(name).suffix.lower() in {".zip", ".elpx"}}
    present = {path.relative_to(root).as_posix() for path in (root / "downloads").rglob("*")
               if path.suffix.lower() in {".zip", ".elpx"}}
    require(bool(names) and names == present, "Public archive inventory differs from SHA256SUMS.txt")
    paths = []
    for name in sorted(names):
        path = source_path(root, name)
        require(path.stat().st_size <= MAX_ASSET_BYTES, "Public archive exceeds the hosting size limit")
        require(digest(path.read_bytes()) == inventory[name], "Checksum mismatch: " + name)
        paths.append(path)
    return paths


def verify_public_archives(root: Path) -> dict:
    """Check every published/nested loader and the current native projects."""
    from release_support import source_path
    paths = public_archives(root)
    affected = loaders = nested_elpx = direct_loaders = 0
    checked = {}
    for path in paths:
        payload = path.read_bytes()
        count, nested = verify_archive(payload)
        checked[path.relative_to(root).as_posix()] = count
        affected += bool(count)
        loaders += count
        nested_elpx += nested
        if path.suffix.lower() == ".elpx":
            with zipfile.ZipFile(BytesIO(payload)) as archive:
                direct = len(SCRIPT_PATHS & set(archive.namelist()))
            require(direct > 0, "Native public archive has no reviewed PDF loaders: " + path.name)
            direct_loaders += direct
    version = json.loads((root / "VERSION.json").read_text("utf-8"))
    for record in [version["download"], *version.get("presets", [])]:
        name = record["path"]
        require(name in checked, "The current native project is missing from the public archive inventory: " + name)
        payload = source_path(root, name).read_bytes()
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            require(SCRIPT_PATHS <= set(archive.namelist()),
                    "The current native project must retain all reviewed PDF loaders at their root paths: " + name)
            for script in SCRIPT_PATHS:
                verify_loader(archive.read(script).decode("utf-8"))
        require(record["sha256"] == digest(payload) and record["bytes"] == len(payload),
                "Stale release download metadata: " + name)
    return {"public_archives": len(paths), "affected_archives": affected,
            "loaders": loaders, "direct_loaders": direct_loaders,
            "nested_loaders": loaders - direct_loaders, "nested_elpx": nested_elpx}


def checksum_text(directory: Path, text: str) -> str:
    lines = []
    for line in text.splitlines():
        old, separator, name = line.partition("  ")
        require(separator == "  " and re.fullmatch(r"[0-9a-f]{64}", old) is not None,
                "Invalid delivery checksum entry")
        lines.append(digest((directory / name).read_bytes()) + separator + name)
    return "\n".join(lines) + "\n"


def delivery_update(directory: Path, check: bool) -> None:
    native = directory / "MitoMapa_canario_GobCan.elpx"
    exported = directory / "MitoMapa_canario_GobCan_HTML.zip"
    validation = directory / "VALIDACION_GOBCAN.txt"
    sums = directory / "SHA256SUMS.txt"
    bundle = directory / "Entrega_MitoMapa_GobCan.zip"
    if not check:
        native_bytes, loaders, _ = patched_archive(native.read_bytes())
        require(loaders == 3 and native_bytes == (ROOT / "downloads" / native.name).read_bytes(),
                "Delivery/public ELPX copies differ")
        exported_bytes, loaders, _ = patched_archive(exported.read_bytes())
        require(loaders == 3, "Unexpected delivery HTML PDF loader inventory")
        native.write_bytes(native_bytes)
        exported.write_bytes(exported_bytes)
        text = validation.read_text("utf-8")
        for prefix, data in [("ELPX SHA-256: ", native_bytes), ("HTML ZIP SHA-256: ", exported_bytes)]:
            pattern = "^" + re.escape(prefix) + r"[0-9a-f]{64}$"
            require(len(re.findall(pattern, text, re.M)) == 1, "Missing explicit validation digest")
            text = re.sub(pattern, prefix + digest(data), text, flags=re.M)
        validation.write_text(text, "utf-8")
        sums.write_text(checksum_text(directory, sums.read_text("utf-8")), "utf-8")
        infos, files, comment = read_archive(bundle.read_bytes())
        before = dict(files)
        allowed = {native.name, exported.name, validation.name, sums.name}
        for name in allowed:
            require(name in files, "Delivery bundle is missing " + name)
            files[name] = (directory / name).read_bytes()
        require(all(files[name] == before[name] for name in files if name not in allowed),
                "Unrelated delivery document changed")
        if files != before:
            bundle.write_bytes(write_archive(infos, files, comment))
    require(native.read_bytes() == (ROOT / "downloads" / native.name).read_bytes(),
            "Delivery/public ELPX copies differ")
    require(all(verify_archive(path.read_bytes()) == (3, 0) for path in (native, exported)),
            "Unexpected delivery PDF loader inventory")
    require(sums.read_text("utf-8") == checksum_text(directory, sums.read_text("utf-8")),
            "Delivery checksums are stale")
    for prefix, path in [("ELPX SHA-256: ", native), ("HTML ZIP SHA-256: ", exported)]:
        require(prefix + digest(path.read_bytes()) in validation.read_text("utf-8"),
                "Delivery validation hash is stale")
    _, files, _ = read_archive(bundle.read_bytes())
    require(all(data == (directory / name).read_bytes() for name, data in files.items()),
            "Nested delivery files differ from final copies")
    require(verify_archive(bundle.read_bytes()) == (6, 1), "Delivery bundle PDF policy is stale")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without changing files")
    parser.add_argument("--delivery-dir", type=Path, help="Include the final presentation package")
    parser.add_argument("--artifact", type=Path, help="Only check/harden one editor ELPX or HTML ZIP")
    args = parser.parse_args()
    verify_dependency_manifest()
    require(not (args.artifact and args.delivery_dir), "Use --artifact or --delivery-dir separately")
    if args.artifact:
        path = args.artifact.resolve()
        before = path.read_bytes()
        if args.check:
            loaders, nested = verify_archive(before)
        else:
            after, loaders, nested = patched_archive(before)
            if after != before:
                path.write_bytes(after)
        require(loaders > 0, "No native jsPDF export loaders found")
        print(json.dumps({"mode": "checked" if args.check else "updated", "artifact": str(path),
                          "loaders": loaders, "nested_elpx": nested}))
        return
    require(args.check, "Global mode is read-only; use --check or explicitly harden one --artifact copy")
    summary = verify_public_archives(ROOT)
    if args.delivery_dir:
        delivery_update(args.delivery_dir.resolve(), True)
    print(json.dumps({"mode": "checked", **summary,
                      "native_XML_search_pages_media_preserved": True,
                      "delivery_included": bool(args.delivery_dir)}))


if __name__ == "__main__":
    main()
