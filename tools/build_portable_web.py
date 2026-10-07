#!/usr/bin/env python3
"""Build the local MitoMapa application bundled as a resource in an ELPX.

The native project can embed content/resources/mitomapa/index.html with an
iframe and offer a separate-window link to the same file. No published website
is required to run the map, stories, activities, teacher guide or narrations.
Bibliographic links remain external references. ELPX/ZIP downloads are handled
by the native document's Download source file iDevice, avoiding nested packages.
"""

from __future__ import annotations

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
APPLICATION_VERSION = "4.4.0"
DOCUMENTS = (
    "GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html", "AUDIO_CREDITOS.html",
    "AUDIO_ORIGENES.json", "AUDIO_SELECCION.json", "CREDITOS_MATERIALES.csv",
    "LICENCIA_Y_CREDITOS.txt", "tools/prepare_narrations.py",
)
TEMPLATES = (
    "downloads/Cuaderno_de_ruta_MitoMapa_web_4_0.html",
    "downloads/Rubrica_lectura_MitoMapa_4_0.html",
    "downloads/Rubrica_MitoMapa_4_0.csv",
)


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attributes = dict(attributes)
        for attribute in ("src", "href", "poster", "action"):
            value = attributes.get(attribute)
            if value:
                kind = "stylesheet" if tag == "link" and attribute == "href" and "stylesheet" in (attributes.get("rel") or "").split() else attribute
                self.references.append((tag, kind, value))
        for candidate in (attributes.get("srcset") or "").split(","):
            if candidate.strip():
                self.references.append((tag, "srcset", candidate.strip().split()[0]))


def references(html: str) -> list[tuple[str, str, str]]:
    parser = References()
    parser.feed(html)
    return parser.references


def replace_section(html: str, heading: str, replacement: str) -> str:
    expression = rf"<section[^>]*>\s*<h2>{re.escape(heading)}</h2>.*?</section>"
    result, count = re.subn(expression, replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Missing reuse-guide section: {heading}")
    return result


def portable_index(html: str, version: str) -> str:
    template_links = "".join((
        '<li><a href="downloads/Cuaderno_de_ruta_MitoMapa_web_4_0.html">Abrir el cuaderno de ruta</a></li>',
        '<li><a href="downloads/Rubrica_lectura_MitoMapa_4_0.html">Abrir la rúbrica de lectura e impresión</a></li>',
        '<li><a href="downloads/Rubrica_MitoMapa_4_0.csv" download>Descargar la rúbrica editable (CSV)</a></li>',
    ))
    replacement = (
        '<section class="section panel reuse-panel" aria-labelledby="reuseTitle">'
        '<div class="reuse-heading"><img src="assets/images/pintadera_roseta.webp" width="72" height="72" alt="" aria-hidden="true" loading="lazy">'
        '<div><p class="challenge-kicker">Un recurso para compartir y adaptar</p>'
        '<h2 id="reuseTitle">Conserva y adapta el recurso</h2></div></div>'
        '<p data-elpx-source-notice>Esta aplicación está incluida en el proyecto eXeLearning. '
        'Para conservar el archivo editable completo, vuelve al documento eXeLearning y utiliza '
        '<strong>«Descargar el REA editable (.elpx)»</strong>, en Créditos, fuentes y licencia. '
        'No necesitas descargar otra copia de la web.</p>'
        '<p>Puedes adaptar y compartir los materiales propios con atribución, sin fines comerciales y '
        'manteniendo la licencia <a rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es">'
        'CC BY-NC-SA 4.0</a>. Indica los cambios y conserva los créditos.</p>'
        '<div class="rea-downloads"><article class="download-card"><h3>Preparar la actividad</h3>'
        '<p>Consulta las orientaciones de lectura, creación y acompañamiento.</p>'
        '<a class="button secondary" href="GUIA_DOCENTE.html">Abrir la guía docente</a></article>'
        '<article class="download-card"><h3>Adaptar y guardar</h3><p>Conoce las dos partes del proyecto y cómo conservar el trabajo.</p>'
        '<a class="button secondary" href="GUIA_REUTILIZACION.html">Abrir la guía de reutilización</a></article></div>'
        '<div class="classroom-materials"><h3>Materiales para el aula</h3>'
        '<p>Acuerda las tareas con tu docente. Puedes imprimir las plantillas o adaptar una copia.</p>'
        f'<ul>{template_links}</ul></div>'
        f'<p>Aplicación interactiva {escape(version)}, incluida con sus archivos locales, imágenes y ocho narraciones de Jesica Fortes Regalado. '
        'Su seguimiento se guarda desde Docente y es independiente del Informe de progreso y el pasaporte de las actividades nativas de eXeLearning. '
        'Las fuentes bibliográficas externas requieren conexión; el mapa, los cuentos, los juegos y las grabaciones están incluidos en el paquete.</p></section>'
    )
    html, count = re.subn(
        r'<section class="section panel reuse-panel"[^>]*>.*?</section>',
        lambda _: replacement, html, count=1, flags=re.S,
    )
    if count != 1:
        raise ValueError("Missing download/reuse panel in index.html")
    # Public-site metadata should not identify the portable copy as that URL.
    html = re.sub(r'<link\b[^>]*\brel="canonical"[^>]*>\s*', "", html)
    html = re.sub(r'<meta\b[^>]*\b(?:property|name)="(?:og:url|og:image|twitter:image)"[^>]*>\s*', "", html)
    html = re.sub(r'Versión web \d+\.\d+\.\d+', f'Aplicación portable {escape(version)}', html)
    return html


def portable_reuse_guide(html: str, version: str) -> str:
    html, count = re.subn(
        r'<p><strong>(?:Versión de esta web|Distribución web):</strong>.*?</p>',
        '<p><strong>Aplicación interactiva incluida:</strong> ' + escape(version) +
        ' · <strong>Proyecto editable:</strong> el paquete eXeLearning que contiene esta carpeta. '
        'Consulta su ficha para identificar la edición del proyecto y del programa utilizado.</p>',
        html, count=1, flags=re.S,
    )
    if count != 1:
        raise ValueError("Missing reuse-guide version paragraph")
    if "<h2>Descargas de esta edición</h2>" in html:
        html = replace_section(html, "Descargas de esta edición", (
            '<section><h2>Conservar el proyecto completo</h2><p>Esta aplicación ya está incluida en el paquete. '
            'Para obtener el archivo editable completo utiliza «Descargar el REA editable (.elpx)» '
            'en Créditos, fuentes y licencia del documento eXeLearning. No necesitas consultar ni descargar otra edición desde Internet.</p></section>'
        ))
    html = re.sub(
        r'<p>Estas interacciones están disponibles en la web y (?:en su ZIP editable|en el explorador incluido en el ELPX)\..*?</p>',
        '<p>El mapa con pistas, las secuencias y el comparador están incluidos en esta aplicación portable dentro del ELPX. '
        'Funcionan con los archivos locales del paquete. Las actividades nativas de eXeLearning conservan su propia edición y seguimiento.</p>',
        html, count=1, flags=re.S,
    )
    html = replace_section(html, "Adaptación sin programación", (
        '<section><h2>Adaptación sin programación</h2><p>Guarda una copia del ELPX antes de editarlo. '
        'Abre el proyecto en una versión compatible de eXeLearning para adaptar los textos y las actividades nativas. '
        'Sus cuentos, audios y orientaciones permanecen disponibles en el proyecto. '
        'La aplicación interactiva está incluida como un recurso local con su propio código; los cambios de los iDevices '
        'no modifican automáticamente esa copia. Tras una adaptación, revisa la apertura, la navegación y la exportación en tu instalación.</p></section>'
    ))
    html = replace_section(html, "Código en GitHub", (
        '<section><h2>Adaptar la aplicación portable</h2><p>La carpeta de la aplicación está en '
        '<strong>content/resources/mitomapa</strong> dentro del paquete ELPX. Conserva una copia antes de modificarla. '
        'Sus archivos index.html, scripts.js y styles.css contienen la presentación, los relatos y las actividades. '
        'Los módulos de navegación, recorrido, exploración, historias, comparación y Docente conservan sus archivos JS y CSS. '
        'narraciones.js asigna las grabaciones de assets/audio; las imágenes están en assets/images. '
        'La guía docente y los créditos están incluidos como documentos HTML. '
        'Prueba las rutas afectadas y conserva los identificadores y las claves de almacenamiento para mantener la compatibilidad. '
        'Indica tus cambios y conserva la atribución y la licencia. Consulta '
        '<a href="README_PORTABLE.txt">las instrucciones de esta carpeta</a>.</p></section>'
    ))
    html = replace_section(html, "Compartir y conservar", (
        '<section><h2>Compartir y conservar</h2><p>El archivo ELPX incluye las actividades nativas y esta aplicación con '
        'sus imágenes, guías y dieciséis MP3; no incluye respuestas de estudiantes. '
        'El botón «Descargar el REA editable (.elpx)» del documento eXeLearning permite conservar el proyecto completo. '
        'La carpeta de la aplicación también puede alojarse en un servidor estático o abrirse desde su index.html. '
        'El guardado y algunas funciones pueden depender del navegador al utilizar archivos locales. '
        'Para probarla con un servidor, ejecuta python -m http.server 8000 en esta carpeta y abre http://localhost:8000. '
        'El contenido y los audios locales funcionan sin consultar la web publicada; las fuentes enlazadas y cualquier formulario '
        'externo requieren conexión. No se incluyen ELPX ni ZIP anidados dentro de esta carpeta.</p></section>'
    ))
    html = replace_section(html, "Informe nativo de eXeLearning", (
        '<section><h2>Informe nativo de eXeLearning</h2><p>El Informe de progreso del documento eXeLearning registra '
        'las actividades nativas configuradas para esa edición y ese itinerario. '
        'No recibe automáticamente las respuestas ni las pintaderas de esta aplicación. '
        'El pasaporte nativo y las producciones abiertas requieren el acompañamiento y la revisión acordados con el docente. '
        'En la aplicación, Docente → Guardar seguimiento permite descargar una copia local de su propio progreso. '
        'La selección de tareas puede cambiar según el grupo; una actividad opcional pendiente no impide cerrar la sesión acordada.</p></section>'
    ))
    return html


def verify_portable_web(target: Path) -> dict:
    missing: list[str] = []
    external: set[str] = set()
    files = sorted(path for path in target.rglob("*") if path.is_file() and path.name != "PORTABLE_MANIFEST.json")

    def inspect(owner: Path, tag: str, attribute: str, reference: str) -> None:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme in {"http", "https"} or parsed.netloc:
                external.add(reference)
                if tag in {"script", "img", "audio", "source", "iframe", "css"} or (tag == "link" and attribute == "stylesheet"):
                    missing.append(f"External runtime dependency in {owner.relative_to(target)}: {reference}")
            return
        if not parsed.path:
            return
        candidate = (owner.parent / unquote(parsed.path)).resolve()
        if not candidate.is_relative_to(target.resolve()) or not candidate.is_file():
            missing.append(f"{owner.relative_to(target)}: {reference}")

    for path in files:
        if path.suffix in {".elpx", ".zip"}:
            missing.append(f"Nested source archive: {path.relative_to(target)}")
        if path.suffix == ".html":
            source = path.read_text(encoding="utf-8")
            for tag, attribute, reference in references(source):
                inspect(path, tag, attribute, reference)
        elif path.suffix == ".css":
            for value in re.findall(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", path.read_text(encoding="utf-8")):
                inspect(path, "css", "src", value.strip())
        elif path.suffix == ".js":
            for value in re.findall(r"['\"](assets/(?:images|audio)/[^'\"]+)['\"]", path.read_text(encoding="utf-8")):
                inspect(path, "script", "src", value)
    if missing:
        raise ValueError("Invalid portable application:\n" + "\n".join(missing))
    return {"checked_files": len(files), "external_reference_count": len(external), "missing_dependencies": []}


def build_portable_web(targetdir: str | Path, *, application_version: str = APPLICATION_VERSION) -> dict:
    """Copy the standalone application and return its package manifest.

    Returned ``files`` are POSIX paths relative to targetdir, including the
    generated manifest. Add every file to the ELPX and its source-file manifest.
    """
    target = Path(targetdir).resolve()
    if target == ROOT or ROOT.is_relative_to(target) or target.is_relative_to(ROOT / "assets"):
        raise ValueError("Choose a separate destination for the portable application")
    target.mkdir(parents=True, exist_ok=True)
    release = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    version = application_version
    index = portable_index((ROOT / "index.html").read_text(encoding="utf-8"), version)
    required = set(DOCUMENTS) | set(TEMPLATES) | {"favicon.svg"}
    for tag, attribute, reference in references(index):
        if tag == "script" or (tag == "link" and reference.endswith(".css")):
            required.add(reference)
    required.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "assets").rglob("*") if path.is_file())
    for name in sorted(required):
        source = ROOT / name
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(f"Required application file: {name}")
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if name == "scripts.js":
            # Distribution-only download changes do not change this application's edition.
            script = destination.read_text(encoding="utf-8")
            destination.write_text(script.replace(str(release["web_version"]), version), encoding="utf-8")
    (target / "index.html").write_text(index, encoding="utf-8")
    reuse = portable_reuse_guide((ROOT / "GUIA_REUTILIZACION.html").read_text(encoding="utf-8"), version)
    (target / "GUIA_REUTILIZACION.html").write_text(reuse, encoding="utf-8")
    audio_credits = (target / "AUDIO_CREDITOS.html").read_text(encoding="utf-8").replace(
        "El procedimiento reproducible se incluye en el ZIP editable.",
        'El procedimiento reproducible está incluido en <a href="tools/prepare_narrations.py" download>prepare_narrations.py</a>. '
        'Para volver a preparar los MP3 se necesitan los WAV originales, que no se redistribuyen en esta carpeta.',
    )
    (target / "AUDIO_CREDITOS.html").write_text(audio_credits, encoding="utf-8")
    readme = (
        f"MitoMapa: aplicación portable {version} incluida en el proyecto eXeLearning\n\n"
        "Abrir index.html para utilizar la aplicación. Todos los scripts, estilos, imágenes y audios están en esta carpeta.\n"
        "También puede publicarse esta carpeta completa en un servidor estático. Las fuentes bibliográficas externas requieren conexión.\n"
        "Para conservar el ELPX utiliza Descargar el REA editable del documento eXeLearning. No hay archivos ELPX ni ZIP anidados.\n\n"
        "El contenido de los iDevices nativos y el código de esta aplicación se adaptan por separado.\n"
        "Su progreso local no se sincroniza con el Informe de progreso nativo ni con Moodle.\n"
        "Usa Docente -> Guardar seguimiento para conservar las respuestas de la aplicación.\n\n"
        "Código: index.html, scripts.js, styles.css y módulos JS/CSS; registro de audio: narraciones.js.\n"
        "Imágenes: assets/images. Grabaciones: assets/audio. Narradora: Jesica Fortes Regalado.\n"
        "Créditos: AUDIO_CREDITOS.html, AUDIO_ORIGENES.json, CREDITOS_MATERIALES.csv, LICENCIA_Y_CREDITOS.txt.\n"
        "Los efectos son una recreación sonora. Los WAV originales no se incluyen; hacen falta para preparar nuevas mezclas.\n"
        "Conserva la autoría y la licencia CC BY-NC-SA 4.0 e indica tus cambios.\n"
    )
    (target / "README_PORTABLE.txt").write_text(readme, encoding="utf-8")
    validation = verify_portable_web(target)
    paths = sorted(path for path in target.rglob("*") if path.is_file() and path.name != "PORTABLE_MANIFEST.json")
    manifest = {
        "web_version": version,
        "distribution_web_version": str(release["web_version"]),
        "entry_point": "index.html",
        "included_in_elpx": True,
        "runtime_assets_local": True,
        "native_tracking_separate": True,
        "validation": validation,
        "assets": {
            path.relative_to(target).as_posix(): {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for path in paths
        },
        "files": [path.relative_to(target).as_posix() for path in paths] + ["PORTABLE_MANIFEST.json"],
    }
    (target / "PORTABLE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    manifest = build_portable_web(arguments.output_dir)
    print(f"Built MitoMapa {manifest['web_version']}: {len(manifest['files'])} local files in {arguments.output_dir}")


if __name__ == "__main__":
    main()
