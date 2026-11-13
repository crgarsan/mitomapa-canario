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
from pathlib import Path, PurePosixPath
import posixpath
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urljoin, urlsplit

from release_support import (
    MAX_ASSET_BYTES, approved_release_paths, digest, json_bytes, metadata, parse_sums, public_entries,
    pinned_story_media, require_approved, story_media_inventory,
    PINTADERA_DIRECTORY, PINTADERA_GROUPS, PINTADERA_MANIFEST, pintadera_inventory,
    read_zip, safe_name, source_path, sums_bytes, verify_manifest, verify_sums,
    LAPA_STL, STORY_ACTIVITY_BOOK_PDF, STORY_BOOK_PDF, VASIJA_COLLECTION_ZIP, check_vasija_collection, lapa_assets,
    story_book_assets, vasija_assets, zip_bytes,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE_SPECIAL = {"SOURCE_MANIFEST.json", "FUENTES_WEB_LEEME.txt"}
PUBLIC_SUFFIXES = {".html", ".css", ".js", ".md", ".txt"}
SOURCE_SUFFIXES = PUBLIC_SUFFIXES | {".json", ".svg", ".png"}
SOURCE_EXPLICIT = {
    "LICENSE", "_headers", "wrangler.jsonc", "requirements-browser-tests.txt",
    ".github/dependabot.yml", "docs/RESPALDO.md",
}
DOCUMENTS = (
    "GUIA_DOCENTE.html", "GUIA_DOCENTE_GOBCAN.html", "GUIA_REUTILIZACION.html",
    "FUENTES_CUENTOS.html", "LICENCIA_Y_CREDITOS.txt", "CREDITOS_MATERIALES.csv",
    "EDICION_ILUSTRACIONES.txt", "LICENSE", "assets/images/cc-by-sa-4.0.svg",
    "assets/images/insignias_pasaporte.json", "assets/passport_icon_credits.html",
    "styles.css", "docente.css",
    "downloads/Cuaderno_de_ruta_MitoMapa.html",
    "downloads/Pauta_de_revision_MitoMapa.html", "downloads/Pauta_de_revision_MitoMapa.csv",
)
LEGACY_CLASSROOM_DOCUMENTS = {
    "downloads/Cuaderno_de_ruta_MitoMapa_web_4_0.html",
    "downloads/Rubrica_lectura_MitoMapa_4_0.html", "downloads/Rubrica_MitoMapa_4_0.csv",
}
PUBLIC_URL = "https://mitomapacanario.org/"


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
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), parts.path))
            if resolved == version["download"]["path"]:
                target = posixpath.relpath("MitoMapa_canario_GobCan.elpx", "documentacion/" + posixpath.dirname(name))
            elif resolved not in documents:
                target = urljoin(urljoin(PUBLIC_URL, name), target)
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
    editions = (version["web_version"], version["rea_exelearning_version"])
    if not all(isinstance(value, str) and re.fullmatch(r"\d+\.\d+\.\d+", value) for value in editions):
        raise ValueError("The current version must have three numeric components")
    latest = max(editions, key=lambda value: tuple(map(int, value.split("."))))
    current = version.get("release_version", latest)
    if not isinstance(current, str) or not re.fullmatch(r"\d+\.\d+\.\d+", current):
        raise ValueError("The current version must have three numeric components")
    if current != latest:
        raise ValueError("The release version differs from its delivery maximum")
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


def sharing_files(root, version, elpx, approved):
    current = version["rea_exelearning_version"]
    files = {"MitoMapa_canario_GobCan.elpx": elpx}
    documents = set(DOCUMENTS)
    for key in ("release_notes", "rea_release_notes"):
        documents.add(version[key])
    for protocol in ("PROTOCOLO_PILOTAJE.html", "PROTOCOLO_PILOTAJE_WEB_4_9_0.html"):
        if protocol in approved:
            documents.add(protocol)
    require_approved(documents, approved)
    for name in sorted(documents):
        files[f"documentacion/{name}"] = sharing_document(
            source_path(root, name).read_bytes(), name, documents, version)
    files["documentacion/VERSION.json"] = json_bytes(sharing_version(version))
    files["LEEME.txt"] = (
        f"MITOMAPA CANARIO · REA {current}\n\n"
        "Web: https://mitomapacanario.org/\n\n"
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


def source_inventory(approved):
    excluded = SOURCE_SPECIAL | LEGACY_CLASSROOM_DOCUMENTS | {"SHA256SUMS.txt"}
    for name in sorted(approved - excluded):
        path = PurePosixPath(name)
        if path.suffix.lower() in {".zip", ".elpx"}:
            continue
        if (name in SOURCE_EXPLICIT or name in DOCUMENTS
                or (len(path.parts) == 1 and path.suffix in SOURCE_SUFFIXES)
                or name.startswith("assets/")
                or (path.parent == PurePosixPath("tools") and path.suffix in {".py", ".js"})
                or path.parent == PurePosixPath("tools/vendor")
                or (name.startswith("tests/") and path.suffix in {".py", ".js", ".json"})
                or (path.parent == PurePosixPath(".github/workflows") and path.suffix in {".yml", ".yaml"})):
            yield name


def source_files(root, version, version_payload, approved):
    files = {name: source_path(root, name).read_bytes() for name in source_inventory(approved)}
    files["VERSION.json"] = version_payload
    media_note = (
        "\nLos nuevos medios de los cuentos se distribuyen por separado para mantener\n"
        "esta descarga de fuentes dentro del limite del alojamiento. MEDIA_MANIFEST.json\n"
        "identifica sus rutas, tamanos y huellas. Para recuperarlos junto a estas fuentes,\n"
        "ejecuta python3 tools/fetch_story_media.py y despues inicia el servidor local.\n"
        "El origen predeterminado es el respaldo estatico de GitHub Pages, que sirve\n"
        "los archivos sin modificaciones del alojamiento principal. Puedes indicar\n"
        "otro origen HTTPS mediante --base-url. La descarga verifica HTTPS, tamano\n"
        "y SHA-256 antes de guardar cada archivo.\n\n"
        if 'MEDIA_MANIFEST.json' in files else ''
    )
    pintadera_note = (
        '\nLos STL y ZIP de las pintaderas se distribuyen en la web publicada.\n'
        f'Consúltalos en {PUBLIC_URL}#pintaderas3d. {PINTADERA_MANIFEST} contiene sus huellas y tamaños.\n\n'
        if PINTADERA_MANIFEST in files else ''
    )
    vasija_note = (
        "\nLos STL de las vasijas y el ZIP de la colección se distribuyen en la web publicada.\n"
        f"Consulta {PUBLIC_URL}#vasijacanaria3d. El STL de Tenerife se guarda en\n"
        "downloads/vasija/vasija_canaria.stl y los otros seis STL en downloads/vasijas/,\n"
        "con los nombres gran-canaria.stl, la-palma.stl, lanzarote.stl, fuerteventura.stl,\n"
        "la-gomera.stl y el-hierro.stl. Guarda el ZIP conjunto como downloads/vasijas/coleccion.zip.\n\n"
        if vasija_assets(root, approved=approved) else ""
    )
    lapa_note = (
        f"\nEl STL de la lapa blanca se distribuye en {PUBLIC_URL}#lapa-blanca.\n"
        f"Para usar el visor local, guarda el archivo en {LAPA_STL}.\n\n"
        if lapa_assets(root, approved=approved) else ""
    )
    book_assets = story_book_assets(root, approved=approved)
    story_book_note = ''.join(
        f"\nEl libro {title} se descarga desde {PUBLIC_URL}{name}.\n"
        f"Para abrirlo desde la web local, guarda el PDF en {name}.\n\n"
        for name, title in (
            (STORY_BOOK_PDF, 'Cuentos de Canarias'),
            (STORY_ACTIVITY_BOOK_PDF, 'Cuentos y fichas de actividades'),
        )
        if name in book_assets
    )
    files["FUENTES_WEB_LEEME.txt"] = (
        f"MitoMapa canario · Fuentes web {version['web_version']}\n\n"
        "Estas fuentes contienen la web, sus recursos locales, documentación,\n"
        "pruebas y herramientas de la edición vigente. No contienen ZIP ni ELPX.\n"
        "Para consultar la web localmente, ejecuta python3 -m http.server y abre\n"
        "http://localhost:8000/. VERSION.json identifica la edición actual;\n"
        "SOURCE_MANIFEST.json verifica cada archivo sin incluirse a sí mismo.\n"
        "Los descargables históricos siguen disponibles en la web pública.\n\n" + media_note + pintadera_note + vasija_note + lapa_note + story_book_note +
        "Materiales propios: CC BY-SA 4.0; consulta LICENSE y LICENCIA_Y_CREDITOS.txt.\n"
        "El mapa y las dependencias conservan sus condiciones originales.\n"
    ).encode("utf-8")
    files["SOURCE_MANIFEST.json"] = json_bytes({name: metadata(payload) for name, payload in sorted(files.items())})
    return files


def public_names(root, previous, paths, approved, pintaderas, models):
    names = set(previous) | set(paths.values()) | models
    # Only browser modules, teaching documents and the existing static assets
    # are added. CI files, dependency manifests and tests stay in the sources ZIP.
    names.update(name for name in approved if "/" not in name and PurePosixPath(name).suffix in PUBLIC_SUFFIXES)
    names.discard("SHA256SUMS.txt")
    names.discard("requirements-browser-tests.txt")
    names.update(name for name in approved if name.startswith("assets/"))
    names.update({"VERSION.json", "LICENSE"})
    media = pinned_story_media(root, approved=approved) if "MEDIA_MANIFEST.json" in approved else {}
    if media:
        names.update(media)
        names.add('MEDIA_MANIFEST.json')
    if pintaderas:
        names.update(pintaderas)
        names.add(PINTADERA_MANIFEST)
    return names


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


def check_pintadera_downloads(root, inventory):
    if not inventory:
        return
    for name, expected in inventory.items():
        if metadata(source_path(root, name).read_bytes()) != expected:
            raise ValueError('Pintadera download metadata differs: ' + name)
    for group in PINTADERA_GROUPS:
        prefix = f'{PINTADERA_DIRECTORY}/{group}'
        expected = {Path(name).name: details for name, details in inventory.items() if name.startswith(prefix + '/')}
        packed = read_zip(source_path(root, prefix + '.zip').read_bytes())
        if {name: metadata(data) for name, data in packed.items()} != expected:
            raise ValueError('Pintadera ZIP does not match its individual STL files: ' + group)


def check_release(root=ROOT, *, inventory=None):
    approved = approved_release_paths(root, inventory)
    require_approved({"VERSION.json", "index.html", "version.js"}, approved)
    version_path = source_path(root, "VERSION.json")
    version = json.loads(version_path.read_text(encoding="utf-8"))
    paths = release_paths(version)
    public = public_entries(root, approved=approved)
    if not set(paths.values()) <= set(public):
        raise ValueError("Current downloads are missing from the public allowlist")
    if "MEDIA_MANIFEST.json" in approved:
        media = story_media_inventory(root)
        if not (media.keys() | {"MEDIA_MANIFEST.json"}) <= public.keys():
            raise ValueError("Story media are missing from the public allowlist")
        pinned_story_media(root, approved=approved, inventory=media)
    vasijas = vasija_assets(root, approved=approved)
    if not vasijas <= public.keys():
        raise ValueError("Vasija assets are missing from the public allowlist")
    check_vasija_collection(root, vasijas)
    if not lapa_assets(root, approved=approved) <= public.keys():
        raise ValueError("Lapa assets are missing from the public allowlist")
    if not story_book_assets(root, approved=approved) <= public.keys():
        raise ValueError("A story book download is missing from the public allowlist")
    pintaderas = pintadera_inventory(root, approved=approved)
    if pintaderas:
        if not (set(pintaderas) | {PINTADERA_MANIFEST}) <= set(public):
            raise ValueError('Pintadera downloads are missing from the public allowlist')
        check_pintadera_downloads(root, pintaderas)
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
    if sharing != sharing_files(root, version, elpx, approved):
        raise ValueError("The sharing archive is not synchronized with this release")
    sources = read_zip(public[paths["source_archive"]].read_bytes())
    if any(name.lower().endswith((".zip", ".elpx")) for name in sources):
        raise ValueError("A source archive contains another ZIP or ELPX")
    verify_manifest(sources, json.loads(sources["SOURCE_MANIFEST.json"]), {"SOURCE_MANIFEST.json"})
    if sources != source_files(root, version, version_path.read_bytes(), approved):
        raise ValueError("The source archive is not synchronized with current sources")
    for name in ("index.html", "version.js"):
        data = source_path(root, name).read_bytes()
        if name == "index.html" and b"by-nc-sa/4.0" in data.lower():
            raise ValueError("The active web page links the former NC licence")
        if name == "version.js" and version["web_version"].encode() not in data:
            raise ValueError("The release module has a different version")
    return len(public)


def update_release(root=ROOT, *, inventory=None):
    approved = approved_release_paths(root, inventory)
    require_approved({"SHA256SUMS.txt", "VERSION.json", "index.html", "version.js"}, approved)
    version = json.loads(source_path(root, "VERSION.json").read_text(encoding="utf-8"))
    paths = release_paths(version)
    previous = parse_sums(source_path(root, "SHA256SUMS.txt").read_text(encoding="utf-8"))
    generated_archives = {paths["sharing_archive"], paths["source_archive"]}
    require_approved((previous.keys() - generated_archives) | {paths["download"]}, approved)
    pintaderas = pintadera_inventory(root, approved=approved)
    require_approved(pintaderas, approved)
    check_pintadera_downloads(root, pintaderas)
    vasijas = vasija_assets(root, approved=approved)
    models = vasijas | lapa_assets(root, approved=approved) | story_book_assets(root, approved=approved)
    require_approved(models, approved)
    check_vasija_collection(root, vasijas)
    current_downloads = set(paths.values()) | pintaderas.keys() | (vasijas & {VASIJA_COLLECTION_ZIP})
    # Historical packages are immutable, and their existing URLs stay public.
    for name, expected in previous.items():
        if name not in current_downloads and name.lower().endswith((".zip", ".elpx")):
            if digest(source_path(root, name).read_bytes()) != expected:
                raise ValueError(f"Historical download changed: {name}")
    elpx = source_path(root, paths["download"]).read_bytes()
    check_elpx(elpx, version, root)
    version["download"].update(metadata(elpx))
    if version.get("elpx_distribution", {}).get("mode") == "native_only":
        check_download_button(source_path(root, "index.html").read_text(), version)
    sharing = zip_bytes(sharing_files(root, version, elpx, approved))
    version["sharing_archive"].update(metadata(sharing))
    version_payload = json_bytes(version)
    sources = zip_bytes(source_files(root, version, version_payload, approved))
    overrides = {"VERSION.json": version_payload, paths["sharing_archive"]: sharing,
                 paths["source_archive"]: sources}
    files = {name: overrides[name] if name in overrides else source_path(root, name).read_bytes()
             for name in sorted(public_names(root, previous, paths, approved, pintaderas, models))}
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
    parser.add_argument("--inventory", type=Path, help="Reviewed JSON file list for a complete non-Git export")
    args = parser.parse_args()
    action = check_release if args.check else update_release
    count = action(inventory=args.inventory)
    print(f"{'Verified' if args.check else 'Updated'} the current release and {count} public assets")


if __name__ == "__main__":
    main()
