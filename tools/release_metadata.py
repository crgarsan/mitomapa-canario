#!/usr/bin/env python3
"""Derive current release documents from VERSION.json; --check never writes.

The web revision and native REA revision are independent. Product identities
come from local bytes; dated publication observations do not assert the state
of a later deployment. Generated ZIP identities belong in SHA256SUMS.txt and
the external release catalogue, outside documents contained by those ZIPs.
"""

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re

from harden_jspdf_exports import read_archive, read_archive_file
from release_support import MAX_ASSET_BYTES, metadata, safe_name, source_path


ROOT = Path(__file__).resolve().parent.parent
SPANISH_GUIDE_PATHS = frozenset({"GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html"})
ENGLISH_GUIDE_PATHS = frozenset({"GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"})
DOCUMENT_PATHS = frozenset({"VERSION.txt", "version.js", "README.md", "README_ACTUALIZACION.txt", "EDICIONES.md"}) | SPANISH_GUIDE_PATHS
GUIDE_VERSION_FIELDS = {"web": "web_version", "rea": "rea_exelearning_version", "runtime": "exelearning_runtime_version"}
GUIDE_VERSION_TAG = re.compile(
    r'(<(?P<tag>span|title)\b[^>]*\bdata-release-version=(?P<quote>[\"\'])(?P<field>web|rea|runtime|package)(?P=quote)[^>]*>)'
    r'(?P<value>[^<]*)(</(?P=tag)>)')
GUIDE_DOWNLOAD_TAG = re.compile(
    r'<a\b[^>]*\bdata-release-download=([\"\'])(elpx|sharing|source)\1[^>]*>')
BEGIN = "<!-- BEGIN GENERATED CURRENT EDITION -->"
END = "<!-- END GENERATED CURRENT EDITION -->"


def version_module(version):
    """Keep the public legacy API and progress schema version unchanged."""
    values = {"version": version["web_version"], "reaVersion": version["rea_exelearning_version"], "schemaVersion": 1}
    return ("/* Generado a partir de VERSION.json. */\nwindow.MitoMapaVersion = Object.freeze(" +
            json.dumps(values, ensure_ascii=False, separators=(",", ":")) + ");\n").encode("utf-8")


def revision(value):
    return date.fromisoformat(value).strftime("%d/%m/%Y") if value else None


def package_version(version):
    return max((version["web_version"], version["rea_exelearning_version"]),
               key=lambda value: tuple(int(part) for part in value.split(".")))


def native_download_rows(version):
    """Validate external native identities without fetching or staging binaries."""
    if "native_downloads" not in version:
        return []
    entries = version["native_downloads"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValueError("Invalid native download catalogue: expected Spanish and English editions")
    filenames = {"es": "MitoMapa_Canario_ES", "en-GB": "MitoMapa_Canary_Islands_EN"}
    fields = {"language", "version", "exelearning_runtime_version", "filename", "url", "sha256", "bytes"}
    rows = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != fields:
            raise ValueError("Invalid native download metadata fields")
        language = entry["language"]
        if not isinstance(language, str) or language not in filenames or language in rows:
            raise ValueError("Invalid native download language")
        edition, runtime = entry["version"], entry["exelearning_runtime_version"]
        if any(not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value)
               for value in (edition, runtime)):
            raise ValueError("Invalid native download edition or eXeLearning version")
        filename = f"{filenames[language]}_v{edition.replace('.', '_')}.elpx"
        url = f"https://github.com/crgarsan/mitomapa-canario/releases/download/elpx-v{edition}/{filename}"
        if entry["filename"] != filename or entry["url"] != url:
            raise ValueError("Invalid native download URL or filename")
        if (not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
                or type(entry["bytes"]) is not int or entry["bytes"] < 1):
            raise ValueError("Invalid native download SHA-256 or byte length")
        rows[language] = {**entry, "product": "native_elpx", "path": None, "base_version": None,
                          "availability": "external_catalogued"}
    return [rows[language] for language in filenames]


def _local_row(root, version, product, language, path, edition, base=None):
    payload = read_archive_file(source_path(root, path), max_bytes=MAX_ASSET_BYTES)
    row = {"product": product, "language": language, "path": path, "version": edition,
           "base_version": base, **metadata(payload), "availability": "repository"}
    if product == "elpx":
        _, files, _ = read_archive(payload)
        if "EDITORIAL_MANIFEST.json" in files:
            editorial = json.loads(files["EDITORIAL_MANIFEST.json"])
            row["declared_editorial_status"] = editorial.get("edition")
            row["embedded_version"] = editorial.get("source_revision", editorial.get("edition"))
            row["embedded_language"] = editorial.get("language")
    observation = version.get("external_publications", {}).get("production", {})
    for artifact in observation.get("artifacts", []):
        if artifact.get("path") == path:
            row["public_observation"] = {**artifact, "checked_at_utc": observation.get("checked_at_utc"),
                                         "reference_commit": observation.get("reference_commit")}
            matches = all(artifact.get(key) == row[key] for key in ("sha256", "bytes"))
            row["availability"] = ("public_observed" if artifact.get("http_status") == 200 and matches
                                   else "public_observation_differs")
            break
    return row


def product_rows(root, version):
    """Return a Git-independent inventory for an external release catalogue.

    Local hashes describe this checkout, including generated ZIPs if present.
    Publication facts retain their observation date and reference commit.
    """
    root = Path(root)
    native = native_download_rows(version)
    web, rea = version["web_version"], version["rea_exelearning_version"]
    rows = []
    for language, path in (("es", "index.html"), ("en-GB", "index-en.html")):
        if (root / path).exists():
            rows.append(_local_row(root, version, "web", language, path, web))
    rows.append(_local_row(root, version, "elpx", "es", version["download"]["path"], rea, rea))
    for product, key, language, edition, base in (
        ("sharing_zip", "sharing_archive", "es", package_version(version), rea),
        ("source_zip", "source_archive", "es/en-GB", package_version(version), rea),
    ):
        path = version[key]["path"]
        if (root / path).exists():
            rows.append(_local_row(root, version, product, language, path, edition, base))
        else:
            rows.append({"product": product, "language": language, "path": path, "version": edition,
                         "base_version": base, "availability": "not_generated"})
    english = version.get("english_edition")
    if english:
        base = english["base_rea_version"]
        for product, key in (("elpx", "download"), ("sharing_zip", "sharing_archive")):
            row = _local_row(root, version, product, english["language"], english[key]["path"], base, base)
            for field in ("sha256", "bytes"):
                if field in english[key] and english[key][field] != row[field]:
                    raise ValueError(f"VERSION.json English metadata differs: {key}.{field}")
            if product == "elpx":
                if row.get("embedded_version") != base:
                    raise ValueError("The English ELPX base version differs from VERSION.json")
                if row.get("declared_editorial_status") != english["declared_editorial_status"]:
                    raise ValueError("The English ELPX editorial label differs from VERSION.json")
            rows.append(row)
    rows.extend(native)
    mediateca = version.get("external_publications", {}).get("mediateca")
    if mediateca:
        rows.append({"product": "mediateca", "language": "es", "path": None,
                     "url": mediateca["item_url"], "download_url": mediateca["download_url"],
                     "version": mediateca["embedded_version"], "base_version": mediateca["embedded_version"],
                     "announced_version": mediateca["announced_version"],
                     "bytes": mediateca["bytes"], "sha256": mediateca["sha256"],
                     "availability": "public_observed", "checked_at_utc": mediateca["checked_at_utc"],
                     "http_status": mediateca["http_status"]})
    return rows


def _current_block(version):
    web, rea = version["web_version"], version["rea_exelearning_version"]
    web_date = revision(version.get("web_revision_date"))
    rea_date = revision(version.get("rea_revision", version.get("prepared_at")))
    lines = [BEGIN, f"La publicación web **{web}** y el REA editable **{rea}** son recursos diferenciados.",
             (f"Revisión web declarada: {web_date}." if web_date else "Revisión web no declarada.") +
             (f" Revisión del REA: {rea_date}." if rea_date else " Revisión del REA no declarada."),
             "Las fechas de revisión no acreditan la fecha de un despliegue."]
    if version.get("exelearning_runtime_version"):
        lines.append(f"El REA utiliza eXeLearning **{version['exelearning_runtime_version']}** y conserva su seguimiento nativo, independiente de la web.")
    lines.extend(["", "- [Web publicada](https://mitomapacanario.org/).",
                  f"- [REA editable vigente · {rea}]({version['download']['path']}).",
                  f"- [Paquete de la publicación {package_version(version)} · incluye el REA {rea}]({version['sharing_archive']['path']}).",
                  f"- [Fuentes web {web} · paquete {package_version(version)}]({version['source_archive']['path']})."])
    english = version.get("english_edition")
    if english:
        lines.extend([f"- [REA editable inglés · base {english['base_rea_version']}]({english['download']['path']}).",
                      f"- [Paquete REA inglés]({english['sharing_archive']['path']})."])
    for row in native_download_rows(version):
        language = "español" if row["language"] == "es" else "inglés"
        lines.append(f"- [ELPX nativo {row['version']} · {language} · eXeLearning {row['exelearning_runtime_version']}]({row['url']}).")
    mediateca = version.get("external_publications", {}).get("mediateca")
    if mediateca:
        lines.append(f"- [Mediateca {mediateca['embedded_version']} · archivo adjunto conservado]({mediateca['item_url']}).")
        lines.append(f"  Nota de la comprobación externa: la ficha anunciaba {mediateca['announced_version']}; se mantiene la edición {mediateca['embedded_version']} del adjunto.")
    lines.extend(["- [Matriz de ediciones, idiomas e identidades](EDICIONES.md).",
                  "- Huellas y tamaños de los ZIP: `SHA256SUMS.txt` y catálogo externo de la entrega.", END])
    return "\n".join(lines)


def _current_change_links(text, version):
    title = "## Correcciones posteriores a la publicación"
    if title not in text or not version.get("release_notes") or not version.get("rea_release_notes"):
        return text
    start = text.index(title) + len(title)
    following = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + following.start() if following else len(text)
    section = text[start:end]
    line = (f"Ver [web {version['web_version']}]({version['release_notes']}) y "
            f"[REA {version['rea_exelearning_version']}]({version['rea_release_notes']}).")
    section = re.sub(r"(?m)^Ver \[web [^\n]+$", lambda _: line, section, count=1)
    return text[:start] + section + text[end:]


def _readme(root, version):
    path = root / "README.md"
    text = source_path(root, "README.md").read_text(encoding="utf-8") if path.exists() else "# MitoMapa canario\n\n## Edición vigente\n\n"
    heading = f"# MitoMapa canario · web {version['web_version']} · REA {version['rea_exelearning_version']}"
    text = re.sub(r"\A#[^\n]*", heading, text, count=1)
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) >= text.index(END):
            raise ValueError("README.md has invalid current-edition markers")
        return _current_change_links(text[:text.index(BEGIN)] + _current_block(version) + text[text.index(END) + len(END):], version)
    section = re.search(r"^## Edición vigente\s*\n", text, re.MULTILINE)
    if not section:
        raise ValueError("README.md has no Edición vigente section")
    following = re.search(r"^## ", text[section.end():], re.MULTILINE)
    end = section.end() + following.start() if following else len(text)
    content = text[section.end():end]
    # Migrate the legacy version paragraph and first list only. All subsequent
    # prose, including contextual historical version references, stays literal.
    links = re.search(r"^- .*\n(?:^- .*\n)*", content, re.MULTILINE)
    replace_end = section.end() + links.end() if links else section.end()
    return _current_change_links(text[:section.end()] + "\n" + _current_block(version) + "\n" + text[replace_end:], version)


def _update_notice(root, version):
    path = root / "README_ACTUALIZACION.txt"
    previous = source_path(root, path.name).read_text(encoding="utf-8") if path.exists() else ""
    historical = re.search(r"^REVISIÓN (?:ANTERIOR|TÉCNICA ANTERIOR)\b", previous, re.MULTILINE)
    tail = previous[historical.start():] if historical else ""
    rea_date = revision(version.get("rea_revision", version.get("prepared_at")))
    lines = [f"MITOMAPA CANARIO · WEB {version['web_version']}",
             f"REA EDITABLE {version['rea_exelearning_version']}" + (f" · REVISIÓN {rea_date}" if rea_date else ""),
             "", "WEB PUBLICADA", "https://mitomapacanario.org/", "", "EDITABLE VIGENTE",
             version['download']['path'],
             f"Abrir con eXeLearning {version.get('exelearning_runtime_version', 'compatible')} y guardar una copia antes de adaptar.",
             "El ELPX y la web son recursos diferenciados, con seguimientos independientes.",
             "", "PAQUETES DE ESTA EDICIÓN",
             f"{version['sharing_archive']['path']}: ELPX vigente y documentación de la entrega.",
             f"{version['source_archive']['path']}: fuentes web sin ZIP ni ELPX anidados.",
             "Los medios nuevos se recuperan con python3 tools/fetch_story_media.py.",
             "Las huellas de los paquetes se consultan en SHA256SUMS.txt y en el catálogo externo.",
             "La matriz EDICIONES.md distingue productos, idiomas y publicaciones observadas.",
             "Las descargas históricas conservan sus archivos, direcciones y condiciones.", ""]
    native = native_download_rows(version)
    if native:
        lines.extend(["ELPX NATIVOS EXTERNOS", ""])
        for row in native:
            language = "Español" if row["language"] == "es" else "Inglés"
            lines.extend([f"{language}: edición {row['version']} para eXeLearning {row['exelearning_runtime_version']}.",
                          row["url"]])
        lines.append("")
    return ("\n".join(lines) + "\n" + tail).encode("utf-8")


def _cell(value):
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def _editions(version, rows):
    lines = ["# Ediciones de MitoMapa", "", "Generado desde `VERSION.json`; no editar esta matriz manualmente.", "",
             "La versión web y la del REA son independientes. `prepared_at` describe la preparación del REA;",
             "`web_revision_date` describe una revisión web, no una fecha de publicación comprobada.", "",
             "Las huellas de los ELPX locales describen esta entrega; los hechos de publicación conservan su fecha de observación.", "",
             "| Producto | Idioma | Versión | Base REA | Ruta o ficha | Bytes | SHA-256 / referencia |",
             "| --- | --- | --- | --- | --- | ---: | --- |"]
    labels = {"web": "Web", "elpx": "ELPX", "native_elpx": "ELPX nativo (externo)",
              "sharing_zip": "ZIP REA", "source_zip": "ZIP fuentes", "mediateca": "Mediateca (adjunto)"}
    for row in rows:
        generated = row["product"] in {"sharing_zip", "source_zip"}
        route = row.get("path") or row.get("url")
        # Web HTML changes during deployment; its local identity is available
        # to the external catalogue. ZIP self-identities cannot go inside ZIPs.
        omit_identity = generated or row["product"] == "web"
        values = [labels[row["product"]], row["language"], row["version"], row.get("base_version"), route,
                  "Consultar catálogo externo" if omit_identity else row.get("bytes"),
                  "SHA256SUMS.txt / catálogo externo" if omit_identity else row.get("sha256")]
        lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
    lines.extend(["", "Los ZIP generados se identifican fuera de los paquetes mediante `SHA256SUMS.txt` y el catálogo",
                  "externo de la entrega. Sus propios tamaños y huellas se omiten aquí para evitar referencias circulares.",
                  "El catálogo externo también puede identificar los HTML locales; una inyección del alojamiento puede cambiar su hash público."])
    native = [row for row in rows if row["product"] == "native_elpx"]
    if native:
        lines.extend(["", "## ELPX nativos externos", "",
                      "Estas ediciones tienen versión y runtime propios. Sus archivos se alojan en GitHub Releases;",
                      "las huellas y tamaños del catálogo identifican los paquetes, sin sustituir una comprobación de disponibilidad pública."])
        for row in native:
            language = "Español" if row["language"] == "es" else "Inglés"
            lines.append(f"- {language}: edición **{row['version']}**, preparada para eXeLearning **{row['exelearning_runtime_version']}**.")
    english = version.get("english_edition")
    if english:
        lines.extend(["", "## Inglés: estado editorial declarado y disponibilidad", "",
                      f"El manifiesto interno del ELPX declara literalmente «{english['declared_editorial_status']}».",
                      english.get("editorial_status_note", "La etiqueta interna y la disponibilidad pública son hechos distintos.")])
        for row in rows:
            if row["product"] == "elpx" and row["language"] == english["language"]:
                observation = row.get("public_observation")
                if observation:
                    lines.append(f"Disponibilidad observada: `{row['availability']}`; HTTP {observation.get('http_status')}; comprobación {observation.get('checked_at_utc')}; referencia `{observation.get('reference_commit')}`.")
                else:
                    lines.append("Disponibilidad pública no comprobada en los metadatos de esta entrega.")
    mediateca = version.get("external_publications", {}).get("mediateca")
    if mediateca:
        lines.extend(["", "## Mediateca: ficha y archivo adjunto", "",
                      f"Edición de Mediateca conservada: **{mediateca['embedded_version']}** (archivo adjunto).",
                      f"La ficha anuncia **{mediateca['announced_version']}**; el ELPX descargado contiene **{mediateca['embedded_version']}**.",
                      f"Comprobación: {mediateca['checked_at_utc']}; HTTP {mediateca['http_status']}.",
                      f"Archivo inspeccionado: {mediateca['download_url']}",
                      "Esta observación externa no sustituye la versión del ELPX servido directamente por MitoMapa."])
    return ("\n".join(lines) + "\n").encode("utf-8")


def document_paths(version):
    """Require guide documents only for the editions being packaged."""
    return DOCUMENT_PATHS | (ENGLISH_GUIDE_PATHS if version.get("english_edition") else frozenset())


def _guide(root, name, version):
    """Synchronize explicitly marked current values, preserving all other bytes.

    Historical credits, observations of Mediateca and versioned manual links
    deliberately have no marker. Titles carry their own marker; a version
    span is never inserted into the title's plain text.
    """
    text = source_path(root, name).read_text(encoding="utf-8")
    seen = set()

    def replace(match):
        field = match["field"]
        value = match["value"]
        numbers = list(re.finditer(r"\b\d+\.\d+\.\d+\b", value))
        if len(numbers) != 1 or (field != "package" and GUIDE_VERSION_FIELDS[field] not in version):
            raise ValueError(f"Invalid current version marker in {name}: {field}")
        selected = numbers[0]
        edition = (package_version(version) if field == "package" else
                   version["english_edition"]["base_rea_version"]
                   if field == "rea" and name in ENGLISH_GUIDE_PATHS
                   else version[GUIDE_VERSION_FIELDS[field]])
        seen.add(field)
        return (match[1] + value[:selected.start()] + edition + value[selected.end():] + match[6])

    rendered, count = GUIDE_VERSION_TAG.subn(replace, text)
    if not {"web", "rea"} <= seen or count != text.count("data-release-version="):
        raise ValueError(f"Missing or invalid current version markers in {name}")

    def download(match):
        product = match[2]
        owner = (version["english_edition"]
                 if name in ENGLISH_GUIDE_PATHS and product != "source" else version)
        key = {"elpx": "download", "sharing": "sharing_archive", "source": "source_archive"}[product]
        target = owner[key]["path"]
        safe_name(target)
        tag, hrefs = re.subn(r'''(\s+href\s*=\s*)(["'])(.*?)\2''',
                            lambda href: href[1] + href[2] + escape(target, quote=True) + href[2],
                            match[0], count=1)
        if hrefs != 1:
            raise ValueError(f"Missing current download href in {name}: {product}")
        return tag

    rendered, downloads = GUIDE_DOWNLOAD_TAG.subn(download, rendered)
    if downloads != text.count("data-release-download="):
        raise ValueError(f"Invalid current download marker in {name}")
    return rendered.encode("utf-8")


def document_outputs(root, version):
    """Return relative paths and UTF-8 bytes, with no writes or Git dependency."""
    root = Path(root)
    web_date = revision(version.get("web_revision_date"))
    rea_date = revision(version.get("rea_revision", version.get("prepared_at")))
    text = (f"MitoMapa canario · web {version['web_version']} · " +
            (f"revisión web del {web_date}" if web_date else "revisión web no declarada") + "\n" +
            f"REA editable {version['rea_exelearning_version']} · " +
            (f"revisión del {rea_date}" if rea_date else "revisión no declarada") + "\n" +
            f"eXeLearning {version.get('exelearning_runtime_version', 'no declarado')} · CC BY-SA 4.0 para materiales propios\n")
    outputs = {"VERSION.txt": text.encode("utf-8"), "version.js": version_module(version),
               "README_ACTUALIZACION.txt": _update_notice(root, version),
               "README.md": _readme(root, version).encode("utf-8"),
               "EDICIONES.md": _editions(version, product_rows(root, version))}
    for name in document_paths(version) & (SPANISH_GUIDE_PATHS | ENGLISH_GUIDE_PATHS):
        outputs[name] = _guide(root, name, version)
    return outputs


def check_documents(root, version):
    outputs = document_outputs(root, version)
    changed = [name for name, data in outputs.items() if not (root / name).is_file() or source_path(root, name).read_bytes() != data]
    if changed:
        raise ValueError("Release documents differ from VERSION.json: " + ", ".join(changed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate release documents without writing")
    args = parser.parse_args()
    version = json.loads(source_path(ROOT, "VERSION.json").read_text(encoding="utf-8"))
    if args.check:
        check_documents(ROOT, version)
    else:
        for name, data in document_outputs(ROOT, version).items():
            destination = ROOT / name
            if destination.is_symlink():
                raise ValueError(f"Symbolic-link document: {name}")
            destination.write_bytes(data)
    print("Verified release documents" if args.check else "Updated release documents")


if __name__ == "__main__":
    main()
