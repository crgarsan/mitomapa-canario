#!/usr/bin/env python3
"""Update the latest native eXeLearning projects with the portable web edition.

Requires lxml. Keeps native activity IDs and settings, and synchronizes the ODE
model, editable Text properties, exported pages, search data and source manifest.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from lxml import etree, html
from build_portable_web import build_portable_web
from harden_jspdf_exports import harden_directory

ROOT = Path(__file__).resolve().parent.parent
VERSION = "4.4.0"
NS = {"o": "http://www.intef.es/xsd/ode"}
EXPLORER_ID = "20261006EXPLORER440"
EXPLORER_DEVICE = "20261006TEXPLORER440"
CONTEXT = "{{context_path}}"
APP = CONTEXT + "/content/resources/mitomapa/"


def field(node, tag):
    return node.findtext("o:" + tag, namespaces=NS) or ""


def set_field(node, tag, value):
    node.find("o:" + tag, NS).text = value


def set_property(node, tag, key, value):
    matches = node.findall(f".//o:{tag}[o:key='{key}']/o:value", NS)
    if not matches:
        raise ValueError(f"Missing property {tag}/{key}")
    for match in matches:
        match.text = value


def content_of(component):
    data = json.loads(field(component, "jsonProperties"))
    return data["textTextarea"]


def set_text(component, content):
    data = json.loads(field(component, "jsonProperties"))
    data["textTextarea"] = content
    set_field(component, "jsonProperties", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    # Preserve the official Text template and any feedback outside the content.
    view = html.fragment_fromstring(field(component, "htmlView"))
    target = view.xpath(".//div[@class='exe-text-activity']/div")[0]
    target.clear()
    append_fragments(target, content)
    set_field(component, "htmlView", html.tostring(view, encoding="unicode"))


def append_fragments(target, markup):
    for fragment in html.fragments_fromstring(markup):
        if isinstance(fragment, str):
            if len(target):
                target[-1].tail = (target[-1].tail or "") + fragment
            else:
                target.text = (target.text or "") + fragment
        else:
            target.append(fragment)


def body_markup(element):
    return (element.text or "") + "".join(html.tostring(child, encoding="unicode") for child in element)


def legacy_unescape(value):
    """Decode the JavaScript escape() format used by official native games."""
    return re.sub(r"%u([0-9A-Fa-f]{4})|%([0-9A-Fa-f]{2})", lambda match: chr(int(match[1] or match[2], 16)), value)


def decode_game(value):
    return json.loads("".join(chr(ord(char) ^ 146) for char in legacy_unescape(value)))


def encode_game(data):
    value = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    units = value.encode("utf-16-be")
    encoded = []
    safe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./"
    for offset in range(0, len(units), 2):
        code = int.from_bytes(units[offset:offset + 2], "big") ^ 146
        char = chr(code)
        encoded.append(char if char in safe else f"%{code:02X}" if code < 256 else f"%u{code:04X}")
    return "".join(encoded)


def repair_native_games(components):
    for component in components.values():
        kind = field(component, "odeIdeviceTypeName")
        if kind not in ["quick-questions", "complete"]:
            continue
        view = html.fragment_fromstring(field(component, "htmlView"))
        css = "quext-DataGame" if kind == "quick-questions" else "completa-DataGame"
        node = view.xpath(f".//*[contains(concat(' ',normalize-space(@class),' '),' {css} ')]")[0]
        data = decode_game(node.text_content())
        if kind == "complete":
            # Official Complete runtime reads its cloze text from this element.
            # The previous edition kept it only in the encoded editor data.
            if not view.xpath(".//div[contains(concat(' ',normalize-space(@class),' '),' completa-text-game ')]"):
                text = etree.SubElement(view, "div", attrib={"class": "completa-text-game js-hidden"})
                append_fragments(text, legacy_unescape(data["textText"]))
        else:
            # Remove the editor's sample introduction video. These are text
            # questions, not video activities, and must work without YouTube.
            if data.get("idVideo") == "https://www.youtube.com/watch?v=nj168qvxJzg":
                data["idVideo"] = ""
                data["startVideo"] = 0
                data["endVideo"] = 0
            if data.get("itinerary", {}).get("clueGame", "").startswith("Este es tu número:"):
                data["itinerary"]["clueGame"] = "Puedes continuar con el cuento o elegir otra isla."
            # The question-specific explanations already exist in the project;
            # enable them instead of displaying only the generic point message.
            if all(question.get("msgHit") and question.get("msgError") for question in data["questionsGame"]):
                data["customMessages"] = True
            node.text = encode_game(data)
            if decode_game(node.text) != data:
                raise ValueError("Native game serialization changed the data")
        set_field(component, "htmlView", html.tostring(view, encoding="unicode"))


def routes():
    source = (ROOT / "scripts.js").read_text()
    start = source.index("[", source.index("const routes"))
    return json.JSONDecoder().raw_decode(source[start:])[0]


def practical_guide():
    document = html.parse(str(ROOT / "GUIA_DOCENTE.html"))
    section = document.xpath("//section[contains(@class,'teacher-guide')]")[0]
    for paragraph in section.xpath(".//p | .//li"):
        text = paragraph.text_content()
        replacements = {
            "En Inicio → Etapa y ajustes": "<strong>Ajusta la etapa y la lectura.</strong> Acuerda un itinerario y los apoyos. En el Explorador interactivo puedes usar Inicio → Etapa y ajustes de lectura; en los capítulos de eXeLearning, consulta el desplegable de apoyos del cuento.",
            "En «Ajustes y seguimiento»": "<strong>Prepara el Taller.</strong> Selecciona las actividades y la producción que vais a realizar. Las demás son opcionales. Puedes acordar una producción oral, en papel o fuera del recurso.",
            "Puedes desactivar Ambiente suave": "<strong>Escucha con el grupo.</strong> Cada cuento incorpora la narración de Jesica Fortes Regalado. En el Explorador interactivo puedes elegir Ambiente suave y velocidad lenta. Los capítulos de eXeLearning ofrecen voz sola y una alternativa con ambiente; utiliza solo un reproductor a la vez y pausa para conversar.",
            "El seguimiento recuerda": "El Explorador interactivo recuerda el trabajo en este navegador y permite guardar una copia. Los capítulos nativos de eXeLearning tienen su propio informe y un pasaporte manual: ambos seguimientos son independientes. Las conversaciones, investigaciones y creaciones se comparten y comentan contigo.",
            "La pintadera se obtiene": "En el Explorador interactivo, la pintadera se obtiene con la comprensión en Infantil y 1.º ciclo; en las demás etapas, con comprensión y verdadero/falso. En los capítulos nativos, se marca manualmente tras revisar las tareas acordadas. Ningún requisito impide elegir una isla o desarrollar una sesión.",
        }
        for marker, replacement in replacements.items():
            if marker in text:
                paragraph.clear()
                append_fragments(paragraph, replacement)
                break
    return html.tostring(section, encoding="unicode") + (
        f'<p><a href="{APP}GUIA_DOCENTE.html" target="_blank" rel="noopener">'
        'Abrir o imprimir la guía de la versión interactiva</a>.</p>'
    )


def update_model(tree, source_hash, source_name):
    root = tree.getroot()
    pages = root.findall(".//o:odeNavStructure", NS)
    components = {field(c, "odeIdeviceId"): c for c in root.findall(".//o:odeComponent", NS)}
    repair_native_games(components)
    islands = pages[2:10]
    data_routes = routes()
    set_property(root, "odeProperty", "pp_modified", "2026-10-06T00:00:00Z")
    set_property(root, "odeProperty", "pp_addPagination", "false")
    set_property(root, "odeResource", "odeVersionId", "20261006MITOMAPA440")
    set_property(root, "odeProperty", "pp_description", "REA editable con ocho cuentos, narraciones de Jesica, elección libre de islas, pintaderas y guía docente práctica. Incluye las actividades nativas y el explorador interactivo portable de la web 4.4.0.")
    set_property(root, "odeProperty", "pp_license", "creative commons: attribution - share alike 4.0")
    set_property(root, "odeProperty", "pp_licenseUrl", "https://creativecommons.org/licenses/by-sa/4.0/")
    footer = f'<p>MitoMapa canario: ocho islas, ocho pintaderas · Jesica Fortes Regalado; Gloria Elsa González Martín; Cristian García Santana · CC BY-SA 4.0</p><p>Edición del REA eXeLearning {VERSION} · narración: Jesica Fortes Regalado</p>'
    set_property(root, "odeProperty", "footer", footer)
    for page in islands:
        name = re.sub(r"^\d+\.\s*", "", field(page, "pageName"))
        set_field(page, "pageName", name)
        for key in ["titlePage", "titleNode"]:
            set_property(page, "odeNavStructureProperty", key, name)

    cards = []
    for route, page in zip(data_routes, islands):
        name = field(page, "pageName").split(":", 1)[0]
        cards.append(f'<a href="exe-node:{field(page,"odePageId")}" style="display:inline-flex;flex-direction:column;align-items:center;gap:.5rem;min-width:130px;padding:1rem;border:1px solid #bfae97;border-radius:12px;text-decoration:none"><img src="{CONTEXT}/content/resources/{route["badge"]}" alt="" width="80" height="80" style="object-fit:contain"><strong>{name}</strong></a>')
    grid = '<div style="display:flex;flex-wrap:wrap;gap:.75rem;justify-content:center">' + "".join(cards) + "</div>"
    intro = f'''<p><strong>Edición del REA {VERSION} · elige tu propia ruta</strong></p>
<h2>Tu viaje por los cuentos de Canarias</h2>
<p>Elige una isla, lee o escucha su cuento y comparte lo que descubres. Puedes empezar por donde quieras y volver a cualquier isla.</p>
<p><a href="exe-node:{EXPLORER_ID}"><strong>Abrir el mapa y los juegos interactivos →</strong></a></p>
<h3>Elige una pintadera para abrir su cuento</h3>{grid}
<p>Las pintaderas son símbolos de esta expedición, sin numeración ni orden obligatorio. No representan una atribución arqueológica a cada isla.</p>
<details><summary>Cómo empezar</summary><ol><li>Elige una isla y escucha a Jesica Fortes Regalado o lee el cuento.</li><li>Conversa y realiza las tareas que hayas acordado con tu docente.</li><li>Crea una respuesta oral, escrita, dibujada o representada y compártela.</li></ol><p>No necesitas resolver el puzle ni reunir pintaderas para acceder a los cuentos. Puedes repetir, pedir ayuda o cambiar de isla.</p></details>
<p><strong>Autoría:</strong> Jesica Fortes Regalado, Gloria Elsa González Martín y Cristian García Santana. <a href="exe-node:20260823155836GUIAXU">Guía docente</a> · <a href="exe-node:20260823155836CREDIT">Créditos y licencia</a>.</p>'''
    # The credits page ID comes from the original project rather than a slug.
    intro = intro.replace("exe-node:20260823155836CREDIT", "exe-node:" + field(pages[-1], "odePageId"))
    set_text(components["20260823155836TINTRO"], intro)
    # The old preset copies customized the rendered passport, but retained the
    # complete edition's Text JSON. Preserve the preset's explanation on editing.
    passport = components["20260823155836TPASSI"]
    passport_view = html.fragment_fromstring(field(passport, "htmlView"))
    passport_content = passport_view.xpath(".//div[@class='exe-text-activity']/div")[0]
    set_text(passport, body_markup(passport_content).replace("4.0.2", VERSION))

    itinerary = components["20260823155836TITINW"]
    content = content_of(itinerary)
    content = re.sub(r'<h3>Rutas</h3>.*?<\/ol>', '<h3>Rutas sin orden obligatorio</h3>' + grid, content, flags=re.S)
    set_text(itinerary, content)
    for route, page in zip(data_routes, islands):
        story = page.find(".//o:odeComponent[o:odeIdeviceTypeName='text']", NS)
        content = content_of(story)
        content = re.sub(r"Ruta \d+ · Cuento legendario", "Cuento legendario", content)
        content = re.sub(r'<p><strong>Locución:</strong>.*?</p>', '', content, flags=re.S)
        name = field(page, "pageName").split(":", 1)[0]
        player = f'''<section aria-label="Escuchar el cuento de {name}"><h3>Escucha a Jesica Fortes Regalado</h3><p>Voz sola. Puedes pausar y volver al texto cuando lo necesites.</p><audio controls="controls" preload="none" aria-label="Narración de {name}, voz de Jesica Fortes Regalado" style="width:100%;max-width:550px" src="{APP}assets/audio/{route['id']}.mp3">Tu navegador no permite reproducir el audio. <a href="{APP}assets/audio/{route['id']}.mp3">Abrir la narración</a>.</audio><details><summary>Escuchar con un ambiente suave al principio</summary><p>Alternativa con una introducción tenue de percusión y naturaleza, recreada digitalmente. Pausa la voz sola antes de iniciar esta versión.</p><audio controls="controls" preload="none" aria-label="Narración de {name} con ambiente suave" style="width:100%;max-width:550px" src="{APP}assets/audio/{route['id']}-ambiente.mp3">Tu navegador no permite reproducir el audio. <a href="{APP}assets/audio/{route['id']}-ambiente.mp3">Abrir la narración con ambiente</a>.</audio></details></section>'''
        # Keep the whole transcript and native itinerary editable.
        heading_end = content.index("</h2>") + len("</h2>")
        content = content[:heading_end] + player + content[heading_end:]
        # eXe's legacy importer treats a resource href fragment as a filename.
        # Link to the local application's entry point without triggering that warning.
        content += f'<p><a href="{APP}index.html" target="_blank" rel="noopener">Abrir el explorador interactivo</a> y elegir {name} para practicar «Ordena el cuento». <a href="exe-node:{EXPLORER_ID}">Mapa, pistas y comparación de cuentos</a>.</p>'
        set_text(story, content)

    set_text(components["20260823155837TGUID1"], practical_guide())
    teacher_page = pages[11]
    for block in teacher_page.findall(".//o:odePagStructure", NS):
        if field(block, "blockName") == "Aplicación en el aula":
            set_field(block, "blockName", "Guía para desarrollar la actividad")
        elif field(block, "blockName") == "Currículo y evaluación":
            set_field(block, "blockName", "Orientaciones y seguimiento opcional")
    c = components["20260823155837TGUID2"]
    set_text(c, content_of(c).replace("4.0.2", VERSION))
    set_text(components["20260823155837TGUID3"], f'''<h2>Edición y reutilización</h2><p>El archivo conserva los 94 iDevices originales y añade un iDevice Texto para el Explorador interactivo. Los cuentos, las actividades nativas, los reproductores y la guía se pueden modificar en eXeLearning. Los identificadores y los ajustes del informe nativo se conservan.</p><p>El Explorador incluye una copia local del código de la web 4.4.0: mapa con pintaderas, pistas, secuencias, comparación, vistas ordenadas, ajustes de lectura y seguimiento. Su interfaz se abre dentro del recurso o en una pestaña; su código HTML, CSS y JavaScript se conserva en <code>content/resources/mitomapa</code>. Esas funciones se adaptan editando su código, no desde los formularios de los juegos nativos.</p><h3>Audio y acceso</h3><p>Los ocho cuentos incluyen la voz grabada de Jesica Fortes Regalado y una alternativa con ambiente suave. Las 16 pistas están dentro del paquete. Se inicia la reproducción al pulsar los controles; no hay reproducción automática. El texto completo sigue disponible.</p><h3>Elegir y acompañar</h3><p>No hay isla inicial ni una secuencia obligatoria. Selecciona las rutas y tareas con el grupo y usa los apoyos necesarios. El pasaporte y el informe nativos son independientes del seguimiento del Explorador; no se sincronizan con la web publicada.</p><h3>Conservar y adaptar</h3><p>Guarda una copia del ELPX {VERSION}. Duplica el proyecto, adapta los contenidos y comprueba una exportación antes de usarla. Conserva la autoría, indica los cambios y distribuye la adaptación con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.es" target="_blank" rel="noopener">CC BY-SA 4.0</a>. Las fuentes externas conservan sus condiciones de uso.</p><p>Los cuentos, las imágenes, los juegos y los audios son locales. Las fuentes de investigación y el cuestionario externo requieren conexión. Prepara fuentes accesibles para el trabajo sin Internet.</p><p><a href="{APP}GUIA_REUTILIZACION.html" target="_blank" rel="noopener">Guía de reutilización y atribución</a> · <a href="{APP}AUDIO_CREDITOS.html" target="_blank" rel="noopener">Créditos de audio</a>.</p>''')
    locution = components["20260823155837TLOC1D"]
    old = content_of(locution)
    old = re.sub(r'^.*?(?=<h3>Tenerife)', '', old, flags=re.S)
    set_text(locution, f'''<h2>Narraciones y uso del sonido</h2><p><strong>Narración: Jesica Fortes Regalado.</strong> Se han seleccionado ocho grabaciones, una por cuento, y se han ajustado su volumen y formato para facilitar la escucha. Las grabaciones originales no se han sustituido por una voz generada.</p><p>Cada cuento ofrece voz sola y una alternativa con ambiente breve y tenue. La percusión inspirada en tambores y chácaras y los sonidos de naturaleza son recreaciones digitales; no son grabaciones tradicionales de intérpretes canarios. El ambiente desaparece al comenzar la narración.</p><p>Mantén visible el texto, permite pausas para conversar y utiliza una sola pista a la vez. En el Explorador puedes elegir velocidad lenta y desactivar el ambiente.</p><p><a href="{APP}AUDIO_CREDITOS.html" target="_blank" rel="noopener">Selección de tomas y créditos</a>.</p><details><summary>Estribillos y orientación para leer en voz alta</summary>{old}</details>''')
    credits = components["20260823155837TCRED0"]
    content = content_of(credits).replace("en eXeLearning el pasaporte se marca manualmente y las locuciones grabadas quedan pendientes.", "el pasaporte nativo de eXeLearning es manual; el Explorador portable tiene seguimiento propio. Esta edición incluye las narraciones de Jesica en ambos recorridos.")
    content += f'<h3>Créditos de las narraciones</h3><p>Narración de los ocho cuentos: Jesica Fortes Regalado. Selección de tomas y edición técnica documentadas en <a href="{APP}AUDIO_CREDITOS.html" target="_blank" rel="noopener">Créditos de audio</a>. Ambientación opcional recreada digitalmente, inspirada en percusión y naturaleza.</p>'
    set_text(credits, content)
    history = components["20260930IHISTORIA40"]
    set_text(history, f'''<h2>Edición actual {VERSION} · 6 de octubre de 2026</h2><p>Actualiza el REA nativo 4.0.2 con las mejoras de la web 4.4.0: islas sin numeración, pintaderas con acceso directo, explorador y pistas, secuencias y comparación, interfaz ordenada, guía práctica y las narraciones de Jesica con ambiente opcional.</p><p>Se conservan los cuentos corregidos, sus fuentes, los identificadores y las actividades nativas. Las funciones web también se incluyen como aplicación local. El seguimiento de ambas partes es independiente.</p><details><summary>Archivo editable de partida</summary><p>{source_name}</p><p>SHA-256: <code>{source_hash}</code></p></details><details><summary>Historia de la edición 4.0</summary>{content_of(history)}</details>''')

    # Add an independent chapter, so the complete web does not clutter Inicio.
    new_page = deepcopy(pages[12])
    set_field(new_page, "odePageId", EXPLORER_ID)
    set_field(new_page, "odeParentPageId", field(pages[0], "odePageId"))
    set_field(new_page, "pageName", "Explorador interactivo")
    set_field(new_page, "odeNavStructureOrder", "1")
    for key in ["titlePage", "titleNode"]:
        set_property(new_page, "odeNavStructureProperty", key, "Explorador interactivo")
    set_property(new_page, "odeNavStructureProperty", "description", "Mapa libre, pintaderas y juegos de los cuentos")
    block = new_page.find(".//o:odePagStructure", NS)
    set_field(block, "odePageId", EXPLORER_ID)
    set_field(block, "odeBlockId", "20261006BEXPLORER440")
    set_field(block, "blockName", "Explora las islas a tu ritmo")
    component = block.find(".//o:odeComponent", NS)
    for key, value in [("odePageId", EXPLORER_ID), ("odeBlockId", "20261006BEXPLORER440"), ("odeIdeviceId", EXPLORER_DEVICE)]:
        set_field(component, key, value)
    data = json.loads(field(component, "jsonProperties"))
    data["ideviceId"] = EXPLORER_DEVICE
    set_field(component, "jsonProperties", json.dumps(data, ensure_ascii=False))
    set_text(component, f'''<p>Elige una isla en el mapa o en la lista de pintaderas. Puedes entrar por donde quieras, escuchar los cuentos, ordenar sus acontecimientos y comparar dos relatos.</p><p><a href="{APP}index.html" target="_blank" rel="noopener"><strong>Abrir el explorador en una pestaña completa →</strong></a></p><iframe src="{APP}index.html" title="MitoMapa: mapa, cuentos y juegos interactivos" width="100%" height="900" style="width:100%;height:900px;border:1px solid #cdbf9f;border-radius:12px" loading="lazy"></iframe><details><summary>Retomar el trabajo</summary><p>El explorador recuerda el trabajo en este navegador y permite guardar una copia. Si prefieres utilizar los capítulos de este libro, sus actividades y pasaporte tienen un seguimiento independiente. Acuerda con tu docente qué tareas realizar y cómo compartir tu creación.</p></details>''')
    for page in pages[1:]:
        set_field(page, "odeNavStructureOrder", str(int(field(page, "odeNavStructureOrder")) + 1))
    pages[0].getparent().insert(1, new_page)

    # Optional material is initially collapsed; stories and the practical guide remain open.
    for page in root.findall(".//o:odeNavStructure", NS):
        for block in page.findall(".//o:odePagStructure", NS):
            name = field(block, "blockName")
            if name in ["Puzle del archipiélago", "Elige tu itinerario", "Orientaciones y seguimiento opcional", "Ficha técnica"] or page in islands and name != "Cuento ilustrado":
                set_property(block, "odePagStructureProperty", "minimized", "true")
    return footer


def exported_content(value, page_path, paths):
    prefix = "../" if page_path.startswith("html/") else ""
    value = value.replace(CONTEXT + "/", prefix)
    def node_link(match):
        target = paths[match.group(1)]
        relative = posixpath.relpath(target, posixpath.dirname(page_path) or ".")
        return relative + (match.group(2) or "")
    return re.sub(r"exe-node:([A-Za-z0-9]+)(#[^\"'<>\s]*)?", node_link, value)


def update_export(folder, tree, footer):
    root = tree.getroot()
    search_path = folder / "search_index.js"
    search = json.loads(search_path.read_text().removeprefix("window.exeSearchData = ").rstrip(";\n"))
    paths = {pid: value["fileUrl"] for pid, value in search.items()}
    paths[EXPLORER_ID] = "html/explorador-interactivo.html"
    pages = root.findall(".//o:odeNavStructure", NS)
    explorer_template = folder / paths[field(pages[-2], "odePageId")]
    shutil.copyfile(explorer_template, folder / paths[EXPLORER_ID])
    for page in pages:
        pid = field(page, "odePageId")
        path = paths[pid]
        document = html.parse(str(folder / path))
        if pid == EXPLORER_ID:
            old_pid = field(pages[-2], "odePageId")
            document.getroot().set("id", "exe-" + EXPLORER_ID)
            document.xpath("//main")[0].set("id", EXPLORER_ID)
            document.xpath("//a[@id='skipNav']")[0].set("href", "#" + EXPLORER_ID)
            document.xpath(f"//div[@id='page-content-{old_pid}']")[0].set("id", "page-content-" + EXPLORER_ID)
            template_component = document.xpath("//div[@data-idevice-type='text']")[0]
            template_component.set("id", EXPLORER_DEVICE)
            template_component.set("data-idevice-json-data", json.dumps({"ideviceId": EXPLORER_DEVICE}))
            article = template_component.xpath("ancestor::article")[0]
            article.set("id", "20261006BEXPLORER440")
        for component in page.findall(".//o:odeComponent", NS):
            iid = field(component, "odeIdeviceId")
            target = document.xpath(f'//div[@id="{iid}"]')
            if not target:
                raise ValueError(f"Missing exported component {path}: {iid}")
            target = target[0]
            for child in list(target):
                target.remove(child)
            target.text = None
            append_fragments(target, exported_content(field(component, "htmlView"), path, paths))
        for block in page.findall(".//o:odePagStructure", NS):
            bid = field(block, "odeBlockId")
            article = document.xpath(f'//article[@id="{bid}"]')[0]
            article.xpath(".//h1[@class='box-title']")[0].text = field(block, "blockName")
            minimized = block.find(".//o:odePagStructureProperty[o:key='minimized']/o:value", NS).text == "true"
            if minimized:
                article.set("class", "box minimized")
                button = article.xpath(".//button[contains(@class,'box-toggle')]")[0]
                button.set("class", "box-toggle box-toggle-off")
                article.xpath("./div[@class='box-content']")[0].set("style", "display:none")
        document.xpath("//h1[@class='page-title']")[0].text = field(page, "pageName")
        document.xpath("//title")[0].text = field(page, "pageName") + " | MitoMapa canario"
        for node in document.xpath("//*[contains(concat(' ',normalize-space(@class),' '),' page-counter ')] | //div[contains(concat(' ',normalize-space(@class),' '),' nav-buttons ')]"):
            node.getparent().remove(node)
        nav = document.xpath("//nav//ul")[0]
        for child in list(nav):
            nav.remove(child)
        for target_page in pages:
            target_pid = field(target_page, "odePageId")
            li = etree.SubElement(nav, "li")
            a = etree.SubElement(li, "a", href=posixpath.relpath(paths[target_pid], posixpath.dirname(path) or "."))
            a.text = field(target_page, "pageName")
            if target_pid == pid:
                li.set("class", "active")
                a.set("class", "active")
        user_footer = document.xpath("//div[@id='siteUserFooter']")[0]
        user_footer.clear()
        user_footer.set("id", "siteUserFooter")
        append_fragments(user_footer, footer)
        (folder / path).write_bytes(html.tostring(document, encoding="utf-8", method="html", doctype="<!DOCTYPE html>"))
        # Update search from the same authoritative model, including the added page.
        info = search.get(pid, deepcopy(search[field(pages[-2], "odePageId")]))
        info.update(name=field(page, "pageName"), fileName=path.rsplit("/", 1)[-1], fileUrl=path, blocks={})
        position = pages.index(page)
        info["isIndex"] = position == 0
        info["prePageId"] = field(pages[position - 1], "odePageId") if position else None
        info["nextPageId"] = field(pages[position + 1], "odePageId") if position + 1 < len(pages) else None
        for block in page.findall(".//o:odePagStructure", NS):
            bid = field(block, "odeBlockId")
            info["blocks"][bid] = {"name": field(block, "blockName"), "order": int(field(block, "odePagStructureOrder")), "idevices": {}}
            for component in block.findall(".//o:odeComponent", NS):
                iid = field(component, "odeIdeviceId")
                info["blocks"][bid]["idevices"][iid] = {"order": int(field(component, "odeComponentsOrder")), "htmlView": exported_content(field(component, "htmlView"), path, paths), "jsonProperties": field(component, "jsonProperties")}
        search[pid] = info
    search_path.write_text("window.exeSearchData = " + json.dumps(search, ensure_ascii=False, separators=(",", ":")) + ";\n")


def build(source, destination):
    with tempfile.TemporaryDirectory(prefix="mitomapa-elpx-") as temp:
        folder = Path(temp)
        with ZipFile(source) as archive:
            for name in archive.namelist():
                if name.startswith("/") or ".." in Path(name).parts:
                    raise ValueError(f"Unsafe source path: {name}")
            archive.extractall(folder)
        tree = etree.parse(str(folder / "content.xml"))
        footer = update_model(tree, sha256(source.read_bytes()).hexdigest(), source.name)
        build_portable_web(folder / "content/resources/mitomapa")
        update_export(folder, tree, footer)
        tree.write(str(folder / "content.xml"), encoding="UTF-8", xml_declaration=True, doctype='<!DOCTYPE ode SYSTEM "content.dtd">')
        with (folder / "content.dtd").open("rb") as stream:
            dtd = etree.DTD(stream)
        if not dtd.validate(tree):
            raise ValueError(dtd.error_log)
        harden_directory(folder)
        files = sorted(str(file.relative_to(folder)) for file in folder.rglob("*") if file.is_file())
        manifest = {"version": 1, "files": files, "projectTitle": "MitoMapa canario: ocho islas, ocho pintaderas"}
        (folder / "libs/elpx-manifest.js").write_text("window.__ELPX_MANIFEST__=" + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n")
        temporary = destination.with_suffix(".elpx.tmp")
        with ZipFile(temporary, "w") as archive:
            for name in files:
                entry = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, (folder / name).read_bytes(), compresslevel=6)
        size = temporary.stat().st_size
        if size >= 25 * 1024 * 1024:
            raise ValueError(f"Package exceeds Cloudflare's per-file limit: {size}")
        temporary.replace(destination)
        print(f"{destination.name}: {size:,} bytes; {len(files)} files; SHA256 {sha256(destination.read_bytes()).hexdigest()}")


def main():
    sources = [
        ("MitoMapa_canario_REA_eXeLearning_v4_0_2.elpx", "MitoMapa_canario_REA_eXeLearning_v4_4_0.elpx"),
        ("MitoMapa_REA_v4_0_2_Esencial.elpx", "MitoMapa_REA_v4_4_0_Esencial.elpx"),
        ("MitoMapa_REA_v4_0_2_Intermedio.elpx", "MitoMapa_REA_v4_4_0_Intermedio.elpx"),
    ]
    for source, destination in sources:
        build(ROOT / "downloads" / source, ROOT / "downloads" / destination)


if __name__ == "__main__":
    main()
