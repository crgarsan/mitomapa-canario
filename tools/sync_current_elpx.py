#!/usr/bin/env python3
"""Synchronize the current ELPX from its pinned, immutable native edition.

Native activities, IDs and media are retained. Only current orientations,
edition metadata and the local web application are refreshed. --check performs
the same synchronization in memory and reports stale files without writing.
"""

import argparse
import copy
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import posixpath
import re
import tempfile
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipInfo

from lxml import etree, html

from build_portable_web import portable_index, portable_reuse_guide, verify_portable_web
from harden_jspdf_exports import ZIP_INFO_FIELDS, read_archive, write_archive
from release_support import MAX_ASSET_BYTES, digest, json_bytes, metadata, read_zip, source_path


ROOT = Path(__file__).resolve().parent.parent
NS = {"o": "http://www.intef.es/xsd/ode"}
CONTEXT = "{{context_path}}"
PORTABLE = "content/resources/mitomapa/"
APP = CONTEXT + "/" + PORTABLE
MEDIA_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".wav", ".opus", ".woff", ".woff2", ".ico"}
TEXT_IDS = {
    "GBCTPORTADA", "GBCTJUSTIFICA", "20260823155836TINTRO", "20260823155836TITINW",
    "20260823155836TPASSI", "20260823155837TFINTI", "GBCTDESARROLLO",
    "20260823155837TGUID1", "20260823155837TGUID2", "20260823155837TGUID3",
    "GBCTMETODO", "GBCTRECURSOS", "GBCTACOMPANA", "20260823155837TCRED0",
    "20260930IHISTORIA40",
}
FORMATS = (
    "Una sesión de unos 45 minutos y una isla; un itinerario corto de cuatro sesiones de unos 50 minutos "
    "y dos islas; o el banco completo opcional de ocho a diez sesiones de 35–50 minutos. "
    "El profesorado elige y ancla curricularmente las tareas, las fuentes y los apoyos para su grupo."
)
ROUTE_NOTE = (
    "<p><strong>Ruta acordada y colección de pintaderas.</strong> En el Explorador, Docente → Ajustes y seguimiento "
    "permite seleccionar las islas y revisar sus tareas. Dos islas revisadas de dos acordadas pueden completar "
    "la ruta sin reunir las ocho pintaderas. La colección reconoce retos automáticos y se muestra por separado. "
    "El pasaporte nativo es manual; el informe de 42 juegos y el seguimiento local del Explorador son independientes "
    "y no se sincronizan entre sí ni con la web publicada.</p>"
)


def field(node, name):
    return node.findtext("o:" + name, default="", namespaces=NS)


def set_property(root, container, key, value):
    matches = root.findall(f".//o:{container}[o:key='{key}']/o:value", NS)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one native property {container}/{key}")
    matches[0].text = value


def append_markup(target, markup):
    target.text = None
    for child in list(target):
        target.remove(child)
    for fragment in html.fragments_fromstring(markup):
        if isinstance(fragment, str):
            if len(target):
                target[-1].tail = (target[-1].tail or "") + fragment
            else:
                target.text = (target.text or "") + fragment
        else:
            target.append(fragment)


def inner_markup(node):
    return (node.text or "") + "".join(html.tostring(child, encoding="unicode") for child in node)


def set_text(component, markup):
    properties = json.loads(field(component, "jsonProperties"))
    properties["textTextarea"] = markup
    component.find("o:jsonProperties", NS).text = json.dumps(properties, ensure_ascii=False, separators=(",", ":"))
    view = html.fragment_fromstring(field(component, "htmlView"))
    targets = view.xpath(".//div[@class='exe-text-activity']/div")
    if len(targets) != 1:
        raise ValueError(f"Unexpected Text template: {field(component, 'odeIdeviceId')}")
    append_markup(targets[0], markup)
    component.find("o:htmlView", NS).text = html.tostring(view, encoding="unicode")


def native_guide(root):
    document = html.fromstring(source_path(root, "GUIA_DOCENTE.html").read_bytes())
    main = document.xpath("//main")[0]
    for node in main.xpath(".//a[@href] | .//img[@src]"):
        attribute = "href" if node.tag == "a" else "src"
        reference = node.get(attribute)
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        # The native importer treats fragments/queries in resource URLs as
        # filename characters. Native links open the document itself instead.
        node.set(attribute, APP + parsed.path)
    for link in main.xpath("./a[contains(@class,'guide-back')]"):
        link.getparent().remove(link)
    return "<h2>Guía práctica multinivel</h2>" + inner_markup(main) + ROUTE_NOTE


def native_texts(root, components, version):
    current = version["web_version"]
    originals = {iid: json.loads(field(components[iid], "jsonProperties"))["textTextarea"] for iid in TEXT_IDS}
    result = dict(originals)
    result["GBCTPORTADA"] = result["GBCTPORTADA"].replace(
        "3.er ciclo · Educación Primaria<br>Referencia curricular: 6.º · adaptable a 5.º",
        "Propuesta multinivel<br>Anclaje curricular a cargo del profesorado",
    ).replace(
        ">4 sesiones</p>", ">Una sesión, itinerario corto o banco de actividades</p>",
    ).replace(
        "Objeto de aprendizaje con itinerario libre. Cuatro sesiones de unos 50 minutos para explorar dos islas, contrastar una fuente y compartir una creación. Las ocho islas forman un banco de elección y ampliación.",
        "Objeto de aprendizaje con itinerario libre. " + FORMATS + " Las ocho islas forman un banco de elección y ampliación.",
    )
    result["GBCTJUSTIFICA"] += "<p>La propuesta es multinivel. " + FORMATS + "</p>"
    result["20260823155836TINTRO"] = result["20260823155836TINTRO"].replace(
        "Elige dos islas con tu grupo.", "Acuerda con tu grupo las islas y las tareas que vais a trabajar.",
    )
    result["20260823155836TITINW"] += "<h3>Tres formas de organizar el recorrido</h3><p>" + FORMATS + "</p>" + ROUTE_NOTE
    result["20260823155836TPASSI"] = result["20260823155836TPASSI"].replace(
        "Acuerda dos islas y unas tareas.", "Acuerda las islas y las tareas de tu ruta.",
    ).replace("para terminar las cuatro sesiones", "para terminar la ruta acordada") + ROUTE_NOTE
    result["20260823155837TFINTI"] = result["20260823155837TFINTI"].replace(
        "Como cierre de las cuatro sesiones, en equipo, elige una de las dos islas exploradas",
        "Como cierre de la ruta acordada, individualmente o en equipo, elige una de las islas exploradas",
    ) + "<p>La pieza y la forma de compartirla se ajustan al grupo y al tiempo acordado; la ruta no exige completar las ocho islas.</p>"
    result["GBCTDESARROLLO"] = result["GBCTDESARROLLO"].replace(
        "Elige dos islas por curiosidad", "Elige las islas de tu ruta por curiosidad",
    ).replace("Para las cuatro sesiones,", "En el ejemplo de cuatro sesiones y dos islas,")
    result["20260823155837TGUID1"] = native_guide(root)
    result["20260823155837TGUID2"] = (
        "<h2>Ejemplo curricular adaptable</h2><p>Esta selección ilustra el itinerario corto. No fija el nivel "
        "obligatorio del recurso multinivel. Para otro grupo, el profesorado selecciona y verifica las competencias, "
        "los criterios y los saberes pertinentes conforme a su programación. " + FORMATS + "</p>"
        + result["20260823155837TGUID2"]
    )
    result["20260823155837TGUID3"] = result["20260823155837TGUID3"].replace("web 4.5.1", "web " + current).replace("ELPX 4.5.1", "ELPX " + current)
    result["20260823155837TGUID3"] += (
        ROUTE_NOTE + "<p>El Explorador permite desplazar la narración y saltar diez segundos; admite valoraciones solo escritas. "
        "Los audios y las escenas se conservan íntegros. <strong>Pilotaje pendiente:</strong> consulta "
        f'<a href="{APP}PROTOCOLO_PILOTAJE.html">el protocolo imprimible para la primera aplicación</a>.</p>'
    )
    result["GBCTMETODO"] += "<p>Los ejemplos de dos cuentos son una posibilidad del itinerario corto. " + FORMATS + "</p>"
    result["GBCTACOMPANA"] = result["GBCTACOMPANA"].replace("calificación de una ruta de dos islas", "calificación de la ruta acordada") + ROUTE_NOTE
    result["GBCTRECURSOS"] += (
        f'<ul><li><a href="{APP}GUIA_DOCENTE.html">Guía práctica multinivel y tres duraciones posibles</a>.</li>'
        f'<li><a href="{APP}GUIA_DOCENTE_GOBCAN.html">Ejemplo curricular GobCan del itinerario corto</a>.</li>'
        f'<li><a href="{APP}PROTOCOLO_PILOTAJE.html">Protocolo de pilotaje y hoja imprimible</a>. '
        'Propuesta todavía no aplicada con alumnado.</li></ul>'
    )
    result["20260823155837TCRED0"] = re.sub(
        r"<p><strong>Edición:</strong>.*?</p>",
        f"<p><strong>Edición:</strong> {current} · adaptación GobCan. Propuesta multinivel con tres formatos, "
        "ruta acordada separada de la colección, acompañamiento y mejoras de uso. Conserva los cuentos, las "
        f"escenas, las narraciones y los juegos nativos. El proyecto se edita con eXeLearning {version['exelearning_runtime_version']}.</p>",
        result["20260823155837TCRED0"], count=1, flags=re.S,
    )
    result["20260930IHISTORIA40"] = result["20260930IHISTORIA40"].replace("Edición actual 4.5.1", "Edición anterior 4.5.1")
    result["20260930IHISTORIA40"] += (
        f"<p><strong>Edición actual {current}.</strong> Actualiza las orientaciones multinivel, el reinicio, "
        "la valoración escrita, los controles de narración y la ruta acordada del Explorador. Conserva los 39 "
        "capítulos, 118 identidades de iDevices, 42 juegos nativos y los medios de la edición anterior. "
        "Materiales propios: CC BY-SA 4.0; los materiales de terceros conservan sus condiciones.</p>"
    )
    return result


def exported_content(markup, page_path, paths):
    prefix = "../" if page_path.startswith("html/") else ""
    markup = markup.replace(CONTEXT + "/", prefix)
    def node_link(match):
        relative = posixpath.relpath(paths[match.group(1)], posixpath.dirname(page_path) or ".")
        return relative + (match.group(2) or "")
    return re.sub(r"exe-node:([A-Za-z0-9]+)(#[^\"'<>\s]*)?", node_link, markup)


def update_native(files, root, version):
    parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True)
    tree = etree.fromstring(files["content.xml"], parser)
    components = {field(component, "odeIdeviceId"): component for component in tree.findall(".//o:odeComponent", NS)}
    replacements = native_texts(root, components, version)
    for iid, markup in replacements.items():
        set_text(components[iid], markup)
    subtitle = "Lectura, patrimonio y creación · propuesta multinivel"
    set_property(tree, "odeProperty", "pp_subtitle", subtitle)
    date = version["prepared_at"]
    modified = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp() * 1000)
    set_property(tree, "odeProperty", "pp_modified", str(modified))
    set_property(tree, "odeResource", "odeVersionId", date.replace("-", "") + "MITOMAPA" + version["web_version"].replace(".", ""))
    footer = (
        "<p>MitoMapa canario: ocho islas, ocho pintaderas · Jesica Fortes Regalado; Gloria Elsa González Martín; "
        "Cristian García Santana · CC BY-SA 4.0</p>"
        f"<p>{version['web_version']} · adaptación GobCan y propuesta multinivel · Narración: Jesica Fortes Regalado.</p>"
    )
    set_property(tree, "odeProperty", "footer", footer)
    source = files["search_index.js"].decode()
    search = json.loads(source[source.index("{"):].rstrip(";\n"))
    paths = {pid: info["fileUrl"] for pid, info in search.items()}
    for page in tree.findall(".//o:odeNavStructure", NS):
        pid = field(page, "odePageId")
        page_path = paths[pid]
        document = html.fromstring(files[page_path])
        for component in page.findall(".//o:odeComponent", NS):
            iid = field(component, "odeIdeviceId")
            if iid not in replacements:
                continue
            targets = document.xpath(f'//div[@id="{iid}"]')
            if len(targets) != 1:
                raise ValueError(f"Missing native exported Text: {iid}")
            view = exported_content(field(component, "htmlView"), page_path, paths)
            append_markup(targets[0], view)
            attributes = targets[0].get("data-idevice-json-data")
            if attributes and "textTextarea" in attributes:
                targets[0].set("data-idevice-json-data", field(component, "jsonProperties"))
            for block in search[pid]["blocks"].values():
                if iid in block["idevices"]:
                    block["idevices"][iid]["htmlView"] = view
                    block["idevices"][iid]["jsonProperties"] = field(component, "jsonProperties")
        for node in document.xpath("//p[contains(concat(' ',normalize-space(@class),' '),' package-subtitle ')]"):
            node.text = subtitle
        for node in document.xpath("//div[@id='siteUserFooter']"):
            append_markup(node, footer)
        files[page_path] = html.tostring(document, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")
    files["search_index.js"] = b"window.exeSearchData = " + json.dumps(search, ensure_ascii=False, separators=(",", ":")).encode() + b";\n"
    if not etree.DTD(BytesIO(files["content.dtd"])).validate(tree):
        raise ValueError("The synchronized ODE model does not match its DTD")
    files["content.xml"] = etree.tostring(tree, encoding="UTF-8", xml_declaration=True, doctype='<!DOCTYPE ode SYSTEM "content.dtd">')


def portable_version(version):
    result = copy.deepcopy(version)
    for key in ("download", "sharing_archive", "source_archive"):
        for field_name in ("sha256", "bytes"):
            result[key].pop(field_name, None)
    return result


def version_module(version):
    values = {"version": version["web_version"], "reaVersion": version["rea_exelearning_version"], "schemaVersion": 1}
    return (
        "/* Generado a partir de VERSION.json. */\nwindow.MitoMapaVersion = Object.freeze("
        + json.dumps(values, ensure_ascii=False, separators=(",", ":")) + ");\n"
    ).encode()


def external_archive_links(markup):
    """Keep optional archive references online without nesting those packages."""
    def replace(match):
        reference = match.group(2)
        parsed = urlsplit(reference)
        if not parsed.scheme and not parsed.netloc and parsed.path.lower().endswith((".zip", ".elpx")):
            return match.group(1) + "https://mitomapa-canario.cgarcias.workers.dev/" + reference + match.group(3)
        return match.group(0)
    return re.sub(r"(<a\b[^>]*\bhref=[\"'])([^\"']+)([\"'])", replace, markup)


def update_portable(files, root, version):
    portable = {name[len(PORTABLE):]: data for name, data in files.items() if name.startswith(PORTABLE)}
    portable.pop("PORTABLE_MANIFEST.json", None)
    for name in list(portable):
        if (root / name).is_file():
            portable[name] = source_path(root, name).read_bytes()
    for pattern in ("*.js", "*.css", "*.html"):
        for path in root.glob(pattern):
            portable[path.name] = source_path(root, path.name).read_bytes()
    for name in (version["release_notes"], version["rea_release_notes"], "LICENSE", "LICENCIA_Y_CREDITOS.txt", "CREDITOS_MATERIALES.csv"):
        portable[name] = source_path(root, name).read_bytes()
    for path in (root / "assets").rglob("*"):
        if path.is_file():
            name = path.relative_to(root).as_posix()
            portable[name] = source_path(root, name).read_bytes()
    current = version["web_version"]
    portable["index.html"] = portable_index(source_path(root, "index.html").read_text(), current).encode()
    portable["GUIA_REUTILIZACION.html"] = portable_reuse_guide(source_path(root, "GUIA_REUTILIZACION.html").read_text(), current).encode()
    portable["VERSION.json"] = json_bytes(portable_version(version))
    portable["version.js"] = version_module(version)
    portable["README_PORTABLE.txt"] = (
        f"MitoMapa canario · Aplicación portable {current}\n\n"
        "Abre index.html. Incluye scripts, estilos, imágenes, audios y guías locales.\n"
        "Para conservar el proyecto completo utiliza el iDevice Descargar el REA editable.\n"
        "No contiene ZIP ni ELPX anidados. Fuentes bibliográficas y correo requieren conexión.\n\n"
        "Las actividades nativas y la aplicación se adaptan por separado. Su seguimiento\n"
        "no se sincroniza: guarda la aplicación desde Docente → Ajustes y seguimiento.\n"
        "La ruta acordada revisada es distinta de la colección de ocho pintaderas.\n"
        "Narración: Jesica Fortes Regalado. Se conservan los 16 MP3 y las ocho escenas.\n"
        "Propuesta multinivel pendiente de pilotaje; consulta PROTOCOLO_PILOTAJE.html.\n"
        "Materiales propios: CC BY-SA 4.0. Conserva los créditos y las condiciones de terceros.\n"
    ).encode()
    for name, payload in list(portable.items()):
        if name.endswith(".html"):
            portable[name] = external_archive_links(payload.decode()).encode()
    if any(name.lower().endswith((".zip", ".elpx")) for name in portable):
        raise ValueError("Nested package in the portable application")
    with tempfile.TemporaryDirectory(prefix="mitomapa-portable-check-") as temporary:
        folder = Path(temporary)
        for name, payload in portable.items():
            destination = folder / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        validation = verify_portable_web(folder)
    portable["PORTABLE_MANIFEST.json"] = json_bytes({
        "web_version": current, "distribution_web_version": current, "entry_point": "index.html",
        "included_in_elpx": True, "runtime_assets_local": True, "native_tracking_separate": True,
        "validation": validation,
        "assets": {name: metadata(payload) for name, payload in sorted(portable.items())},
        "files": sorted([*portable, "PORTABLE_MANIFEST.json"]),
    })
    for name, payload in portable.items():
        files[PORTABLE + name] = payload


def native_structure(files):
    tree = etree.fromstring(files["content.xml"], etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True))
    components = tree.findall(".//o:odeComponent", NS)
    return {
        "pages": [field(page, "odePageId") for page in tree.findall(".//o:odeNavStructure", NS)],
        "components": {field(component, "odeIdeviceId"): component for component in components},
    }


def verify_preservation(baseline, result):
    before, after = native_structure(baseline), native_structure(result)
    if before["pages"] != after["pages"] or set(before["components"]) != set(after["components"]):
        raise ValueError("Synchronization changed native page or activity identities")
    for iid, original in before["components"].items():
        current = after["components"][iid]
        if iid not in TEXT_IDS and etree.tostring(original) != etree.tostring(current):
            raise ValueError(f"Synchronization changed a preserved native activity: {iid}")
        if field(original, "odeIdeviceTypeName") != field(current, "odeIdeviceTypeName"):
            raise ValueError(f"Synchronization changed a native activity type: {iid}")
    for name, payload in baseline.items():
        if Path(name).suffix.lower() in MEDIA_EXTENSIONS and result.get(name) != payload:
            raise ValueError(f"Synchronization changed an existing media asset: {name}")
        if name.startswith(("libs/", "idevices/", "theme/")) and name != "libs/elpx-manifest.js" and result.get(name) != payload:
            raise ValueError(f"Synchronization changed an existing runtime dependency: {name}")


def build_current(root=ROOT):
    version = json.loads((root / "VERSION.json").read_text())
    source = version["elpx_source"]
    payload = source_path(root, source["path"]).read_bytes()
    if digest(payload) != source["sha256"]:
        raise ValueError("The pinned native source ELPX has changed")
    baseline = read_zip(payload)
    result = dict(baseline)
    update_native(result, root, version)
    update_portable(result, root, version)
    result["libs/elpx-manifest.js"] = (
        f"/** Complete current MitoMapa {version['web_version']} source inventory. */\nwindow.__ELPX_MANIFEST__=".encode()
        + json_bytes({"version": 1, "files": sorted(result), "projectTitle": "MitoMapa canario: ocho islas, ocho pintaderas"}).rstrip()
        + b";\n"
    )
    verify_preservation(baseline, result)
    return result, version


def source_zip_info(root, version):
    infos, _, comment = read_archive(source_path(root, version["elpx_source"]["path"]).read_bytes())
    return infos, comment


def current_zip_info(root, version, files):
    infos, comment = source_zip_info(root, version)
    known = {info.filename for info in infos}
    for name in sorted(set(files) - known):
        entry = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = 0o644 << 16
        infos.append(entry)
    return infos, comment


def build_archive(root, version, files):
    infos, comment = current_zip_info(root, version, files)
    # Reuse the existing editor-aware writer: native flag bits, timestamps,
    # zero attributes and data descriptors retain the original representation.
    return write_archive(infos, files, comment)


def verify_zip_info(root, version, files, payload):
    expected, comment = current_zip_info(root, version, files)
    actual, _, actual_comment = read_archive(payload)
    if actual_comment != comment or len(expected) != len(actual):
        raise ValueError("The current ELPX changed its editor ZIP metadata")
    for before, after in zip(expected, actual, strict=True):
        if any(getattr(before, name) != getattr(after, name) for name in ZIP_INFO_FIELDS):
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
    print(f"{'Verified' if args.check else 'Synchronized'} the current ELPX: {count} members; native activities and media preserved")


if __name__ == "__main__":
    main()
