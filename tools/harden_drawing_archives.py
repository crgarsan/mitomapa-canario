#!/usr/bin/env python3
"""Patch distributed drawing routines without rebuilding their native projects.

The maintained CLI is read-only: --check verifies the reviewed drawing helpers
and import guards in the public inventory, including nested archives. It does
not require old Git commits or rewrite historical downloads. The lower-level
migration helpers remain available for the historical one-time migration;
they are not used by the current check or the normal publication pipeline.
"""
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import zipfile

from harden_jspdf_exports import (
    ArchiveBudget, SCRIPT_PATHS as JSPDF_SCRIPT_PATHS, patch_loader, public_archives,
    read_archive, read_archive_file,
)
from release_support import MAX_ASSET_BYTES, parse_sums, source_path


ROOT = Path(__file__).resolve().parent.parent
HELPER_MARKER = "// Comprueba los contenedores completos antes de que el navegador decodifique un dibujo.\n"
STORAGE = 'const workshopStorageKey="mitomapa-canario-cuaderno-v1";'
ROUTES_GUARD = 'if(!workshopState.routes||typeof workshopState.routes!=="object")workshopState.routes={};'
CONFIRM = '  if(!confirm("¿Quieres sustituir el progreso de este navegador por el del archivo seleccionado?")){status.textContent="Importación cancelada.";return;}'
PORTABLE = "content/resources/mitomapa/"
NATIVE_NAMES = {
    "MitoMapa_canario_GobCan.elpx",
    "MitoMapa_canario_REA_eXeLearning_v4_4_0.elpx",
    "MitoMapa_REA_v4_4_0_Esencial.elpx",
    "MitoMapa_REA_v4_4_0_Intermedio.elpx",
}
BASELINE_REF = "HEAD"


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def once(text: str, anchor: str) -> None:
    require(text.count(anchor) == 1, f"Expected one anchor: {anchor[:90]!r}")


def function(text: str, name: str) -> str:
    match = re.search(r"^(?:async )?function " + re.escape(name) + r"\(", text, re.M)
    require(match is not None, f"Missing function {name}")
    following = re.search(r"^(?:async )?function \w+\(", text[match.end():], re.M)
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]


def line(text: str, prefix: str) -> str:
    found = [value for value in text.splitlines(keepends=True) if value.startswith(prefix)]
    require(len(found) == 1, f"Expected one line starting {prefix!r}")
    return found[0]


def between(text: str, start: str, end: str) -> str:
    once(text, start)
    once(text, end)
    a = text.index(start) + len(start)
    b = text.index(end, a)
    return text[a:b]


def replace_region(text: str, old: str, new: str) -> str:
    once(text, old)
    return text.replace(old, new, 1)


def git_bytes(name: str, reference: str | None = None) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{reference or BASELINE_REF}:{name}"])


def original_root() -> str:
    """Also support --check after the hardening itself has been committed."""
    global BASELINE_REF
    baseline = git_bytes("scripts.js", "HEAD").decode("utf-8")
    if HELPER_MARKER not in baseline:
        BASELINE_REF = "HEAD"
        return baseline
    commits = subprocess.check_output(["git", "-C", str(ROOT), "rev-list", "HEAD"], text=True)
    for commit in commits.splitlines():
        baseline = git_bytes("scripts.js", commit).decode("utf-8")
        if HELPER_MARKER not in baseline:
            BASELINE_REF = commit
            return baseline
    raise ValueError("The original drawing baseline is unavailable in Git history")


def drawing_patch(candidate: str):
    """Derive reviewed replacements, retaining every historical surrounding line."""
    baseline = original_root()
    once(candidate, HELPER_MARKER)
    once(candidate, STORAGE)
    helpers = candidate[candidate.index(HELPER_MARKER):candidate.index(STORAGE)]
    require("function drawingImageSize(" in helpers and "async function normalizeImportedDrawings(" in helpers,
            "Current drawing helpers are incomplete")
    startup = between(candidate, ROUTES_GUARD, "\n\nfunction activityEscape(")
    require("removeUnsafeWorkshopDrawings(workshopState)" in startup, "Missing startup purge")
    old_getter = line(function(baseline, "getWorkshopRouteState"), " state.drawing=")
    new_getter = line(function(candidate, "getWorkshopRouteState"), " state.drawing=")
    old_restore = line(function(baseline, "setupWorkshopCanvas"), " const restore=")
    new_restore = line(function(candidate, "setupWorkshopCanvas"), " const restore=")
    source_line = line(function(baseline, "sanitizeImportedWorkshop"), "  const source=")
    old_drawing = between(function(baseline, "sanitizeImportedWorkshop"), source_line, "  clean.routes[")
    new_drawing = between(function(candidate, "sanitizeImportedWorkshop"), source_line, "  clean.routes[")
    old_import = function(baseline, "importProgressFile")
    new_import = function(candidate, "importProgressFile")
    preparation = between(new_import, CONFIRM, "  sourcePassed=")
    require("await normalizeImportedDrawings(sanitizeImportedWorkshop(payload.workshop))" in preparation,
            "Import must normalize drawings before changing progress")
    old_assignment = line(old_import, "  workshopState=")
    new_assignment = line(new_import, "  workshopState=")
    old_catch = line(old_import, " }catch(error){status.textContent=")
    new_catch = line(new_import, " }catch(error){status.textContent=")
    require("safeWorkshopDrawing" in new_getter and "loadWorkshopDrawing" in new_restore
            and "DRAWING_INVALID" in new_drawing and "DRAWING_INVALID" in new_catch,
            "Current drawing guard replacements are incomplete")

    def patch(text: str) -> str:
        original_header = text.splitlines()[0]
        once(text, STORAGE)
        if HELPER_MARKER in text:
            once(text, HELPER_MARKER)
            old_helpers = text[text.index(HELPER_MARKER):text.index(STORAGE)]
            text = replace_region(text, old_helpers, helpers)
        else:
            require("function drawingImageSize(" not in text, "Unknown preexisting drawing helper")
            text = replace_region(text, STORAGE, helpers + STORAGE)
        old_startup = between(text, ROUTES_GUARD, "\n\nfunction activityEscape(")
        require(old_startup == "" or "removeUnsafeWorkshopDrawings(workshopState)" in old_startup,
                "Unknown startup region")
        text = replace_region(text, ROUTES_GUARD + old_startup, ROUTES_GUARD + startup)
        getter = line(function(text, "getWorkshopRouteState"), " state.drawing=")
        require(getter == old_getter or "safeWorkshopDrawing(state.drawing)" in getter,
                "Unknown drawing getter variant")
        text = replace_region(text, getter, new_getter)
        restore = line(function(text, "setupWorkshopCanvas"), " const restore=")
        require(restore == old_restore or "loadWorkshopDrawing(imageData)" in restore,
                "Unknown canvas restore variant")
        text = replace_region(text, restore, new_restore)
        drawing = between(function(text, "sanitizeImportedWorkshop"), source_line, "  clean.routes[")
        require(drawing == old_drawing or ("safeWorkshopDrawing(source.drawing)" in drawing
                and "DRAWING_INVALID" in drawing), "Unknown imported drawing variant")
        text = replace_region(text, source_line + drawing, source_line + new_drawing)
        imported = function(text, "importProgressFile")
        existing = between(imported, CONFIRM, "  sourcePassed=")
        require(existing == "\n" or "const importedWorkshop=await normalizeImportedDrawings(" in existing,
                "Unknown import preparation variant")
        text = replace_region(text, CONFIRM + existing, CONFIRM + preparation)
        assignment = line(function(text, "importProgressFile"), "  workshopState=")
        require(assignment in (old_assignment, new_assignment), "Unknown workshop assignment variant")
        text = replace_region(text, assignment, new_assignment)
        caught = line(function(text, "importProgressFile"), " }catch(error){status.textContent=")
        require(caught == old_catch or "DRAWING_INVALID" in caught, "Unknown import error variant")
        text = replace_region(text, caught, new_catch)
        require(text.splitlines()[0] == original_header, "Historical version header changed")
        verify(text)
        return text

    def verify(text: str) -> None:
        require(between(text, HELPER_MARKER, STORAGE) == helpers.removeprefix(HELPER_MARKER),
                "Distributed helpers do not match current scripts.js")
        for anchor in (new_getter, new_restore, new_drawing, preparation, new_assignment, new_catch):
            once(text, anchor)
        for unsafe in (old_getter, old_restore, old_drawing, old_assignment, old_catch):
            require(unsafe not in text, "Old drawing guard remains")
        require(between(text, ROUTES_GUARD, "\n\nfunction activityEscape(") == startup,
                "Missing drawing startup purge")
        imported = function(text, "importProgressFile")
        require(imported.index("await normalizeImportedDrawings(") < imported.index("  sourcePassed=")
                < imported.index(new_assignment), "Import mutates state before drawing validation")

    require(patch(baseline) == candidate, "Root script contains changes outside the narrow drawing patch")
    return patch, verify


def drawing_policy(candidate: str):
    """Keep image/import checks exact while allowing unrelated later features."""
    once(candidate, HELPER_MARKER)
    once(candidate, STORAGE)
    helpers = between(candidate, HELPER_MARKER, STORAGE)
    require("function drawingImageSize(" in helpers
            and "async function normalizeImportedDrawings(" in helpers,
            "Current drawing helpers are incomplete")
    getter = line(function(candidate, "getWorkshopRouteState"), " state.drawing=")
    restore = line(function(candidate, "setupWorkshopCanvas"), " const restore=")
    sanitizer = function(candidate, "sanitizeImportedWorkshop")
    source = line(sanitizer, "  const source=")
    guard = between(sanitizer, source, "  clean.routes[")
    require("safeWorkshopDrawing(state.drawing)" in getter and "loadWorkshopDrawing(imageData)" in restore
            and "safeWorkshopDrawing(source.drawing)" in guard and "DRAWING_INVALID" in guard,
            "Current drawing entry points are incomplete")
    preparation = "const importedWorkshop=await normalizeImportedDrawings(sanitizeImportedWorkshop(payload.workshop));"
    assignment = "workshopState=importedWorkshop;"

    def verify(text: str) -> None:
        require(between(text, HELPER_MARKER, STORAGE) == helpers,
                "Distributed drawing helpers differ from the reviewed policy")
        for anchor in (getter, restore):
            once(text, anchor)
        current = function(text, "sanitizeImportedWorkshop")
        require(between(current, source, "  clean.routes[") == guard,
                "Imported drawing validation differs from the reviewed policy")
        startup = between(text, ROUTES_GUARD, "\n\nfunction activityEscape(")
        require("removeUnsafeWorkshopDrawings(workshopState)" in startup,
                "Missing drawing startup purge")
        imported = function(text, "importProgressFile")
        once(imported, preparation)
        once(imported, assignment)
        workshop_assignments = list(re.finditer(
            r"(?<![\w.])workshopState\s*(?:=(?!=)|(?:\*\*|>>>|<<|>>|&&|\|\||\?\?|[+*/%&|^\-])=|\+\+|--)",
            imported))
        require(len(workshop_assignments) == 1
                and workshop_assignments[0].start() == imported.index(assignment),
                "The import must have one workshopState assignment, from the prepared workshop")
        require("DRAWING_INVALID" in imported and "file.size>5000000" in imported,
                "The import size/error guards are incomplete")
        prepared_at = imported.index(preparation)
        mutations = [match.start() for match in re.finditer(
            r"(?<![\w.])(?:sourcePassed|truthPassed|earned|learningLevel|learnerName|workshopState|finalState|itineraries)\s*=(?!=)",
            imported)]
        mutations += [match.start() for match in re.finditer(r"\bclearLearnerResponses\s*\(", imported)]
        require(bool(mutations) and all(prepared_at < position for position in mutations)
                and prepared_at < imported.index(assignment),
                "Import mutates progress before drawing validation")

    verify(candidate)
    return verify


def verify_drawing_archive(payload: bytes, verify, *, budget: ArchiveBudget | None = None,
                           depth: int = 0) -> tuple[int, int]:
    """Verify drawing entry points in this archive and every nested release."""
    if budget is None:
        budget = ArchiveBudget()
    _, files, _ = read_archive(payload, budget=budget, depth=depth)
    scripts = nested_archives = 0
    for name, data in files.items():
        if (name == "scripts.js" or name.endswith("/scripts.js")) and b"function sanitizeImportedWorkshop(" in data:
            verify(data.decode("utf-8"))
            scripts += 1
            portable = str(Path(name).parent / "PORTABLE_MANIFEST.json")
            if portable in files:
                manifest = json.loads(files[portable])
                require(manifest["assets"]["scripts.js"] == {"sha256": digest(data), "bytes": len(data)},
                        "Stale drawing manifest: " + name)
        elif name.lower().endswith((".elpx", ".zip")):
            found, nested = verify_drawing_archive(data, verify, budget=budget, depth=depth + 1)
            scripts += found
            nested_archives += nested + 1
    return scripts, nested_archives


def verify_delivery(directory: Path, verify) -> None:
    """Check an optional delivery without invoking the historical migrator."""
    native = directory / "MitoMapa_canario_GobCan.elpx"
    require(read_archive_file(native) == read_archive_file(ROOT / "downloads" / native.name),
            "Delivery/public ELPX copies differ")
    for path in directory.iterdir():
        if path.suffix in {".zip", ".elpx"}:
            verify_drawing_archive(read_archive_file(path), verify)
    for name, expected in parse_sums((directory / "SHA256SUMS.txt").read_text("utf-8")).items():
        require(digest(read_archive_file(source_path(directory, name))) == expected,
                "Stale delivery checksum: " + name)


def write_archive(infos, files, comment: bytes) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as output:
        output.comment = comment
        for info in infos:
            output.writestr(copy.copy(info), files[info.filename])
    result = buffer.getvalue()
    new_infos, actual, actual_comment = read_archive(result)
    require(actual == files and actual_comment == comment, "Repacked archive differs from prepared bytes")
    preserved = ("filename", "date_time", "compress_type", "create_system", "create_version",
                 "extract_version", "external_attr", "internal_attr", "extra", "comment", "flag_bits")
    require(all(all(getattr(a, name) == getattr(b, name) for name in preserved)
                for a, b in zip(infos, new_infos, strict=True)), "ZIP entry metadata changed")
    return result


def patched_archive(payload: bytes, patch, verify):
    infos, files, comment = read_archive(payload)
    before = dict(files)
    script_paths = [name for name in files if name == "scripts.js" or name.endswith("/scripts.js")]
    affected = [name for name in script_paths if "function sanitizeImportedWorkshop(" in files[name].decode("utf-8")]
    require(len(affected) <= 1, "Unexpected multiple drawing scripts in archive")
    if not affected:
        return payload, None
    script = affected[0]
    files[script] = patch(files[script].decode("utf-8")).encode("utf-8")
    allowed = {script}
    portable = str(Path(script).parent / "PORTABLE_MANIFEST.json")
    if portable in files:
        manifest = json.loads(files[portable])
        manifest["assets"]["scripts.js"] = {"sha256": digest(files[script]), "bytes": len(files[script])}
        files[portable] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        allowed.add(portable)
    changed = {name for name in files if files[name] != before[name]}
    require(changed <= allowed, "Unrelated archive entry changed")
    require(all(files[name] == before[name] for name in files if name not in allowed),
            "Native content, media or historical features changed")
    verify(files[script].decode("utf-8"))
    return write_archive(infos, files, comment) if changed else payload, script


def verify_public(path: Path, patch, verify) -> bool:
    _, files, _ = read_archive(read_archive_file(path, max_bytes=MAX_ASSET_BYTES))
    script_paths = [name for name in files if name == "scripts.js" or name.endswith("/scripts.js")]
    affected = [name for name in script_paths if b"function sanitizeImportedWorkshop(" in files[name]]
    if not affected:
        return False
    require(len(affected) == 1, "Unexpected multiple public drawing scripts")
    script = affected[0]
    verify(files[script].decode("utf-8"))
    _, baseline, _ = read_archive(git_bytes(path.relative_to(ROOT).as_posix()))
    require(files[script] == patch(baseline[script].decode("utf-8")).encode("utf-8"),
            f"Historical script features/version changed: {path.name}")
    portable = str(Path(script).parent / "PORTABLE_MANIFEST.json")
    if portable in files:
        manifest = json.loads(files[portable])
        require(manifest["assets"]["scripts.js"] == {"sha256": digest(files[script]), "bytes": len(files[script])},
                f"Stale drawing manifest: {path.name}")
        allowed = {script, portable}
        require(files.keys() == baseline.keys(), f"Native archive inventory changed: {path.name}")
        require(all(files[name] == (patch_loader(baseline[name].decode("utf-8")).encode("utf-8")
                                   if name in JSPDF_SCRIPT_PATHS else baseline[name])
                    for name in files if name not in allowed),
                f"Native XML/search/pages/media changed: {path.name}")
    return True


def checksum_text(directory: Path, text: str) -> str:
    lines = []
    for entry in text.splitlines():
        old, separator, name = entry.partition("  ")
        require(separator == "  " and len(old) == 64, "Invalid delivery checksum entry")
        lines.append(digest(read_archive_file(directory / name)) + separator + name)
    return "\n".join(lines) + "\n"


def delivery_update(directory: Path, patch, verify, check: bool) -> None:
    native = directory / "MitoMapa_canario_GobCan.elpx"
    exported = directory / "MitoMapa_canario_GobCan_HTML.zip"
    validation = directory / "VALIDACION_GOBCAN.txt"
    bundle = directory / "Entrega_MitoMapa_GobCan.zip"
    if not check:
        native_before = read_archive_file(native)
        native_bytes, _ = patched_archive(native_before, patch, verify)
        require(native_bytes == read_archive_file(ROOT / "downloads" / native.name),
                "Delivery ELPX no longer matches public ELPX")
        exported_bytes, _ = patched_archive(read_archive_file(exported), patch, verify)
        native.write_bytes(native_bytes)
        exported.write_bytes(exported_bytes)
        text = validation.read_text("utf-8")
        for prefix, payload in [("ELPX SHA-256: ", native_bytes), ("HTML ZIP SHA-256: ", exported_bytes)]:
            pattern = re.escape(prefix) + r"[0-9a-f]{64}"
            require(len(re.findall(pattern, text)) == 1, "Missing explicit delivery validation digest")
            text = re.sub(pattern, prefix + digest(payload), text)
        validation.write_text(text, "utf-8")
        sums = directory / "SHA256SUMS.txt"
        sums.write_text(checksum_text(directory, sums.read_text("utf-8")), "utf-8")
        infos, files, comment = read_archive(read_archive_file(bundle))
        before = dict(files)
        for name in [native.name, exported.name, validation.name, sums.name]:
            require(name in files, "Delivery bundle is missing " + name)
            files[name] = read_archive_file(directory / name)
        allowed = {native.name, exported.name, validation.name, sums.name}
        require(all(files[name] == before[name] for name in files if name not in allowed),
                "Unrelated delivery document changed")
        if files != before:
            bundle.write_bytes(write_archive(infos, files, comment))
    require(read_archive_file(native) == read_archive_file(ROOT / "downloads" / native.name),
            "Delivery/public ELPX copies differ")
    for path in (native, exported):
        payload = read_archive_file(path)
        result, script = patched_archive(payload, patch, verify)
        require(result == payload and script == PORTABLE + "scripts.js", "Delivery drawing patch is stale")
    sums = directory / "SHA256SUMS.txt"
    require(sums.read_text("utf-8") == checksum_text(directory, sums.read_text("utf-8")),
            "Delivery checksums are stale")
    for prefix, path in [("ELPX SHA-256: ", native), ("HTML ZIP SHA-256: ", exported)]:
        require(prefix + digest(read_archive_file(path)) in validation.read_text("utf-8"),
                "Delivery validation hash is stale")
    _, files, _ = read_archive(read_archive_file(bundle))
    require(all(files[name] == read_archive_file(directory / name) for name in files),
            "Nested delivery files differ from final copies")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the current policy without changing files")
    parser.add_argument("--delivery-dir", type=Path, help="Also verify a presentation directory without changing it")
    args = parser.parse_args()
    require(args.check, "The maintained global mode is read-only; use --check")
    verify = drawing_policy((ROOT / "scripts.js").read_text("utf-8"))
    public = public_archives(ROOT)
    affected = drawing_scripts = nested_archives = 0
    for path in public:
        count, nested = verify_drawing_archive(read_archive_file(path, max_bytes=MAX_ASSET_BYTES), verify)
        affected += bool(count)
        drawing_scripts += count
        nested_archives += nested
    require(drawing_scripts > 0, "The public inventory contains no reviewed drawing import scripts")
    if args.delivery_dir:
        verify_delivery(args.delivery_dir.resolve(), verify)
    print(json.dumps({"mode": "checked", "public_archives": len(public),
                      "affected_archives": affected, "drawing_scripts": drawing_scripts,
                      "nested_archives": nested_archives,
                      "delivery_included": bool(args.delivery_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
