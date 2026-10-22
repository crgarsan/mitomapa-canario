#!/usr/bin/env python3
"""Package the current editable release; --check validates without writing.

VERSION.json is the release authority. Historical downloads stay in the public
allowlist, but are never nested inside the current sources or sharing archive.
The ELPX is synchronized separately by sync_current_elpx.py; this command does
not regenerate the learning activities from the historical 4.4 generator.
"""

import argparse
import copy
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urljoin, urlsplit

from release_support import (
    MAX_ASSET_BYTES, digest, json_bytes, metadata, parse_sums, public_entries,
    read_zip, safe_name, source_path, sums_bytes, verify_manifest, verify_sums,
    zip_bytes,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE_SPECIAL = {"SOURCE_MANIFEST.json", "FUENTES_WEB_LEEME.txt"}
DOCUMENTS = (
    "GUIA_DOCENTE.html", "GUIA_DOCENTE_GOBCAN.html", "GUIA_REUTILIZACION.html",
    "FUENTES_CUENTOS.html", "LICENCIA_Y_CREDITOS.txt", "CREDITOS_MATERIALES.csv",
    "EDICION_ILUSTRACIONES.txt", "LICENSE", "assets/images/cc-by-sa-4.0.svg",
    "assets/images/insignias_pasaporte.json", "assets/passport_icon_credits.html",
    "styles.css", "docente.css",
    "downloads/Cuaderno_de_ruta_MitoMapa_web_4_0.html",
    "downloads/Rubrica_lectura_MitoMapa_4_0.html", "downloads/Rubrica_MitoMapa_4_0.csv",
)
PUBLIC_URL = "https://mitomapa-canario.cgarcias.workers.dev/"


def check_download_button(markup, version):
    """Tie the advertised edition, saved filename and revision to the ELPX."""
    class Buttons(HTMLParser):
        def __init__(self):
            super().__init__()
            self.buttons = []
            self.current = None

        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            if tag == "a" and attributes.get("id") == "currentReaDownload":
                self.current = {"attrs": attributes, "text": ""}
                self.buttons.append(self.current)

        def handle_data(self, data):
            if self.current is not None:
                self.current["text"] += data

        def handle_endtag(self, tag):
            if tag == "a":
                self.current = None

    parser = Buttons()
    parser.feed(markup)
    if len(parser.buttons) != 1:
        raise ValueError("Expected one current REA download button")
    button = parser.buttons[0]
    attrs = button["attrs"]
    edition = version["rea_exelearning_version"]
    link = urlsplit(attrs.get("href", ""))
    if (" ".join(button["text"].split()) != f"Descargar REA {edition}"
            or attrs.get("data-rea-version") != edition
            or attrs.get("download") != f"MitoMapa_canario_{edition.replace('.', '_')}.elpx"
            or link.scheme or link.netloc or link.path != version["download"]["path"]
            or parse_qs(link.query).get("revision") != [version["download"]["sha256"][:12]]):
        raise ValueError("The download button differs from the current ELPX edition or revision")


def sharing_document(payload, name, documents, version):
    """Keep printable guides local; route web/download navigation explicitly."""
    if name.endswith(".html"):
        def link(match):
            prefix, quote, raw = match.groups()
            target = unescape(raw)
            parts = urlsplit(target)
            if parts.scheme or target.startswith(("#", "//")):
                return match.group(0)
            if parts.path == version["download"]["path"]:
                target = "../MitoMapa_canario_GobCan.elpx"
            elif parts.path not in documents:
                target = urljoin(PUBLIC_URL, target)
            return prefix + quote + escape(target, quote=True) + quote
        return re.sub(r'''(\b(?:href|src|poster)\s*=\s*)(["'])(.*?)\2''',
                      link, payload.decode("utf-8"), flags=re.IGNORECASE).encode("utf-8")
    if name.endswith(".css"):
        # The shared stylesheet also contains rules for the web's puzzle. The
        # printed guides do not use its map; keep that optional image online
        # instead of duplicating 310 KiB beside an ELPX near the host's limit.
        return payload.replace(b"url('assets/", ("url('" + PUBLIC_URL + "assets/").encode())
    return payload


def release_paths(version):
    current = version.get("release_version", version["rea_exelearning_version"])
    if not all(re.fullmatch(r"\d+\.\d+\.\d+", value) for value in (current, version["web_version"])):
        raise ValueError("The current version must have three numeric components")
    if version["rea_exelearning_version"] != current:
        raise ValueError("The editable edition differs from its delivery version")
    expected = {
        "download": "downloads/MitoMapa_canario_GobCan.elpx",
        "sharing_archive": f"downloads/MitoMapa_REA_v{current.replace('.', '_')}.zip",
        "source_archive": f"downloads/MitoMapa_fuentes_web_v{current.replace('.', '_')}.zip",
    }
    for key, path in expected.items():
        safe_name(version[key]["path"])
        if version[key]["path"] != path:
            raise ValueError(f"Current release path differs from its version: {key}")
    return expected


def sharing_version(version):
    result = copy.deepcopy(version)
    # A ZIP cannot contain its own final checksum or byte length. The public
    # VERSION.json and SHA256SUMS.txt hold that information after packaging.
    for key in ("sharing_archive", "source_archive"):
        for field in ("sha256", "bytes"):
            result[key].pop(field, None)
    return result


def sharing_files(root, version, elpx):
    current = version["rea_exelearning_version"]
    files = {"MitoMapa_canario_GobCan.elpx": elpx}
    documents = set(DOCUMENTS)
    for key in ("release_notes", "rea_release_notes"):
        documents.add(version[key])
    if (root / "PROTOCOLO_PILOTAJE.html").is_file():
        documents.add("PROTOCOLO_PILOTAJE.html")
    for name in sorted(documents):
        files[f"documentacion/{name}"] = sharing_document(
            source_path(root, name).read_bytes(), name, documents, version)
    files["documentacion/VERSION.json"] = json_bytes(sharing_version(version))
    files["LEEME.txt"] = (
        f"MITOMAPA CANARIO · REA {current}\n\n"
        "Web: https://mitomapa-canario.cgarcias.workers.dev/\n\n"
        "1. Descomprime este ZIP.\n"
        "2. Abre MitoMapa_canario_GobCan.elpx con eXeLearning 4.0.5 o compatible.\n"
        "3. Guarda una copia si quieres adaptar el recurso.\n\n"
        "Incluye ocho cuentos, escenas, narraciones y actividades nativas.\n"
        "La web se enlaza al final como recurso adicional, sin embeberla.\n"
        "La propuesta es multinivel: el profesorado\n"
        "elige y ancla curricularmente la ruta. Consulta la guía docente general;\n"
        "la guía GobCan ofrece un ejemplo curricular adaptable.\n"
        "El recurso está pendiente de pilotaje con alumnado.\n\n"
        "Las guías y las plantillas se pueden consultar sin conexión; sus\n"
        "enlaces a la web y a otras descargas requieren conexión.\n\n"
        "El progreso de las actividades nativas de eXe y el de la web externa\n"
        "son independientes. La valoración y su envío por correo son\n"
        "voluntarios; cualquier archivo se adjunta manualmente y sin nombres.\n\n"
        "Autoría: Jesica Fortes Regalado, Gloria Elsa González Martín y\n"
        "Cristian García Santana. Materiales propios: CC BY-SA 4.0.\n"
        "El mapa y los componentes de terceros conservan sus condiciones.\n"
        "Sugerencias: sugerencias.mitomapacanario@gmail.com\n"
    ).encode("utf-8")
    files["SHA256SUMS.txt"] = sums_bytes(files)
    return files


def source_inventory(root, version):
    # Seed from the curated current/previous source inventory, then include new
    # source modules, guides and checks. Never derive it from public downloads.
    candidates = [version["source_archive"]["path"]]
    previous = version.get("previous_web_version", "").replace(".", "_")
    if previous:
        candidates.append(f"downloads/MitoMapa_fuentes_web_v{previous}.zip")
    names = set()
    for candidate in candidates:
        if (root / candidate).is_file():
            names.update(read_zip((root / candidate).read_bytes()))
            break
    names.difference_update(SOURCE_SPECIAL | {"SHA256SUMS.txt"})
    for extension in ("*.html", "*.css", "*.js", "*.md", "*.txt", "*.json", "*.svg", "*.png"):
        names.update(path.relative_to(root).as_posix() for path in root.glob(extension) if path.is_file())
    for directory, patterns in {
        "assets": ("**/*",), "tools": ("*.py",), "tests": ("**/*.py", "**/*.js", "**/*.json"),
        ".github/workflows": ("*.yml", "*.yaml"),
    }.items():
        for pattern in patterns:
            names.update(path.relative_to(root).as_posix() for path in (root / directory).glob(pattern) if path.is_file())
    names.update(name for name in ("LICENSE", "_headers", "wrangler.jsonc", "requirements-browser-tests.txt") if (root / name).is_file())
    return sorted(name for name in names if name not in SOURCE_SPECIAL | {"SHA256SUMS.txt"}
                  and not name.lower().endswith((".zip", ".elpx")) and (root / name).is_file())


def source_files(root, version, version_payload):
    files = {name: source_path(root, name).read_bytes() for name in source_inventory(root, version)}
    files["VERSION.json"] = version_payload
    files["FUENTES_WEB_LEEME.txt"] = (
        f"MitoMapa canario · Fuentes web {version['web_version']}\n\n"
        "Estas fuentes contienen la web, sus recursos locales, documentación,\n"
        "pruebas y herramientas de la edición vigente. No contienen ZIP ni ELPX.\n"
        "Para consultar la web localmente, ejecuta python3 -m http.server y abre\n"
        "http://localhost:8000/. VERSION.json identifica la edición actual;\n"
        "SOURCE_MANIFEST.json verifica cada archivo sin incluirse a sí mismo.\n"
        "Los descargables históricos siguen disponibles en la web pública.\n\n"
        "Materiales propios: CC BY-SA 4.0; consulta LICENSE y LICENCIA_Y_CREDITOS.txt.\n"
        "El mapa y las dependencias conservan sus condiciones originales.\n"
    ).encode("utf-8")
    files["SOURCE_MANIFEST.json"] = json_bytes({name: metadata(payload) for name, payload in sorted(files.items())})
    return files


def public_names(root, previous, paths):
    names = set(previous) | set(paths.values())
    # Only browser modules, teaching documents and the existing static assets
    # are added. CI files, dependency manifests and tests stay in the sources ZIP.
    for extension in ("*.html", "*.css", "*.js", "*.md", "*.txt"):
        names.update(path.name for path in root.glob(extension) if path.is_file())
    names.discard("SHA256SUMS.txt")
    names.discard("requirements-browser-tests.txt")
    names.update(path.relative_to(root).as_posix() for path in (root / "assets").rglob("*") if path.is_file())
    names.update({"VERSION.json", "LICENSE"})
    return sorted(names)


def check_elpx(payload, version, root=ROOT):
    files = read_zip(payload)
    script = files["libs/elpx-manifest.js"].decode("utf-8")
    assignment = re.search(r"window\.__ELPX_MANIFEST__\s*=\s*({.*})\s*;?\s*$", script, re.DOTALL)
    if not assignment:
        raise ValueError("Invalid ELPX inventory assignment")
    manifest = json.loads(assignment.group(1))
    if len(manifest["files"]) != len(set(manifest["files"])) or set(manifest["files"]) != set(files):
        raise ValueError("Incomplete ELPX inventory")
    if version.get("elpx_distribution", {}).get("mode") == "native_only":
        editorial = json.loads(files["EDITORIAL_MANIFEST.json"])
        if editorial.get("distribution") != "native_only" or editorial.get("embedded_web_app") is not False:
            raise ValueError("The current ELPX must be independent of the web application")
        if editorial["edition"] != version["rea_exelearning_version"]:
            raise ValueError("The native ELPX edition differs from the release")
        if "content/resources/mitomapa/index.html" in files or any(
                name.startswith("content/resources/mitomapa/") and name.endswith((".js", ".html", ".css"))
                for name in files):
            raise ValueError("The native ELPX still contains the web application")
        ns = {"o": "http://www.intef.es/xsd/ode"}
        model = ET.fromstring(files["content.xml"])
        native_license = model.findtext(".//o:odeProperty[o:key='pp_license']/o:value", namespaces=ns)
        if native_license != "creative commons: attribution - share alike 4.0":
            raise ValueError("The native project licence must be CC BY-SA 4.0")
        pages = model.findall(".//o:odeNavStructure", ns)
        components = model.findall(".//o:odeComponent", ns)
        if set(editorial["pages"]) != {page.findtext("o:odePageId", namespaces=ns) for page in pages}:
            raise ValueError("The editorial page inventory differs from the native project")
        if set(editorial["idevices"]) != {item.findtext("o:odeIdeviceId", namespaces=ns) for item in components}:
            raise ValueError("The editorial activity inventory differs from the native project")
        return files
    prefix = "content/resources/mitomapa/"
    portable = {name[len(prefix):]: data for name, data in files.items() if name.startswith(prefix)}
    portable_manifest = json.loads(portable["PORTABLE_MANIFEST.json"])
    verify_manifest(portable, portable_manifest["assets"], {"PORTABLE_MANIFEST.json"})
    if "files" in portable_manifest and set(portable_manifest["files"]) != set(portable):
        raise ValueError("Incomplete portable file inventory")
    if portable_manifest["web_version"] != version["web_version"]:
        raise ValueError("Portable version differs from the release")
    portable_version = json.loads(portable["VERSION.json"])
    if portable_version["web_version"] != version["web_version"]:
        raise ValueError("Embedded VERSION.json differs from the release")
    if b"by-nc-sa/4.0" in portable["index.html"].lower():
        raise ValueError("The active portable page links the former NC licence")
    if "version.js" in portable and portable["version.js"] != source_path(root, "version.js").read_bytes():
        raise ValueError("Embedded release module differs from the current web")
    return files


def check_release(root=ROOT):
    version = json.loads((root / "VERSION.json").read_text(encoding="utf-8"))
    paths = release_paths(version)
    public = public_entries(root)
    if not set(paths.values()) <= set(public):
        raise ValueError("Current downloads are missing from the public allowlist")
    for name, path in public.items():
        if name.lower().endswith((".zip", ".elpx")):
            read_zip(path.read_bytes())
    elpx = public[paths["download"]].read_bytes()
    for key in ("download", "sharing_archive"):
        details = metadata(public[paths[key]].read_bytes())
        if any(version[key].get(field) != value for field, value in details.items()):
            raise ValueError(f"VERSION.json download metadata differs: {key}")
    check_elpx(elpx, version, root)
    if version.get("elpx_distribution", {}).get("mode") == "native_only":
        check_download_button(source_path(root, "index.html").read_text(), version)
    sharing = read_zip(public[paths["sharing_archive"]].read_bytes())
    verify_sums(sharing)
    if sharing != sharing_files(root, version, elpx):
        raise ValueError("The sharing archive is not synchronized with this release")
    sources = read_zip(public[paths["source_archive"]].read_bytes())
    if any(name.lower().endswith((".zip", ".elpx")) for name in sources):
        raise ValueError("A source archive contains another ZIP or ELPX")
    verify_manifest(sources, json.loads(sources["SOURCE_MANIFEST.json"]), {"SOURCE_MANIFEST.json"})
    if sources != source_files(root, version, (root / "VERSION.json").read_bytes()):
        raise ValueError("The source archive is not synchronized with current sources")
    for name in ("index.html", "version.js"):
        data = source_path(root, name).read_bytes()
        if name == "index.html" and b"by-nc-sa/4.0" in data.lower():
            raise ValueError("The active web page links the former NC licence")
        if name == "version.js" and version["web_version"].encode() not in data:
            raise ValueError("The release module has a different version")
    return len(public)


def update_release(root=ROOT):
    version = json.loads((root / "VERSION.json").read_text(encoding="utf-8"))
    paths = release_paths(version)
    previous = parse_sums((root / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    # Historical packages are immutable, and their existing URLs stay public.
    for name, expected in previous.items():
        if name not in paths.values() and name.lower().endswith((".zip", ".elpx")):
            if digest(source_path(root, name).read_bytes()) != expected:
                raise ValueError(f"Historical download changed: {name}")
    elpx = source_path(root, paths["download"]).read_bytes()
    check_elpx(elpx, version, root)
    version["download"].update(metadata(elpx))
    if version.get("elpx_distribution", {}).get("mode") == "native_only":
        check_download_button(source_path(root, "index.html").read_text(), version)
    sharing = zip_bytes(sharing_files(root, version, elpx))
    version["sharing_archive"].update(metadata(sharing))
    version_payload = json_bytes(version)
    sources = zip_bytes(source_files(root, version, version_payload))
    overrides = {"VERSION.json": version_payload, paths["sharing_archive"]: sharing,
                 paths["source_archive"]: sources}
    files = {name: overrides[name] if name in overrides else source_path(root, name).read_bytes()
             for name in public_names(root, previous, paths)}
    oversized = [name for name, data in files.items() if len(data) > MAX_ASSET_BYTES]
    if oversized:
        raise ValueError(f"Public assets exceed the 25 MiB limit: {', '.join(oversized)}")
    for name, data in overrides.items():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(destination)
    (root / "SHA256SUMS.txt").write_bytes(sums_bytes(files))
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate current packages without writing files")
    args = parser.parse_args()
    count = check_release() if args.check else update_release()
    print(f"{'Verified' if args.check else 'Updated'} the current release and {count} public assets")


if __name__ == "__main__":
    main()
