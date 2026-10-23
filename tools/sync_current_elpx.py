#!/usr/bin/env python3
"""Build the native GobCan project from its pinned source, independently of the web.

Editorial changes affect Text components, navigation and the stored project
thumbnail. Games, other media and native runtime dependencies are preserved;
--check is read-only and never repairs files.
"""
import argparse
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipInfo

from lxml import etree

from editorial_elpx import apply_editorial
from native_preservation import verify_component
from project_thumbnail import THUMBNAIL_MEMBERS, verify_project_thumbnail
from harden_jspdf_exports import ZIP_INFO_FIELDS, read_archive, write_archive
from release_support import MAX_ASSET_BYTES, digest, json_bytes, read_zip, source_path

ROOT = Path(__file__).resolve().parent.parent
NS = {"o": "http://www.intef.es/xsd/ode"}
PORTABLE = "content/resources/mitomapa/"
APP = "{{context_path}}/" + PORTABLE
MEDIA_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".wav", ".opus", ".woff", ".woff2", ".ico"}
MERGED_TEACHER_PAGES = {"GBC20261006CURRICULO", "GBC20261006METODO", "GBC20261006RECURSOS", "GBC20261006SEGUIMIENTO", "20260823155836LOCUT0"}


def field(node, name):
    return node.findtext("o:" + name, default="", namespaces=NS)


def native_structure(files):
    tree = etree.fromstring(files["content.xml"], etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True))
    return {
        "pages": [field(page, "odePageId") for page in tree.findall(".//o:odeNavStructure", NS)],
        "components": {field(node, "odeIdeviceId"): node for node in tree.findall(".//o:odeComponent", NS)},
    }


def version_module(version):
    values = {"version": version["web_version"], "reaVersion": version["rea_exelearning_version"], "schemaVersion": 1}
    return ("/* Generado a partir de VERSION.json. */\nwindow.MitoMapaVersion = Object.freeze(" + json.dumps(values, ensure_ascii=False, separators=(",", ":")) + ");\n").encode()


def verify_preservation(baseline, result):
    verify_project_thumbnail(result)
    before, after = native_structure(baseline), native_structure(result)
    if set(before["pages"]) - set(after["pages"]) != MERGED_TEACHER_PAGES or set(after["pages"]) - set(before["pages"]):
        raise ValueError("The editorial merge changed pages outside the five teacher sections")
    if set(before["components"]) != set(after["components"]):
        raise ValueError("The editorial revision lost or added a native activity identity")
    for iid, original in before["components"].items():
        current = after["components"][iid]
        kind = field(original, "odeIdeviceTypeName")
        if kind != field(current, "odeIdeviceTypeName"):
            raise ValueError(f"The editorial revision changed an activity type: {iid}")
        if kind != "text":
            verify_component(original, current, result)
    for name, payload in baseline.items():
        if name not in THUMBNAIL_MEMBERS and Path(name).suffix.lower() in MEDIA_EXTENSIONS and result.get(name) != payload:
            raise ValueError(f"The editorial revision changed a media asset: {name}")
        if name.startswith(("libs/", "idevices/", "theme/")) and name != "libs/elpx-manifest.js" and result.get(name) != payload:
            raise ValueError(f"The editorial revision changed a runtime dependency: {name}")


def build_current(root=ROOT):
    version = json.loads((root / "VERSION.json").read_text())
    if version.get("elpx_distribution", {}).get("mode") != "native_only":
        raise ValueError("The current ELPX must be explicitly independent of the web application")
    source = version["elpx_source"]
    payload = source_path(root, source["path"]).read_bytes()
    if digest(payload) != source["sha256"]:
        raise ValueError("The pinned source ELPX has changed")
    baseline = read_zip(payload)
    result = dict(baseline)
    apply_editorial(result, root, version)
    # Native recordings, scenes and badges keep their original resource URLs.
    # The former application's documents, scripts and manifests are excluded.
    for name in list(result):
        if name.startswith(PORTABLE) and Path(name).suffix.lower() not in MEDIA_EXTENSIONS:
            del result[name]
    structure = native_structure(result)
    result["EDITORIAL_MANIFEST.json"] = json_bytes({
        "edition": version["rea_exelearning_version"], "distribution": "native_only",
        "external_web": "https://mitomapa-canario.cgarcias.workers.dev/",
        "embedded_web_app": False, "pages": structure["pages"],
        "idevices": sorted(structure["components"]), "license": "CC-BY-SA-4.0",
    })
    # The inventory includes itself; it has no self-referential checksums.
    names = sorted(set(result) | {"libs/elpx-manifest.js"})
    result["libs/elpx-manifest.js"] = (
        b"/** Complete native MitoMapa project inventory. */\nwindow.__ELPX_MANIFEST__="
        + json_bytes({"version": 1, "files": names, "projectTitle": "MitoMapa canario: ocho islas, ocho piezas"}).rstrip() + b";\n"
    )
    tree = etree.fromstring(result["content.xml"], etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True))
    if not etree.DTD(BytesIO(result["content.dtd"])).validate(tree):
        raise ValueError("The editorial ODE model does not match its DTD")
    verify_preservation(baseline, result)
    return result, version


def current_zip_info(root, version, files):
    infos, _, comment = read_archive(source_path(root, version["elpx_source"]["path"]).read_bytes())
    # Preserve editor metadata for retained members; removed web files are not written.
    infos = [info for info in infos if info.filename in files]
    known = {info.filename for info in infos}
    for name in sorted(set(files) - known):
        entry = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = 0o644 << 16
        infos.append(entry)
    return infos, comment


def build_archive(root, version, files):
    infos, comment = current_zip_info(root, version, files)
    return write_archive(infos, files, comment)


def verify_zip_info(root, version, files, payload):
    expected, comment = current_zip_info(root, version, files)
    actual, _, actual_comment = read_archive(payload)
    if actual_comment != comment or len(expected) != len(actual):
        raise ValueError("The current ELPX changed its editor ZIP metadata")
    for before, after in zip(expected, actual, strict=True):
        if any(getattr(before, key) != getattr(after, key) for key in ZIP_INFO_FIELDS):
            raise ValueError(f"The current ELPX changed editor ZIP metadata: {before.filename}")


def synchronize(root=ROOT, *, check=False):
    files, version = build_current(root)
    destination = root / version["download"]["path"]
    module = version_module(version)
    module_path = root / "version.js"
    if check:
        if not module_path.is_file() or module_path.read_bytes() != module:
            raise ValueError("The version.js release module is not synchronized with VERSION.json")
        if destination.stat().st_size > MAX_ASSET_BYTES:
            raise ValueError("The current ELPX exceeds 25 MiB")
        payload = destination.read_bytes()
        actual = read_zip(payload)
        changed = sorted(name for name in set(files) | set(actual) if files.get(name) != actual.get(name))
        if changed:
            raise ValueError("The current ELPX is not synchronized: " + ", ".join(changed[:12]))
        verify_zip_info(root, version, files, payload)
    else:
        payload = build_archive(root, version, files)
        if len(payload) > MAX_ASSET_BYTES:
            raise ValueError(f"The synchronized ELPX exceeds 25 MiB: {len(payload)} bytes")
        temporary = destination.with_name(destination.name + ".tmp")
        temporary.write_bytes(payload)
        module_temporary = module_path.with_name(module_path.name + ".tmp")
        module_temporary.write_bytes(module)
        temporary.replace(destination)
        module_temporary.replace(module_path)
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check synchronization without writing files")
    args = parser.parse_args()
    count = synchronize(check=args.check)
    print(f"{'Verified' if args.check else 'Synchronized'} the native ELPX: {count} members; activities and media preserved")


if __name__ == "__main__":
    main()
