"""Apply the publication editor's requirements to the native eXe project.

The native model is authoritative. Exported pages and the search catalogue are
rebuilt from that same model. Multimedia and game questions are preserved;
only repeated project-author credits are cleared from native game metadata.
"""

from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from io import BytesIO
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit

from lxml import etree, html


NS = {"o": "http://www.intef.es/xsd/ode"}
CONTEXT = "{{context_path}}"
APP = CONTEXT + "/content/resources/mitomapa/"
COVER = "GBC20261006PORTADA"
HOME = "20260823155836HOMEJL"
JUSTIFICATION = "GBC20261006JUSTIFICA"
PASSPORT = "20260823155836PASSID"
STORIES = "GBC20261006DESARROLLO"
CLOSING = "20260823155836FINALA"
TEACHER = "20260823155836GUIAXU"
SOURCES = "GBC20261006FUENTES"
CREDITS = "20260823155836CREDJS"
EXTRA = "20261006EXPLORER440"
TEACHER_CHILDREN = (
    "GBC20261006CURRICULO", "GBC20261006METODO", "GBC20261006RECURSOS",
    "GBC20261006SEGUIMIENTO", "20260823155836LOCUT0",
)
AUTHORS = "Jesica Fortes Regalado; Gloria Elsa González Martín; Cristian García Santana"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/deed.es"
PUBLIC_WEB = "https://mitomapa-canario.cgarcias.workers.dev/"
PASSPORT_DEVICE = "20260823155836CHKPAS"
PASSPORT_OLD_FOOTER = "MitoMapa canario · CC BY-NC-SA 4.0"
PASSPORT_FOOTER = "MitoMapa canario · CC BY-SA 4.0"
STORY_IDS = (
    "20260823155836ST1CG9", "20260823155837ST28I4", "20260823155837ST3GFP",
    "20260823155837ST48OR", "20260823155837ST577Q", "20260823155837ST6CHF",
    "20260823155837ST7CGH", "20260823155837ST8IN6",
)
RESEARCH_IDS = (
    "20260823155837RS1L1E", "20260823155837RS28MQ", "20260823155837RS3AL5",
    "20260823155837RS43PN", "20260823155837RS5U02", "20260823155837RS6BYI",
    "20260823155837RS7D16", "20260823155837RS8O96",
)
ISLANDS = (
    ("tenerife", "Tenerife"), ("gran-canaria", "Gran Canaria"),
    ("la-palma", "La Palma"), ("la-gomera", "La Gomera"),
    ("el-hierro", "El Hierro"), ("fuerteventura", "Fuerteventura"),
    ("lanzarote", "Lanzarote"), ("la-graciosa", "La Graciosa"),
)
LANGUAGE_SUBSTITUTIONS = {
    "vais": "van", "hayáis": "hayan", "habéis": "han", "necesitéis": "necesiten",
    "vosotros": "ustedes", "vosotras": "ustedes", "vuestro": "su", "vuestra": "su",
    "vuestros": "sus", "vuestras": "sus", "acordad": "acuerden", "elegid": "elijan",
    "leed": "lean", "escuchad": "escuchen", "comparad": "comparen", "buscad": "busquen",
    "anotad": "anoten", "compartid": "compartan", "podéis": "pueden", "debéis": "deben",
    "haced": "hagan", "tenéis": "tienen", "sois": "son", "estáis": "están",
}


def field(node, key):
    return node.findtext("o:" + key, default="", namespaces=NS)


def set_field(node, key, value):
    target = node.find("o:" + key, NS)
    if target is None:
        raise ValueError(f"Missing native field {key}")
    target.text = value


def set_property(node, kind, key, value):
    matches = node.findall(f".//o:{kind}[o:key='{key}']/o:value", NS)
    if not matches:
        raise ValueError(f"Missing native property {kind}/{key}")
    for target in matches:
        target.text = value


def fragment(markup):
    return html.fragment_fromstring(markup or "<p></p>", create_parent="div")


def inner(node):
    return (node.text or "") + "".join(html.tostring(child, encoding="unicode") for child in node)


def replace_content(node, markup):
    node.text = None
    for child in list(node):
        node.remove(child)
    for child in html.fragments_fromstring(markup):
        if isinstance(child, str):
            if len(node):
                node[-1].tail = (node[-1].tail or "") + child
            else:
                node.text = (node.text or "") + child
        else:
            node.append(child)


def text_of(component):
    return json.loads(field(component, "jsonProperties"))["textTextarea"]


def set_text(component, markup):
    data = json.loads(field(component, "jsonProperties"))
    data["textTextarea"] = markup
    set_field(component, "jsonProperties", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    view = fragment(field(component, "htmlView"))
    template = view.xpath(".//div[@class='exe-text-template']")[0]
    targets = view.xpath(".//div[@class='exe-text-activity']/div")
    if len(targets) != 1:
        raise ValueError(f"Unexpected Text template: {field(component, 'odeIdeviceId')}")
    replace_content(targets[0], markup)
    set_field(component, "htmlView", html.tostring(template, encoding="unicode"))


def local_link(page, label, anchor=""):
    return f'<a href="exe-node:{page}{"#" + anchor if anchor else ""}">{label}</a>'


def box(title, markup, identifier=""):
    key = f' id="{escape(identifier, quote=True)}"' if identifier else ""
    return (f'<details{key} style="margin:1rem 0;border:1px solid #bba98f;padding:.7rem 1rem;border-radius:.3rem">'
            f'<summary style="cursor:pointer;font-weight:bold;min-height:44px;padding:.5rem 0">{title}</summary>'
            f'<div style="padding:.5rem 0">{markup}</div></details>')


def plural_text(value):
    for old, new in LANGUAGE_SUBSTITUTIONS.items():
        value = re.sub(r"\b" + re.escape(old) + r"\b", lambda m: new.capitalize() if m[0][0].isupper() else new, value, flags=re.I)
    return re.sub(r"\bOA\b", "Objeto de Aprendizaje", value)


AUTHOR_FIELD = re.compile(r'("author"\s*:\s*)("(?:[^"\\]|\\.)*")')


def decode_native_payload(value):
    """Return the JSON text and whether the official XOR146 codec was used."""
    try:
        json.loads(value)
        return value, False
    except (ValueError, TypeError):
        escaped = re.sub(r"%u([0-9A-Fa-f]{4})|%([0-9A-Fa-f]{2})", lambda m: chr(int(m[1] or m[2], 16)), value)
        decoded = "".join(chr(ord(char) ^ 146) for char in escaped)
        json.loads(decoded)
        return decoded, True


def encode_native_payload(value):
    units = value.encode("utf-16-be", errors="surrogatepass")
    safe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./"
    encoded = []
    for offset in range(0, len(units), 2):
        code = int.from_bytes(units[offset:offset + 2], "big") ^ 146
        char = chr(code)
        encoded.append(char if char in safe else f"%{code:02X}" if code < 256 else f"%u{code:04X}")
    return "".join(encoded)


def remove_game_author(component):
    """Clear only project-owned author values displayed by official games.

    Questions, cards, instructions, scoring, resources and external author
    credits retain their exact decoded values. The static HTML is untouched.
    """
    original = field(component, "htmlView")
    view = original
    for node in fragment(original).xpath(".//*[contains(@class,'DataGame')]"):
        payload = node.text_content()
        try:
            decoded, encoded = decode_native_payload(payload)
        except (ValueError, TypeError):
            continue
        def replacement(match):
            return match[1] + '""' if json.loads(match[2]) == AUTHORS else match[0]
        updated = AUTHOR_FIELD.sub(replacement, decoded)
        if updated == decoded:
            continue
        if encoded:
            if payload not in view:
                raise ValueError("The official encoded author payload could not be located")
            view = view.replace(payload, encode_native_payload(updated), 1)
        else:
            # Plain Relaciona data uses escaped text within its hidden div.
            # Matching only JSON author fields preserves every static byte.
            view = AUTHOR_FIELD.sub(replacement, view)
        expected = json.loads(decoded)
        def clear_author(value):
            if isinstance(value, dict):
                return {key: "" if key == "author" and item == AUTHORS else clear_author(item) for key, item in value.items()}
            if isinstance(value, list):
                return [clear_author(item) for item in value]
            return value
        updated_nodes = fragment(view).xpath(".//*[contains(@class,'DataGame')]")
        matching = next(n for n in updated_nodes if n.get("class") == node.get("class"))
        actual, _ = decode_native_payload(matching.text_content())
        if json.loads(actual) != clear_author(expected):
            raise ValueError("A native game's pedagogical data changed while removing its author credit")
    if view != original:
        set_field(component, "htmlView", view)


def correct_passport_license(component):
    """Correct only the legacy licence footer in the native passport."""
    if field(component, "odeIdeviceId") != PASSPORT_DEVICE:
        raise ValueError("The passport licence correction targets one reviewed iDevice only")
    original = field(component, "htmlView")
    nodes = fragment(original).xpath(".//div[contains(concat(' ',normalize-space(@class),' '),' listacotejo-DataGame ')]")
    if len(nodes) != 1:
        raise ValueError("Expected the single native passport checklist payload")
    payload = nodes[0].text_content()
    decoded, encoded = decode_native_payload(payload)
    before = json.loads(decoded)
    if not encoded or before.get("footer") != PASSPORT_OLD_FOOTER:
        raise ValueError("The pinned passport footer differs from the reviewed legacy value")
    # Preserve JSON formatting and every other field, including checklist
    # criteria and scoring settings, rather than reserializing the object.
    pattern = re.compile(r'("footer"\s*:\s*)("(?:[^"\\]|\\.)*")')
    matches = [match for match in pattern.finditer(decoded) if json.loads(match[2]) == PASSPORT_OLD_FOOTER]
    if len(matches) != 1:
        raise ValueError("Expected one exact legacy footer value in the passport")
    match = matches[0]
    updated = decoded[:match.start(2)] + json.dumps(PASSPORT_FOOTER, ensure_ascii=False) + decoded[match.end(2):]
    expected = deepcopy(before)
    expected["footer"] = PASSPORT_FOOTER
    if json.loads(updated) != expected or payload not in original:
        raise ValueError("The passport changed beyond its reviewed licence footer")
    set_field(component, "htmlView", original.replace(payload, encode_native_payload(updated), 1))


def node_remove(node):
    if node.getparent() is not None:
        node.drop_tree()


def clean_markup(markup, *, allow_authors=False, allow_versions=False):
    """Clean readable text and links without rewriting asset filenames or code."""
    doc = fragment(markup)
    if not allow_authors:
        for node in list(doc.xpath(".//p")):
            text = " ".join(node.text_content().split())
            if (text.startswith(("Autoría:", "Autoría del recurso:", "Autoría del OA:", "Autoría del Objeto de Aprendizaje:"))
                    and any(name in text for name in ("Jesica", "Gloria Elsa", "Cristian García"))):
                node_remove(node)
    for element in doc.iter():
        for attribute in ("text", "tail"):
            value = getattr(element, attribute)
            if not value:
                continue
            value = plural_text(value)
            if not allow_authors:
                replacements = {
                    "Escucha a Jesica Fortes Regalado": "Escucha el cuento",
                    "escucha a Jesica Fortes Regalado": "escucha la narración",
                    "narración de Jesica Fortes Regalado": "narración grabada",
                    "voz de Jesica Fortes Regalado": "voz grabada",
                    "Narración de los ocho cuentos: Jesica Fortes Regalado.": "Narraciones de los ocho cuentos aportadas para el recurso.",
                    "Narración: Jesica Fortes Regalado.": "",
                    "Jesica Fortes Regalado": "la narradora", "Gloria Elsa González Martín": "el equipo del proyecto",
                    "Cristian García Santana": "el equipo del proyecto", "Voz de Jesica": "Voz sola",
                    "narración de Jesica": "narración grabada", "narraciones de Jesica": "narraciones grabadas",
                    "Jesica": "la narradora",
                }
                for old, new in replacements.items():
                    value = value.replace(old, new)
            if not allow_versions:
                # Application releases are editorial metadata, unlike CC 4.0,
                # historical publication years and bibliographic edition dates.
                value = re.sub(r"\b(?:web|REA|ELPX|edición|revisión)\s+(?:actual\s+)?v?\d+\.\d+(?:\.\d+)?", "recurso", value, flags=re.I)
                value = re.sub(r"\b4\.[1-9]\d*\.\d+\b", "actual", value)
            setattr(element, attribute, value)
        for key in ("aria-label", "title", "alt"):
            if element.get(key):
                label = plural_text(element.get(key))
                if not allow_authors:
                    label = label.replace(", voz de Jesica Fortes Regalado", "").replace("Jesica Fortes Regalado", "la narradora")
                element.set(key, label)
    return inner(doc)


def collect_story_sources(texts):
    collected = []
    for (slug, island), sid, rid in zip(ISLANDS, STORY_IDS, RESEARCH_IDS, strict=True):
        story = fragment(texts[sid])
        evidence = []
        for node in list(story.xpath(".//section[contains(concat(' ', normalize-space(@class), ' '), ' source-trace ')]")):
            evidence.append(html.tostring(node, encoding="unicode"))
            node_remove(node)
        for heading in list(story.xpath(".//h3")):
            if "Cómo se fundamenta" not in heading.text_content():
                continue
            sibling = heading.getnext()
            evidence.append(html.tostring(heading, encoding="unicode"))
            node_remove(heading)
            while sibling is not None and sibling.tag == "p":
                following = sibling.getnext()
                if not sibling.xpath(".//a[contains(@href,'mitomapa/index.html') or @href='exe-node:" + EXTRA + "']"):
                    evidence.append(html.tostring(sibling, encoding="unicode"))
                node_remove(sibling)
                sibling = following
        figure_notes = []
        for caption in story.xpath(".//figcaption"):
            figure_notes.append(html.tostring(caption, encoding="unicode"))
            replace_content(caption, "Ilustración contemporánea recreada con IA; no constituye una reconstrucción histórica.")
        research = fragment(texts[rid])
        references = []
        for listing in list(research.xpath(".//ul[.//a[starts-with(@href,'http')]]")):
            references.append(html.tostring(listing, encoding="unicode"))
            replacement = fragment('<p>' + local_link(SOURCES, "Consultar las fuentes de investigación de " + island, "fuentes-" + slug) + '.</p>')[0]
            listing.addprevious(replacement)
            node_remove(listing)
        # Web-only practices belong to the optional external resource, not to
        # the native story. Its transcript and native activities remain intact.
        for paragraph in list(story.xpath(".//p")):
            if paragraph.xpath(".//a[contains(@href,'mitomapa/index.html') or @href='exe-node:" + EXTRA + "']"):
                node_remove(paragraph)
        story.append(fragment('<p>' + local_link(SOURCES, "Consultar las fuentes y las decisiones de adaptación de " + island, "fuentes-" + slug) + '.</p>')[0])
        texts[sid] = inner(story)
        texts[rid] = inner(research)
        note = '<h4>Procedencia de la ilustración</h4>' + "".join(figure_notes)
        collected.append(box(island, "".join(evidence + references) + note, "fuentes-" + slug))
    return "".join(collected)


def source_sections(original, story_sources, curricular):
    doc = fragment(original)
    sections = {"Bibliografía y consultas": [], "Imágenes y pintaderas": [], "Audio y herramientas": [], "Referencias complementarias": []}
    group = "Bibliografía y consultas"
    for node in doc:
        title = node.text_content().strip()
        if node.tag in {"h2", "h3"}:
            if title == "Créditos de las imágenes":
                group = "Imágenes y pintaderas"
                continue
            if title == "Créditos de las narraciones":
                group = "Audio y herramientas"
                continue
            if title.startswith("Referencias identificadas"):
                group = "Referencias complementarias"
                continue
            if title == "Fuentes de referencia":
                continue
        sections[group].append(deepcopy(node))
    legislation = []
    for nodes in sections.values():
        for listing in list(nodes):
            if listing.tag != "ul":
                continue
            for item in list(listing):
                urls = " ".join(item.xpath(".//a/@href"))
                if re.search(r"/boc/|/rubricas/|rubricas-primaria", urls):
                    legislation.append(html.tostring(item, encoding="unicode"))
                    listing.remove(item)
    bibliography = "".join(html.tostring(n, encoding="unicode") for n in sections["Bibliografía y consultas"])
    images = "".join(html.tostring(n, encoding="unicode") for n in sections["Imágenes y pintaderas"])
    audio = "".join(html.tostring(n, encoding="unicode") for n in sections["Audio y herramientas"])
    complement = "".join(html.tostring(n, encoding="unicode") for n in sections["Referencias complementarias"])
    return (
        '<h2>Fuentes y referencias</h2><p>Las fuentes permiten contrastar los cuentos con la documentación. '
        'Las referencias se agrupan aquí para distinguir la información documentada de la recreación literaria. '
        'Los documentos externos conservan sus condiciones de reutilización.</p>'
        + '<h3 id="fuentes-cuentos">Fuentes y adaptación de cada cuento</h3>' + story_sources
        + box("Bibliografía y consultas generales", bibliography + complement, "fuentes-bibliografia")
        + box("Normativa y documentos curriculares", "<ul>" + "".join(legislation) + "</ul>" + curricular, "fuentes-normativa")
        + box("Mapa, imágenes y pintaderas: procedencia y condiciones de uso", images, "fuentes-imagenes")
        + box("Narraciones, ambiente y herramientas de audio", audio, "fuentes-audio")
    )


def adapt_native_guidance(texts):
    replacements = {
        "20260823155836TPASSI": (
            '<h2>Cómo usar el pasaporte</h2><p>Acuerden con su docente las islas y las tareas de su recorrido. '
            'No es necesario completar todas las actividades ni reunir las ocho pintaderas.</p>'
            '<ol><li>Elijan una isla y lean o escuchen el cuento.</li><li>Realicen los retos y el taller acordados; '
            'pueden utilizar apoyos y volver al texto.</li><li>Conversen sobre lo aprendido y revisen su creación.</li>'
            '<li>Marquen manualmente la isla en el pasaporte tras revisar las tareas con su docente.</li></ol>'
            '<p>El informe reúne los juegos nativos disponibles en el recurso. Las actividades que no formen parte '
            'de su recorrido pueden quedar pendientes; este informe no sustituye la revisión de sus producciones.</p>'
        ),
        "20260917TOPINION37": (
            '<h2>Tu opinión ayuda a mejorar</h2><p>Después de una o varias islas, puedes compartir tu opinión '
            'con tu docente de manera oral o en el cuaderno. No modifica el pasaporte ni una calificación.</p>'
            '<ol><li>¿Qué actividad te ayudó a aprender o disfrutar?</li><li>¿Qué parte necesitó una explicación '
            'o un apoyo adicional?</li><li>¿Qué cambiarías y cómo lo harías?</li></ol>'
            '<p>No escribas nombres ni otros datos personales. Puedes aportar solo un comentario. '
            'El profesorado puede recoger las sugerencias de forma colectiva.</p>'
        ),
        "20260823155837TGUID3": (
            '<h2>Uso y reutilización del recurso</h2><p>Los cuentos, las actividades nativas, los reproductores y '
            'las orientaciones se pueden modificar en eXeLearning. Los juegos mantienen sus ajustes y el informe '
            'de progreso; el pasaporte se marca manualmente después de revisar las tareas acordadas.</p>'
            '<h3>Acceso y escucha</h3><p>Los textos, las imágenes, los juegos y las dieciséis pistas de narración '
            'están incluidos localmente. No hay reproducción automática: cada cuento ofrece voz sola y una '
            'alternativa con ambiente breve; se utiliza un solo reproductor a la vez. Los enlaces bibliográficos '
            'requieren conexión. Para trabajar sin Internet, se preparan copias accesibles de las fuentes elegidas.</p>'
            '<h3>Adaptación</h3><p>Antes de modificar el proyecto, se guarda una copia. Después se revisa una '
            'exportación y se comprueban los enlaces y las actividades. Los materiales propios se pueden adaptar '
            'y compartir bajo CC BY-SA 4.0, también con fines comerciales, con atribución, indicación de cambios '
            'y la misma licencia. Las fuentes externas conservan sus condiciones.</p>'
            '<p>Se utiliza el tema Flux de la plantilla oficial y la fuente Andika incluida localmente. '
            'Los recursos y bibliotecas de eXeLearning conservan sus avisos y licencias.</p>'
        ),
        "GBCTRECURSOS": (
            '<h2>Recursos para preparar el recorrido</h2><ul><li>Los ocho cuentos, con ilustración, texto y dos '
            'alternativas de escucha.</li><li>Los retos de comprensión, vocabulario y significado, elegidos según '
            'el grupo.</li><li>Las propuestas de investigación y creación de cada taller.</li><li>El cuaderno '
            'de ruta y la pauta cualitativa disponibles en la caja de materiales descargables.</li><li>Las '
            + local_link(SOURCES, "fuentes de consulta") + ', con procedencia de imágenes y audio.</li></ul>'
            '<p>Se necesita un navegador compatible y, si se elige escuchar, auriculares o altavoces. No se exige '
            'registro. Las producciones pueden ser orales, escritas, gráficas o representadas.</p>'
        ),
        "20261006TEXPLORER440": (
            '<h2>La web de MitoMapa: un recurso extra</h2><p>Si desean ampliar la experiencia, pueden visitar '
            'la web de MitoMapa canario. Ofrece otras formas de explorar las islas, pistas, secuencias, comparación '
            'de cuentos y el juego de nombres históricos.</p>'
            f'<p><a href="{PUBLIC_WEB}" target="_blank" rel="noopener noreferrer">Abrir la web de MitoMapa '
            'canario en una pestaña nueva</a>.</p><p>La web es un recurso independiente: requiere conexión y '
            'no está embebida ni incluida como aplicación dentro de este Objeto de Aprendizaje. Sus respuestas '
            'y su seguimiento se guardan por separado; no se sincronizan con las actividades de eXeLearning. '
            'Utilizarla es opcional y no condiciona el recorrido de este recurso.</p>'
        ),
    }
    texts.update(replacements)
    route_note = ('<p>La ruta se acuerda con el grupo. Revisar las tareas de dos islas puede completar un '
                  'itinerario corto sin recorrer las ocho. El pasaporte se marca manualmente después de esa '
                  'revisión; el informe de juegos y las producciones abiertas aportan evidencias diferentes.</p>')
    for iid in ("20260823155836TINTRO", "20260823155836TITINW", "20260823155837TGUID1", "GBCTACOMPANA"):
        doc = fragment(texts[iid])
        for paragraph in list(doc.xpath(".//p")):
            if "Ruta acordada y colección de pintaderas." in paragraph.text_content():
                paragraph.addprevious(fragment(route_note)[0])
                node_remove(paragraph)
        for paragraph in list(doc.xpath(".//p")):
            if paragraph.xpath(".//a[@href='exe-node:" + EXTRA + "']"):
                node_remove(paragraph)
        if iid == "20260823155837TGUID1":
            for paragraph in list(doc.xpath(".//p")):
                if paragraph.text_content().strip().startswith("Propuesta multinivel · edición"):
                    replace_content(paragraph, "Propuesta multinivel. El profesorado concreta el anclaje curricular, las tareas y los apoyos para su grupo; los ejemplos no fijan un nivel obligatorio.")
            for node in list(doc.xpath(".//li | .//p")):
                text = " ".join(node.text_content().split())
                if "Ajustes y seguimiento" in text and not node.xpath(".//li"):
                    if "Acuerda" in text or "Acuerda" in text:
                        replace_content(node, '<strong>Acuerden la ruta.</strong> Seleccionen las islas y las tareas que se van a trabajar, así como las fuentes, los apoyos y la forma de compartir las producciones.')
                    elif "Prepara el Taller" in text:
                        replace_content(node, '<strong>Prepara el Taller.</strong> Elige las actividades y la producción que se van a realizar. Las demás propuestas quedan disponibles como ampliación opcional.')
                    else:
                        replace_content(node, 'Acuerden las islas y las tareas; revisen las producciones y marquen manualmente el pasaporte. El informe de juegos es una ayuda independiente de esa revisión.')
                elif "En Inicio puedes" in text or "Selecciona una propuesta inicial con los botones" in text:
                    replace_content(node, '<strong>Ajusta la lectura y los apoyos.</strong> Consulta los apoyos del cuento y selecciona las tareas adecuadas al grupo. La propuesta es multinivel y se puede adaptar durante la actividad.')
                elif "En Inicio → Etapa y ajustes de lectura" in text:
                    replace_content(node, '<strong>Preparar la lectura.</strong> Selecciona las actividades, la forma de leer o escuchar y los apoyos que necesita el grupo. Revisa los apoyos del cuento y acuerda cómo responder.')
                elif "quién maneja la web" in text:
                    replace_content(node, '<strong>Acuerda una tarea y el agrupamiento.</strong> Puedes leer con todo el grupo y continuar en parejas, equipos o de forma individual. En parejas, pueden alternar quién maneja el recurso y quién explica lo que observa.')
                elif "Ambiente suave" in text and "Escucha con el grupo" in text:
                    replace_content(node, '<strong>Escucha con el grupo.</strong> Cada cuento ofrece voz sola y una alternativa con ambiente breve. Se puede pausar para conversar; utiliza una sola pista a la vez y mantén visible el texto.')
                elif any(marker in text for marker in ("Nombres de las islas:", "Ordena el cuento:", "Compara dos cuentos:", "Mapa y pistas:")):
                    node_remove(node)
                elif "El juego de nombres es una práctica" in text:
                    node_remove(node)
        texts[iid] = inner(doc)
    # Native narration guidance remains useful; the web-player controls do not.
    doc = fragment(texts["20260823155837TLOC1D"])
    for paragraph in doc.xpath(".//p"):
        if "En el Explorador puedes" in paragraph.text_content():
            replace_content(paragraph, "Mantén visible el texto, permite pausas para conversar y utiliza una sola pista a la vez. Cada cuento contiene voz sola y una alternativa con ambiente breve.")
    texts["20260823155837TLOC1D"] = inner(doc)


def rewrite_local_html_links(markup):
    doc = fragment(markup)
    for node in doc.xpath(".//*[@href] | .//*[@src]"):
        for attribute in ("href", "src"):
            target = node.get(attribute, "")
            if not target.startswith(APP) or not urlsplit(target).path.endswith(".html"):
                continue
            if attribute == "src":
                node_remove(node)
                continue
            name = target.removeprefix(APP).split("#", 1)[0]
            destination = SOURCES if any(part in name for part in ("FUENTES", "AUDIO", "LICENCIA")) else TEACHER
            node.set(attribute, "exe-node:" + destination)
    return inner(doc)


def render_content(markup, path, paths, aliases):
    prefix = "../" if path.startswith("html/") else ""
    markup = markup.replace(CONTEXT + "/", prefix)
    def link(match):
        pid = aliases.get(match[1], match[1])
        if pid not in paths:
            raise ValueError(f"Unresolved native page link: {pid}")
        return posixpath.relpath(paths[pid], posixpath.dirname(path) or ".") + (match[2] or "")
    return re.sub(r"exe-node:([A-Za-z0-9]+)(#[^\"'<>\s]*)?", link, markup)


def render_exports(files, tree, original_search, templates, block_templates, aliases):
    pages = tree.findall(".//o:odeNavStructure", NS)
    paths = {field(page, "odePageId"): original_search[field(page, "odePageId")]["fileUrl"] for page in pages}
    old_extra = paths[EXTRA]
    paths[EXTRA] = "html/la-web-un-recurso-extra.html"
    search = {}
    by_pid = {field(p, "odePageId"): p for p in pages}
    children = {}
    for page in pages:
        children.setdefault(field(page, "odeParentPageId"), []).append(page)
    def nav_list(parent, pid, path):
        listing = etree.Element("ul")
        for target in children.get(parent, []):
            tid = field(target, "odePageId")
            item = etree.SubElement(listing, "li")
            link = etree.SubElement(item, "a", href=posixpath.relpath(paths[tid], posixpath.dirname(path) or "."))
            link.text = field(target, "pageName")
            classes = ["daddy" if children.get(tid) else "no-ch"]
            if tid == pid:
                item.set("class", "active")
                classes.insert(0, "active")
            link.set("class", " ".join(classes))
            if children.get(tid):
                sub = nav_list(tid, pid, path)
                ancestor = pid
                while ancestor and ancestor != tid:
                    ancestor = field(by_pid[ancestor], "odeParentPageId")
                sub.set("class", "current-section" if ancestor == tid else "other-section")
                item.append(sub)
        return listing
    for position, page in enumerate(pages):
        pid = field(page, "odePageId")
        path = paths[pid]
        document = deepcopy(templates[pid])
        main = document.xpath("//main")[0]
        main.set("id", pid)
        body = document.xpath("//div[starts-with(@id,'page-content-')]")[0]
        body.set("id", "page-content-" + pid)
        replace_content(body, "")
        blocks = page.findall("o:odePagStructures/o:odePagStructure", NS)
        info = dict(original_search[pid])
        info.update(name=field(page, "pageName"), isIndex=position == 0,
                    fileName=path.rsplit("/", 1)[-1], fileUrl=path,
                    prePageId=field(pages[position - 1], "odePageId") if position else None,
                    nextPageId=field(pages[position + 1], "odePageId") if position + 1 < len(pages) else None,
                    blocks={})
        for block in blocks:
            bid = field(block, "odeBlockId")
            article = deepcopy(block_templates[bid])
            title = article.xpath(".//*[contains(concat(' ',normalize-space(@class),' '),' box-title ')]")[0]
            title.text = field(block, "blockName")
            minimized = block.findtext(".//o:odePagStructureProperty[o:key='minimized']/o:value", namespaces=NS) == "true"
            teacher_only = block.findtext(".//o:odePagStructureProperty[o:key='teacherOnly']/o:value", namespaces=NS) == "true"
            classes = ["box"] + (["minimized"] if minimized else []) + (["teacher-only"] if teacher_only else [])
            article.set("class", " ".join(classes))
            box_content = article.xpath("./div[@class='box-content']")[0]
            if minimized:
                box_content.set("style", "display:none")
            else:
                box_content.attrib.pop("style", None)
            toggle = article.xpath(".//button[contains(@class,'box-toggle')]")
            if toggle:
                toggle[0].set("class", "box-toggle box-toggle-off" if minimized else "box-toggle box-toggle-on")
            block_info = {"name": field(block, "blockName"), "order": int(field(block, "odePagStructureOrder")), "idevices": {}}
            for component in block.findall("o:odeComponents/o:odeComponent", NS):
                iid = field(component, "odeIdeviceId")
                target = article.xpath(f'.//*[@id="{iid}"]')[0]
                view = render_content(field(component, "htmlView"), path, paths, aliases)
                replace_content(target, view)
                if "textTextarea" in target.get("data-idevice-json-data", ""):
                    target.set("data-idevice-json-data", field(component, "jsonProperties"))
                block_info["idevices"][iid] = {"order": int(field(component, "odeComponentsOrder")), "htmlView": view, "jsonProperties": field(component, "jsonProperties")}
            info["blocks"][bid] = block_info
            body.append(article)
        # Merged boxes may use a native iDevice type not loaded by the former
        # guide page. Copy its original official declarations unchanged.
        head = document.xpath("//head")[0]
        known = {(n.tag, n.get("src") or n.get("href")) for n in head}
        kinds = {field(c, "odeIdeviceTypeName") for c in page.findall(".//o:odeComponent", NS)}
        for template in templates.values():
            for asset in template.xpath("//head/script[@src] | //head/link[@href]"):
                ref = asset.get("src") or asset.get("href")
                if not ref or not any("idevices/" + kind + "/" in ref for kind in kinds):
                    continue
                key = asset.tag, ref
                if key not in known:
                    head.append(deepcopy(asset)); known.add(key)
        for node in document.xpath("//p[contains(concat(' ',normalize-space(@class),' '),' package-subtitle ')]"):
            node_remove(node)
        document.xpath("//h1[@class='page-title']")[0].text = field(page, "pageName")
        document.xpath("//title")[0].text = field(page, "pageName") + " | MitoMapa canario"
        nav = document.xpath("//nav[@id='siteNav']")[0]
        replace_content(nav, "")
        nav.append(nav_list("", pid, path))
        for node in document.xpath("//*[contains(concat(' ',normalize-space(@class),' '),' page-counter-current-page ')]"):
            node.text = str(position + 1)
        for node in document.xpath("//*[contains(concat(' ',normalize-space(@class),' '),' page-counter-total ')]"):
            node.text = str(len(pages))
        buttons = document.xpath("//div[@class='nav-buttons']")[0]
        replace_content(buttons, "")
        for offset, direction, label in ((-1, "left", "Anterior"), (1, "right", "Siguiente")):
            index = position + offset
            if 0 <= index < len(pages):
                target = field(pages[index], "odePageId")
                link = etree.SubElement(buttons, "a", href=posixpath.relpath(paths[target], posixpath.dirname(path) or "."), title=label, attrib={"class": "nav-button nav-button-" + direction})
                etree.SubElement(link, "span").text = label
        for node in document.xpath("//div[@id='siteUserFooter']"):
            replace_content(node, "")
        # A cover needs no second layer of package/title text above its clean
        # title, authors, decorative pintaderas and licence.
        if pid == COVER:
            for node in document.xpath("//div[@class='package-header'] | //div[@class='page-header']"):
                node_remove(node)
        files[path] = html.tostring(document, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")
        search[pid] = info
    retained = set(paths.values())
    for pid in TEACHER_CHILDREN:
        files.pop(original_search[pid]["fileUrl"], None)
    if old_extra not in retained:
        files.pop(old_extra, None)
    files["search_index.js"] = b"window.exeSearchData = " + json.dumps(search, ensure_ascii=False, separators=(",", ":")).encode() + b";\n"


def clean_attached_documents(files):
    for name in list(files):
        if not name.startswith("content/resources/") or name.startswith("content/resources/mitomapa/") or not name.endswith(".html"):
            continue
        if not any(word in Path(name).name.lower() for word in ("cuaderno", "rubrica")):
            continue
        doc = html.fromstring(files[name])
        for paragraph in list(doc.xpath(".//p")):
            text = paragraph.text_content()
            if any(author in text for author in ("Jesica Fortes", "Gloria Elsa", "Cristian García")):
                node_remove(paragraph)
        for footer in doc.xpath(".//footer"):
            if any(author in footer.text_content() for author in ("Jesica Fortes", "Gloria Elsa", "Cristian García")):
                replace_content(footer, '<p>Materiales propios: <a href="' + LICENSE_URL + '" rel="license">CC BY-SA 4.0</a>.</p>')
        for node in doc.iter():
            for attribute in ("text", "tail"):
                value = getattr(node, attribute)
                if value and node.tag not in {"script", "style"}:
                    value = plural_text(value)
                    value = re.sub(r"\b(?:web|REA|ELPX|versión|edición)\s+v?\d+\.\d+(?:\.\d+)?", "recurso", value, flags=re.I)
                    setattr(node, attribute, value)
        files[name] = html.tostring(doc, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")


ATTACHMENT_EDITORIAL_LABELS = {
    "Cuaderno_de_ruta_MitoMapa_4_0.html": (
        "Mi cuaderno de ruta", "Planifica las tareas y registra lectura, fuentes, creación, revisión y cierre. HTML para imprimir o adaptar en un editor de textos."),
    "Rubrica_lectura_MitoMapa_4_0.html": (
        "Pauta cualitativa de lectura e impresión", "Criterios y descriptores cualitativos con espacio para evidencias, avances y un siguiente paso; sin puntuaciones."),
    "Rubrica_MitoMapa_4_0.csv": (
        "Pauta cualitativa editable", "CSV con criterios y descriptores cualitativos para seleccionar y adaptar al trabajo acordado; sin puntuaciones."),
}


def update_attachment(component, files):
    """Only the attachment labels and measured HTML byte sizes are revised."""
    data = json.loads(field(component, "jsonProperties"))
    original_view = field(component, "htmlView")
    view = original_view
    document = fragment(original_view)
    items = document.xpath(".//li[contains(@class,'fileAttachment-item')]")
    for entry, item in zip(data["attachments"], items, strict=True):
        name = entry["filename"]
        title, description = ATTACHMENT_EDITORIAL_LABELS[name]
        old_title, old_description = entry["title"], entry["description"]
        entry.update(title=title, description=description, size=len(files["content/resources/" + name]))
        size = f'{entry["size"] / 1024:.1f} KB'
        old_meta = item.xpath(".//span[@class='fileAttachment-meta']")[0].text
        for before, after in ((old_title, title), (old_description, description), (old_meta, name + " · " + size)):
            if before != after:
                view = view.replace(escape(before, quote=False), escape(after, quote=False))
    set_field(component, "jsonProperties", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    # Preserve comments and native wrapper structure; only matching text nodes
    # differ from the original official attachment markup.
    set_field(component, "htmlView", view)


def apply_editorial(files, root, version):
    """Mutate an unpacked native 4.7.1 project into its clean publication form."""
    parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True)
    tree = etree.fromstring(files["content.xml"], parser)
    source = files["search_index.js"].decode()
    original_search = json.loads(source[source.index("{"):].rstrip(";\n"))
    pages = {field(p, "odePageId"): p for p in tree.findall(".//o:odeNavStructure", NS)}
    components = {field(c, "odeIdeviceId"): c for c in tree.findall(".//o:odeComponent", NS)}
    texts = {iid: text_of(c) for iid, c in components.items() if field(c, "odeIdeviceTypeName") == "text"}
    templates = {pid: html.fromstring(files[info["fileUrl"]]) for pid, info in original_search.items()}
    block_templates = {article.get("id"): deepcopy(article) for document in templates.values() for article in document.xpath("//article[@id]")}
    original_ids = set(components)
    story_sources = collect_story_sources(texts)
    curricular = []
    for iid, markup in list(texts.items()):
        if iid in {"GBCTFUENTES", "20260929TNOMBRES39", "20260823155837TCRED0"}:
            continue
        doc = fragment(markup)
        for paragraph in list(doc.xpath(".//p")):
            links = paragraph.xpath(".//a[starts-with(@href,'http')]")
            if links and any(re.search(r"/boc/|/rubricas/|rubricas-primaria", link.get("href", "")) for link in links):
                curricular.append(html.tostring(paragraph, encoding="unicode"))
                replace_content(paragraph, 'Las referencias normativas y los documentos de consulta se reúnen en ' + local_link(SOURCES, "Fuentes y referencias", "fuentes-normativa") + '.')
        texts[iid] = inner(doc)
    texts["GBCTFUENTES"] = source_sections(texts["GBCTFUENTES"], story_sources, "".join(curricular))
    # The source table is historical material, not another teaching page. Its
    # native box moves to Sources and adopts the current cautious selection.
    names_doc = html.fromstring((root / "FUENTES_CUENTOS.html").read_bytes())
    names = names_doc.xpath("//*[@id='nombres-islas']")
    if names:
        names = deepcopy(names[0])
        for paragraph in list(names.xpath(".//p")):
            if paragraph.xpath(".//a[contains(@href,'index.html')]"):
                node_remove(paragraph)
        texts["20260929TNOMBRES39"] = html.tostring(names, encoding="unicode")
    adapt_native_guidance(texts)
    # The clean cover contains no source list, curricular level or edition.
    intro = fragment(texts["20260823155836TINTRO"])
    badges = intro.xpath(".//a[starts-with(@href,'exe-node:20260823155836ISL')]/img/@src")[:8]
    if len(badges) != 8:
        raise ValueError("The cover requires the eight existing pintaderas")
    rows = []
    for start in (0, 4):
        rows.append('<div style="display:flex;justify-content:center;gap:1rem;margin:.8rem 0">' + "".join(
            f'<span style="flex:1 1 0;max-width:100px;min-width:0;text-align:center"><img src="{escape(src, quote=True)}" alt="" role="presentation" width="80" height="80" style="max-width:100%;height:auto;object-fit:contain"></span>'
            for src in badges[start:start + 4]) + '</div>')
    texts["GBCTPORTADA"] = (
        '<section aria-label="Portada de MitoMapa canario" style="max-width:760px;margin:auto;padding:1.5rem;text-align:center">'
        '<h1 style="font-family:Arial,Helvetica,sans-serif;font-size:18pt;line-height:1.25;margin:.5rem 0 1.5rem">MitoMapa canario<br><span style="font-size:14pt">Ocho islas, ocho pintaderas</span></h1>'
        + rows[0]
        + f'<img src="{CONTEXT}/content/resources/mapa_canarias.webp" alt="Mapa de las ocho islas de Canarias" width="3000" height="1514" style="display:block;width:100%;max-width:100%;height:auto;object-fit:contain;margin:1rem auto">'
        + rows[1] + f'<p style="margin:1.7rem 0 .5rem"><strong>Autoría</strong><br>{AUTHORS.replace("; ", "<br>")}</p>'
        '<p>Narración: Jesica Fortes Regalado.</p>'
        f'<p><a href="{LICENSE_URL}" rel="license"><img src="{APP}assets/images/cc-by-sa-4.0.svg" width="88" height="31" alt="CC BY-SA 4.0"></a><br>'
        f'<a href="{LICENSE_URL}" rel="license">CC BY-SA 4.0</a> · Materiales propios</p></section>'
    )
    texts["GBCTJUSTIFICA"] = (
        '<h2>Un viaje para leer, descubrir y crear</h2><p>En este Objeto de Aprendizaje descubrirán cuentos '
        'ambientados en las ocho islas de Canarias. Podrán leerlos o escucharlos, conversar sobre sus personajes '
        'y elegir por qué isla comenzar. No tendrán que recorrerlas todas ni seguir un orden único.</p>'
        '<p>Al explorar los relatos, distinguirán lo que cuenta una recreación literaria de lo que permiten '
        'conocer las fuentes históricas, la arqueología y la tradición oral. Compararán versiones, buscarán '
        'información con ayuda y reconocerán también aquello que todavía no se puede afirmar con seguridad.</p>'
        '<p>Después compartirán lo aprendido mediante una creación oral, escrita, gráfica o representada para '
        'un museo de cuentos. Acordarán con su docente las tareas y los apoyos que necesiten; podrán volver '
        'al texto, pedir ayuda y revisar sus ideas. La lectura y la creación les permitirán conocer, valorar '
        'y cuidar el patrimonio cultural y natural de Canarias.</p>'
    )
    texts["20260823155837TCRED0"] = (
        '<h2>Autoría y licencia</h2><p><strong>MitoMapa canario: ocho islas, ocho pintaderas.</strong></p>'
        f'<p><strong>Autoría:</strong> {AUTHORS}.<br><strong>Narración de los ocho cuentos:</strong> Jesica Fortes Regalado.</p>'
        '<p>Los cuentos, las preguntas y las propuestas son textos originales creados para este recurso a partir '
        'de mitos, leyendas y fuentes de consulta. No reproducen obras literarias contemporáneas. Las pintaderas '
        'son símbolos de la expedición y no representan una atribución arqueológica a cada isla.</p>'
        f'<p><a href="{LICENSE_URL}" rel="license"><img src="{APP}assets/images/cc-by-sa-4.0.svg" width="88" height="31" alt="CC BY-SA 4.0"></a> '
        f'<a href="{LICENSE_URL}" rel="license">Creative Commons Reconocimiento-CompartirIgual 4.0 Internacional</a>. '
        'Los materiales propios se pueden copiar, adaptar y compartir, también con fines comerciales, con atribución, '
        'indicación de cambios y la misma licencia en las adaptaciones. La licencia se aplica sobre los derechos '
        'propios que correspondan; no atribuye derechos sobre materiales de terceros ni sobre creaciones no protegidas.</p>'
        '<p>El mapa, las fuentes enlazadas, los distintivos y las bibliotecas conservan sus condiciones originales. '
        + local_link(SOURCES, 'Su procedencia, documentación y condiciones se reúnen en Fuentes y referencias') + '.</p>'
        '<p><strong>Sugerencias:</strong> <a href="mailto:sugerencias.mitomapacanario@gmail.com">sugerencias.mitomapacanario@gmail.com</a>.</p>'
    )
    thanks = (
        "Se agradece la colaboración de las personas consultadas sobre aspectos históricos, técnicos y didácticos "
        "durante la elaboración y revisión de MitoMapa canario. Sus observaciones y sugerencias han contribuido "
        "a revisar y mejorar los contenidos, el funcionamiento y las propuestas de aprendizaje del recurso."
    )
    texts["20260930IHISTORIA40"] = '<h2>Agradecimientos</h2><p>' + escape(thanks) + '</p>'
    texts["20260929THISTORIAL39"] = (
        f'<h2>Versión y trazabilidad</h2><p><strong>Objeto de Aprendizaje {escape(version["rea_exelearning_version"])}.</strong> '
        f'Revisión editorial del {escape(version["prepared_at"])}. Preparado para eXeLearning {escape(version["exelearning_runtime_version"])}.</p>'
        '<p>Esta entrega simplifica la portada y la navegación, reúne las fuentes y los créditos, agrupa las '
        'orientaciones docentes en cajas desplegables y separa la web como complemento externo. Conserva los '
        'cuentos, las actividades y los medios de la entrega anterior. Las grabaciones, las ocho escenas y '
        'las pintaderas se mantienen sin alteración.</p>'
        '<p>Las ediciones anteriores se conservan como antecedentes de trazabilidad. El proyecto pasó por las '
        'revisiones 4.4.0, 4.5.1, 4.6.0, 4.7.0 y 4.7.1 antes de esta revisión editorial. Las fechas de las '
        'publicaciones citadas corresponden a sus propias fuentes.</p>'
        '<p><strong>Comprobación:</strong> la integridad del paquete, las referencias locales y la coherencia '
        'entre contenido editable, búsqueda y exportación se verifican técnicamente. Estas comprobaciones '
        'no acreditan eficacia educativa ni una certificación de accesibilidad. La primera aplicación con '
        'alumnado sigue pendiente; conviene registrar los apoyos necesarios y las dificultades observadas.</p>'
        '<p>El progreso se guarda según los mecanismos del navegador y de los juegos. Un cambio de ubicación, '
        'navegador o entrega puede afectar a su conservación. Preparar un archivo no acredita por sí solo su '
        'publicación institucional.</p>'
    )
    # Clean all 63 editable texts, including their preview and later export.
    for iid, markup in texts.items():
        markup = rewrite_local_html_links(markup)
        markup = clean_markup(markup, allow_authors=iid in {"GBCTPORTADA", "20260823155837TCRED0"}, allow_versions=iid == "20260929THISTORIAL39")
        markup = re.sub(r"exe-node:(" + "|".join(TEACHER_CHILDREN) + r")(?=[#\"'])", "exe-node:" + TEACHER, markup)
        set_text(components[iid], markup)
    for component in components.values():
        if field(component, "odeIdeviceTypeName") not in {"text", "file-attachment", "download-source-file", "progress-report", "checklist"}:
            remove_game_author(component)
    correct_passport_license(components[PASSPORT_DEVICE])
    # Merge teacher pages without changing component identities or payloads.
    teacher_blocks = pages[TEACHER].find("o:odePagStructures", NS)
    for pid in TEACHER_CHILDREN:
        for block in list(pages[pid].find("o:odePagStructures", NS)):
            teacher_blocks.append(block)
        pages[pid].getparent().remove(pages[pid])
    source_blocks = pages[SOURCES].find("o:odePagStructures", NS)
    names_block = components["20260929TNOMBRES39"].getparent().getparent()
    source_blocks.append(names_block)
    for page in (pages[TEACHER], pages[SOURCES]):
        for index, block in enumerate(page.findall("o:odePagStructures/o:odePagStructure", NS)):
            set_field(block, "odePageId", field(page, "odePageId"))
            set_field(block, "odePagStructureOrder", str(index))
            for component in block.findall(".//o:odeComponent", NS):
                set_field(component, "odePageId", field(page, "odePageId"))
            set_property(block, "odePagStructureProperty", "allowToggle", "true")
            set_property(block, "odePagStructureProperty", "minimized", "false" if field(block, "odeBlockId") == "GBCBFUENTES" else "true")
            # These clearly separated pages need no hidden ?exe-teacher=1
            # runtime mode: their boxes remain available to every reader.
            set_property(block, "odePagStructureProperty", "teacherOnly", "false")
    block_names = {"20260823155837BGUID3": "Uso y reutilización", "20260823155837BCREDR": "Autoría y licencia", "20260929BHISTORIAL39": "Versión y trazabilidad", "20260930BHISTORIA40": "Agradecimientos", "20261006BEXPLORER440": "La web: recurso extra"}
    for block in tree.findall(".//o:odePagStructure", NS):
        bid = field(block, "odeBlockId")
        if bid in block_names:
            set_field(block, "blockName", block_names[bid])
    # Place acknowledgements before the sole version box in the final page.
    credit_blocks = pages[CREDITS].find("o:odePagStructures", NS)
    by_block = {field(block, "odeBlockId"): block for block in credit_blocks}
    for index, bid in enumerate(("20260823155837BCREDR", "20260930BHISTORIA40", "20260930BDESCARGA40", "20260929BHISTORIAL39")):
        block = by_block[bid]
        credit_blocks.remove(block); credit_blocks.append(block)
        set_field(block, "odePagStructureOrder", str(index))
        set_property(block, "odePagStructureProperty", "teacherOnly", "false")
    # Keep the complete route structure; reduce only duplicated guide pages.
    page_titles = {HOME: "Comenzamos", STORIES: "Los cuentos: elijan su isla", TEACHER: "Orientaciones docentes", SOURCES: "Fuentes y referencias", CREDITS: "Autoría, agradecimientos y licencia", EXTRA: "La web: recurso extra"}
    for pid, title in page_titles.items():
        set_field(pages[pid], "pageName", title)
        for key in ("titlePage", "titleNode"):
            set_property(pages[pid], "odeNavStructureProperty", key, title)
    set_field(pages[JUSTIFICATION], "odeParentPageId", HOME)
    set_field(pages[JUSTIFICATION], "odeNavStructureOrder", "0")
    set_field(pages[PASSPORT], "odeNavStructureOrder", "1")
    set_field(pages[CLOSING], "odeParentPageId", "")
    set_field(pages[EXTRA], "odeParentPageId", "")
    top = [COVER, HOME, STORIES, CLOSING, TEACHER, SOURCES, CREDITS, EXTRA]
    for index, pid in enumerate(top):
        set_field(pages[pid], "odeNavStructureOrder", str(index))
    retained_pages = {field(p, "odePageId"): p for p in tree.findall(".//o:odeNavStructure", NS)}
    ordered = []
    def visit(pid):
        ordered.append(retained_pages[pid])
        children = [p for p in retained_pages.values() if field(p, "odeParentPageId") == pid]
        for child in sorted(children, key=lambda p: int(field(p, "odeNavStructureOrder"))):
            visit(field(child, "odePageId"))
    for pid in top:
        visit(pid)
    container = ordered[0].getparent()
    for page in ordered:
        container.remove(page); container.append(page)
    set_property(tree, "odeProperty", "footer", "")
    set_property(tree, "odeProperty", "pp_subtitle", "")
    # The saved editor thumbnail still depicts the former cover. Leaving it
    # empty lets eXe generate a current preview when the project is saved.
    set_property(tree, "odeProperty", "pp_screenshot", "")
    set_property(tree, "odeProperty", "pp_license", "creative commons: attribution - share alike 4.0")
    set_property(tree, "odeProperty", "pp_licenseUrl", "https://creativecommons.org/licenses/by-sa/4.0/")
    set_property(tree, "odeProperty", "pp_description", "Objeto de Aprendizaje multinivel con ocho cuentos de Canarias, actividades de lectura, investigación y creación, narraciones y orientaciones docentes. La web se ofrece como complemento externo independiente.")
    modified = int(datetime.fromisoformat(version["prepared_at"]).replace(tzinfo=timezone.utc).timestamp() * 1000)
    set_property(tree, "odeProperty", "pp_modified", str(modified))
    set_property(tree, "odeResource", "odeVersionId", version["prepared_at"].replace("-", "") + "MITOMAPA" + version["rea_exelearning_version"].replace(".", ""))
    if set(field(c, "odeIdeviceId") for c in tree.findall(".//o:odeComponent", NS)) != original_ids:
        raise ValueError("Editorial reorganisation changed native component identities")
    if len(ordered) != 34:
        raise ValueError("Editorial navigation should contain 34 native pages")
    clean_attached_documents(files)
    update_attachment(components["20260930IMATERIALES40"], files)
    render_exports(files, tree, original_search, templates, block_templates, {pid: TEACHER for pid in TEACHER_CHILDREN})
    if not etree.DTD(BytesIO(files["content.dtd"])).validate(tree):
        raise ValueError("The editorial ODE model does not match its DTD")
    files["content.xml"] = etree.tostring(tree, encoding="UTF-8", xml_declaration=True, doctype='<!DOCTYPE ode SYSTEM "content.dtd">')
