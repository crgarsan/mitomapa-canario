"""Verify editorial-only exceptions without trusting the code that edits them."""
from copy import deepcopy
from html import escape
import json
import re

from lxml import etree, html

NS = {"o": "http://www.intef.es/xsd/ode"}
AUTHORS = "Jesica Fortes Regalado; Gloria Elsa González Martín; Cristian García Santana"
ATTACHMENT_ID = "20260930IMATERIALES40"
PASSPORT_ID = "20260823155836CHKPAS"
FINAL_CHECKLIST_ID = "20260823155837CHKFIN"
CREATION_CHECKLIST_IDS = frozenset(f"20260823155837CHKCR{index}" for index in range(1, 9))
PASSPORT_ITEMS = (
    "<strong>Tenerife</strong> · Pintadera de la luz",
    "<strong>Gran Canaria</strong> · Pintadera de la memoria",
    "<strong>La Palma</strong> · Pintadera de Idafe",
    "<strong>La Gomera</strong> · Pintadera del encuentro",
    "<strong>El Hierro</strong> · Pintadera de la niebla",
    "<strong>Fuerteventura</strong> · Pintadera de Mafasca",
    "<strong>Lanzarote</strong> · Pintadera de Ico",
    "<strong>La Graciosa</strong> · Pintadera del horizonte",
)
# Keep the verifier's reviewed artwork independent of the code applying it.
PASSPORT_BADGES = {
    "20260823155837TF1RWN": ("sol", "Pintadera de la luz", "tenerife", "Vasija de barro de Tenerife"),
    "20260823155837TF2UX8": ("seis_triangulos", "Pintadera de la memoria", "gran_canaria", "Vasija de barro de Gran Canaria"),
    "20260823155837TF3PNS": ("dentada", "Pintadera de Idafe", "la_palma", "Vasija de barro de La Palma"),
    "20260823155837TF4ICZ": ("triangulo", "Pintadera del encuentro", "la_gomera", "Vasija de barro de La Gomera"),
    "20260823155837TF58IT": ("circulos", "Pintadera de la niebla", "el_hierro", "Vasija de barro de El Hierro"),
    "20260823155837TF6TMM": ("doble_triangulo", "Pintadera de Mafasca", "fuerteventura", "Vasija de barro de Fuerteventura"),
    "20260823155837TF7K1Z": ("chevron", "Pintadera de Ico", "lanzarote", "Vasija de barro de Lanzarote"),
    "20260823155837TF8283": ("espiral_cuadrada", "Pintadera del horizonte", "la_graciosa", "Caracola de barro, símbolo contemporáneo de La Graciosa"),
}
ATTACHMENT_LABELS = {
    "Cuaderno_de_ruta_MitoMapa_4_0.html": ("Mi cuaderno de ruta", "Planifica las tareas y registra lectura, fuentes, creación, revisión y cierre. HTML para imprimir o adaptar en un editor de textos."),
    "Rubrica_lectura_MitoMapa_4_0.html": ("Pauta cualitativa de lectura e impresión", "Criterios y descriptores cualitativos con espacio para evidencias, avances y un siguiente paso; sin puntuaciones."),
    "Rubrica_MitoMapa_4_0.csv": ("Pauta cualitativa editable", "CSV con criterios y descriptores cualitativos para seleccionar y adaptar al trabajo acordado; sin puntuaciones."),
}


# Exact before/after fields reviewed after the native vocabulary audit.
REVIEWED_VOCABULARY = {'20260823155837COM1YD': {'instructions': ('<p>Busca en el cuento el sinónimo de cada verbo.</p>',
                                           '<p>Selecciona el sinónimo de cada verbo. Puedes volver al '
                                           'cuento.</p>'),
                          'textText': ('<p>Busca en el cuento el sinónimo de cada '
                                       'verbo.</p><ol><li><strong>habitaban</strong>: @@vivían | vivian@@ '
                                       '<em>(Pista: Aparece en la primera '
                                       'oración.)</em></li><li><strong>iniciar</strong>: @@comenzar@@ '
                                       '<em>(Pista: Dácil esperaba la luz para hacerlo con el '
                                       'camino.)</em></li><li><strong>narra</strong>: @@cuenta@@ <em>(Pista: '
                                       'La tradición lo hace en el quinto '
                                       'párrafo.)</em></li><li><strong>finalizar</strong>: @@terminar@@ '
                                       '<em>(Pista: Aparece cerca del final.)</em></li></ol>',
                                       '<p>Selecciona el sinónimo de cada verbo. Puedes volver al '
                                       'cuento.</p><ol><li><strong>habitaban</strong>: @@vivían@@ '
                                       '<em>(Pista: Aparece en la primera '
                                       'oración.)</em></li><li><strong>iniciar</strong>: @@comenzar@@ '
                                       '<em>(Pista: Dácil esperaba la luz para hacerlo con el '
                                       'camino.)</em></li><li><strong>narra</strong>: @@cuenta@@ <em>(Pista: '
                                       'La tradición lo hace en el quinto '
                                       'párrafo.)</em></li><li><strong>finalizar</strong>: @@terminar@@ '
                                       '<em>(Pista: Aparece cerca del final.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM2J3': {'instructions': ('<p>Escribe el antónimo que aparece en el cuento.</p>',
                                           '<p>Selecciona el antónimo de cada palabra; utiliza el cuento '
                                           'como apoyo.</p>'),
                          'textText': ('<p>Escribe el antónimo que aparece en el '
                                       'cuento.</p><ol><li><strong>grande</strong>: @@pequeño | pequeno@@ '
                                       '<em>(Pista: Está en el '
                                       'estribillo.)</em></li><li><strong>apagó</strong>: @@encendió | '
                                       'encendio@@ <em>(Pista: Guayarmina lo hizo con una '
                                       'tea.)</em></li><li><strong>oscuridad</strong>: @@luz@@ <em>(Pista: '
                                       'Protegió al grupo durante la '
                                       'noche.)</em></li><li><strong>día</strong>: @@noche@@ <em>(Pista: Es '
                                       'el momento en el que aparece la criatura.)</em></li></ol>',
                                       '<p>Selecciona el antónimo de cada palabra; utiliza el cuento como '
                                       'apoyo.</p><ol><li><strong>grande</strong>: @@pequeño@@ <em>(Pista: '
                                       'Está en el estribillo.)</em></li><li><strong>apagó</strong>: '
                                       '@@encendió@@ <em>(Pista: Guayarmina lo hizo con una '
                                       'tea.)</em></li><li><strong>oscuridad</strong>: @@luz@@ <em>(Pista: '
                                       'Protegió al grupo durante la '
                                       'noche.)</em></li><li><strong>día</strong>: @@noche@@ <em>(Pista: Es '
                                       'el momento en el que aparece la criatura.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM3VY': {'instructions': ('<p>Completa con la expresión del cuento que tiene un significado '
                                           'parecido.</p>',
                                           '<p>Selecciona una expresión con significado parecido. Puedes '
                                           'volver al cuento.</p>'),
                          'textText': ('<p>Completa con la expresión del cuento que tiene un significado '
                                       'parecido.</p><ol><li><strong>permanece erguido</strong>: @@sigue en '
                                       'pie | continuaba erguido@@ <em>(Pista: La primera opción aparece en '
                                       'el estribillo.)</em></li><li><strong>conservar el recuerdo</strong>: '
                                       '@@guardar la memoria | conservar la memoria@@ <em>(Pista: Aparece en '
                                       'el estribillo y al final.)</em></li></ol>',
                                       '<p>Selecciona una expresión con significado parecido. Puedes volver '
                                       'al cuento.</p><ol><li><strong>permanece erguido</strong>: @@sigue en '
                                       'pie | continuaba erguido@@ <em>(Pista: Recuerda el estribillo y lo '
                                       'que sucede después del temblor.)</em></li><li><strong>conservar el '
                                       'recuerdo</strong>: @@guardamos su memoria | guardar la memoria | '
                                       'conservar la memoria@@ <em>(Pista: Puedes apoyarte en el estribillo '
                                       'y en el final.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM4HJ': {'instructions': ('<p>Escribe un término con significado opuesto.</p>',
                                           '<p>Selecciona un término de significado opuesto; puedes '
                                           'deducirlo por el sentido del relato.</p>'),
                          'textText': ('<p>Escribe un término con significado '
                                       'opuesto.</p><ol><li><strong>enemistad</strong>: @@amistad@@ '
                                       '<em>(Pista: Piensa en una relación de afecto y '
                                       'apoyo.)</em></li><li><strong>callar</strong>: @@hablar | decir@@ '
                                       '<em>(Pista: El cuento invita a escuchar y dialogar.)</em></li></ol>',
                                       '<p>Selecciona un término de significado opuesto; puedes deducirlo '
                                       'por el sentido del relato.</p><ol><li><strong>enemistad</strong>: '
                                       '@@amistad@@ <em>(Pista: Piensa en una relación de afecto y '
                                       'apoyo.)</em></li><li><strong>callar</strong>: @@hablar | decir@@ '
                                       '<em>(Pista: El cuento invita a escuchar y dialogar.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM571': {'instructions': ('<p>Escribe el antónimo que aparece o se deduce del cuento.</p>',
                                           '<p>Selecciona el antónimo que aparece o se deduce del '
                                           'cuento.</p>'),
                          'textText': ('<p>Escribe el antónimo que aparece o se deduce del '
                                       'cuento.</p><ol><li><strong>aparecieron</strong>: @@desaparecieron | '
                                       'desapareció | desaparecio@@ <em>(Pista: La historia del árbol no lo '
                                       'hizo.)</em></li><li><strong>ocultar</strong>: @@mostrar | revelar | '
                                       'descubrir@@ <em>(Pista: Es lo contrario de guardar un '
                                       'secreto.)</em></li></ol>',
                                       '<p>Selecciona el antónimo que aparece o se deduce del '
                                       'cuento.</p><ol><li><strong>aparecieron</strong>: @@desaparecieron@@ '
                                       '<em>(Pista: Es lo contrario de hacerse '
                                       'visibles.)</em></li><li><strong>ocultar</strong>: @@mostrar | '
                                       'revelar | descubrir@@ <em>(Pista: Es lo contrario de guardar un '
                                       'secreto.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM6WT': {'instructions': ('<p>Escribe el antónimo que aparece en el cuento.</p>',
                                           '<p>Selecciona un antónimo para cada palabra; puede aparecer o '
                                           'deducirse del cuento.</p>'),
                          'textText': ('<p>Escribe el antónimo que aparece en el '
                                       'cuento.</p><ol><li><strong>apareció</strong>: @@desapareció | '
                                       'desaparecio@@ <em>(Pista: La claridad lo hizo al final de la '
                                       'noche.)</em></li><li><strong>noche</strong>: @@día | dia | '
                                       'amanecer@@ <em>(Pista: Los pastores volvieron '
                                       'después.)</em></li><li><strong>vieja</strong>: @@nueva | nuevo@@ '
                                       '<em>(Pista: Es su opuesto habitual.)</em></li></ol>',
                                       '<p>Selecciona un antónimo para cada palabra; puede aparecer o '
                                       'deducirse del cuento.</p><ol><li><strong>apareció</strong>: '
                                       '@@desapareció@@ <em>(Pista: La claridad se hizo pequeña hasta '
                                       'desaparecer.)</em></li><li><strong>noche</strong>: @@día | '
                                       'amanecer@@ <em>(Pista: Recuerda cuándo volvieron los '
                                       'pastores.)</em></li><li><strong>vieja</strong>: @@nueva@@ '
                                       '<em>(Pista: Es su opuesto habitual.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM7Z9': {'instructions': ('<p>Escribe un término de significado opuesto.</p>',
                                           '<p>Selecciona un término de significado opuesto; puedes '
                                           'deducirlo por el sentido del relato.</p>'),
                          'textText': ('<p>Escribe un término de significado '
                                       'opuesto.</p><ol><li><strong>entrar</strong>: @@salir@@ <em>(Pista: '
                                       'Ico lo hizo caminando al abrirse la '
                                       'puerta.)</em></li><li><strong>húmeda</strong>: @@seca | seco@@ '
                                       '<em>(Pista: Describe algo que no tiene agua.)</em></li></ol>',
                                       '<p>Selecciona un término de significado opuesto; puedes deducirlo '
                                       'por el sentido del relato.</p><ol><li><strong>entrar</strong>: '
                                       '@@salir@@ <em>(Pista: Ico lo hizo caminando al abrirse la '
                                       'puerta.)</em></li><li><strong>húmeda</strong>: @@seca@@ <em>(Pista: '
                                       'Describe algo que no tiene agua.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')},
 '20260823155837COM843': {'instructions': ('<p>Escribe el antónimo que aparece en el cuento.</p>',
                                           '<p>Selecciona el antónimo que aparece en el cuento.</p>'),
                          'textText': ('<p>Escribe el antónimo que aparece en el '
                                       'cuento.</p><ol><li><strong>apareció</strong>: @@desapareció | '
                                       'desaparecio@@ <em>(Pista: La isla lo hacía según la '
                                       'leyenda.)</em></li><li><strong>cerca</strong>: @@lejos | lejos de@@ '
                                       '<em>(Pista: Cuanto más avanzaban, así parecía estar la '
                                       'isla.)</em></li></ol>',
                                       '<p>Selecciona el antónimo que aparece en el '
                                       'cuento.</p><ol><li><strong>aparecía</strong>: @@desaparecía@@ '
                                       '<em>(Pista: La isla lo hacía según la '
                                       'leyenda.)</em></li><li><strong>cerca</strong>: @@lejos | lejos de@@ '
                                       '<em>(Pista: Cuanto más avanzaban, así parecía estar la '
                                       'isla.)</em></li></ol>'),
                          'wordsErrors': (' Cilios, Nueclolo', '')}}


def field(node, name):
    return node.findtext("o:" + name, default="", namespaces=NS)


def without_project_authors(data):
    if isinstance(data, dict):
        return {key: "" if key == "author" and value == AUTHORS else without_project_authors(value) for key, value in data.items()}
    if isinstance(data, list):
        return [without_project_authors(value) for value in data]
    return data


def game_payloads(view):
    """Read raw JSON before HTML parsing can interpret tags inside card strings."""
    pattern = re.compile(r'<div\b[^>]*\bclass=[\'"][^\'"]*\b[^\s\'"]*DataGame\b[^\'"]*[\'"][^>]*>', re.I)
    payloads = []
    normalized = view
    for match in reversed(list(pattern.finditer(view))):
        start = match.end()
        while start < len(view) and view[start].isspace():
            start += 1
        if view[start:start + 1] == "{":
            data, length = json.JSONDecoder().raw_decode(view[start:])
            end = start + length
        else:
            end = view.index("</div>", start)
            raw = view[start:end].strip()
            decoded = re.sub(r'%u([0-9a-f]{4})|%([0-9a-f]{2})', lambda m: chr(int(m.group(1) or m.group(2), 16)), raw, flags=re.I)
            data = json.loads("".join(chr(ord(character) ^ 146) for character in decoded))
        payloads.insert(0, data)
        normalized = normalized[:start] + "[verified native game data]" + normalized[end:]
    return payloads, normalized


def reviewed_escaped_text(value):
    """Independently reproduce the official text-field encoding for checks."""
    safe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./"
    encoded = []
    units = value.encode("utf-16-be", errors="surrogatepass")
    for offset in range(0, len(units), 2):
        number = int.from_bytes(units[offset:offset + 2], "big")
        character = chr(number)
        encoded.append(character if character in safe else f"%{number:02X}" if number < 256 else f"%u{number:04X}")
    return "".join(encoded)


def verify_component(original, current, files):
    """Allow only reviewed author, attachment, badge and checklist-label changes."""
    iid = field(original, "odeIdeviceId")
    expected = deepcopy(original)
    if iid == ATTACHMENT_ID:
        expected.find("o:odePageId", NS).text = "20260823155836GUIAXU"
        before = json.loads(field(original, "jsonProperties"))
        after = json.loads(field(current, "jsonProperties"))
        view = field(original, "htmlView")
        document = html.fragment_fromstring(view, create_parent=True)
        items = document.xpath(".//li[contains(@class,'fileAttachment-item')]")
        for entry, item in zip(before["attachments"], items, strict=True):
            title, description = ATTACHMENT_LABELS[entry["filename"]]
            old_title, old_description = entry["title"], entry["description"]
            entry.update(title=title, description=description, size=len(files["content/resources/" + entry["filename"]]))
            old_meta = item.xpath(".//span[@class='fileAttachment-meta']")[0].text
            new_meta = entry["filename"] + " · " + f'{entry["size"] / 1024:.1f} KB'
            for old, new in ((old_title, title), (old_description, description), (old_meta, new_meta)):
                view = view.replace(escape(old, quote=False), escape(new, quote=False))
        if before != after or view != field(current, "htmlView"):
            raise ValueError("The attachment changed outside its labels, page and measured sizes")
        expected.find("o:jsonProperties", NS).text = field(current, "jsonProperties")
        expected.find("o:htmlView", NS).text = view
    elif iid in PASSPORT_BADGES:
        if field(original, "odeIdeviceTypeName") != "trueorfalse":
            raise ValueError(f"The reviewed badge is not in its native true-or-false activity: {iid}")
        old_name, old_alt, slug, new_alt = PASSPORT_BADGES[iid]
        resource = "{{context_path}}/content/resources/"
        old_src = resource + f"pintadera_{old_name}.webp"
        new_src = resource + f"insignia_{slug}.webp"
        old_image = f'src="{old_src}" alt="{old_alt}"'
        new_image = f'src="{new_src}" alt="{new_alt}"'
        old_label = f"<strong>{old_alt}</strong>"
        new_label = f'<strong>{old_alt.replace("Pintadera", "Pieza", 1)}</strong>'
        properties = field(original, "jsonProperties")
        after_text = json.loads(properties).get("eXeIdeviceTextAfter", "")
        view = field(original, "htmlView")
        document = html.fragment_fromstring(view, create_parent=True)
        after_nodes = document.xpath(".//div[contains(concat(' ',normalize-space(@class),' '),' TOFP-After ')]")
        if (not isinstance(after_text, str) or after_text.count(old_image) != 1
                or view.count(old_image) != 1 or len(after_nodes) != 1
                or len(after_nodes[0].xpath(".//img[@src=$src and @alt=$alt]", src=old_src, alt=old_alt)) != 1
                or after_text.count(old_label) != 1 or view.count(old_label) != 1
                or len(after_nodes[0].xpath(".//strong[text()=$label]", label=old_alt)) != 1):
            raise ValueError(f"The badge differs from the reviewed native image: {iid}")
        quoted_after = json.dumps(after_text, ensure_ascii=False)
        if properties.count(quoted_after) != 1:
            raise ValueError(f"The reviewed badge's editable after-text is not unique: {iid}")
        # Substitute inside the original serialized fields, so formatting and
        # all questions, answers, settings and remaining markup stay exact.
        updated_after = after_text.replace(old_image, new_image, 1).replace(old_label, new_label, 1)
        expected.find("o:jsonProperties", NS).text = properties.replace(
            quoted_after, json.dumps(updated_after, ensure_ascii=False), 1,
        )
        expected.find("o:htmlView", NS).text = view.replace(old_image, new_image, 1).replace(old_label, new_label, 1)
    elif iid in {PASSPORT_ID, FINAL_CHECKLIST_ID} | CREATION_CHECKLIST_IDS:
        before, original_markup = game_payloads(field(original, "htmlView"))
        after, current_markup = game_payloads(field(current, "htmlView"))
        if (field(original, "odeIdeviceTypeName") != "checklist" or len(before) != 1
                or before[0].get("typeGame") != "Cotejo"
                or before[0].get("msgs", {}).get("msgList") != "pasaporte de pintaderas"):
            raise ValueError(f"The checklist differs from the reviewed native labels: {iid}")
        permitted = deepcopy(before)
        permitted[0]["msgs"]["msgList"] = "pasaporte de piezas"
        if iid == PASSPORT_ID:
            old_title = "Pasaporte de pintaderas"
            levels = before[0].get("levels", [])
            if (before[0].get("footer") != "MitoMapa canario · CC BY-NC-SA 4.0"
                    or before[0].get("title") != old_title
                    or [level.get("item") for level in levels] != [old_title, *PASSPORT_ITEMS]):
                raise ValueError("The passport differs from its reviewed footer and award labels")
            permitted[0]["footer"] = "MitoMapa canario · CC BY-SA 4.0"
            permitted[0]["title"] = "Pasaporte de piezas"
            permitted[0]["levels"][0]["item"] = "Pasaporte de piezas"
            for level, old_item in zip(permitted[0]["levels"][1:], PASSPORT_ITEMS, strict=True):
                level["item"] = old_item.replace("Pintadera", "Pieza", 1)
        elif iid == FINAL_CHECKLIST_ID:
            old_title = "Revisión del museo de pintaderas"
            levels = before[0].get("levels", [])
            if (before[0].get("title") != old_title or not levels
                    or levels[0].get("item") != old_title):
                raise ValueError("The museum checklist differs from its reviewed heading")
            permitted[0]["title"] = "Revisión del museo de piezas"
            permitted[0]["levels"][0]["item"] = "Revisión del museo de piezas"
        if permitted != after or original_markup != current_markup:
            raise ValueError(f"The native checklist changed beyond its reviewed labels and footer: {iid}")
        expected.find("o:htmlView", NS).text = field(current, "htmlView")
    elif iid == "20260930IDESCARGA40":
        old_title = "MitoMapa canario: ocho islas, ocho pintaderas"
        view = field(original, "htmlView")
        if (field(original, "odeIdeviceTypeName") != "download-source-file"
                or field(original, "jsonProperties") != "" or view.count(old_title) != 1):
            raise ValueError("The source download differs from its reviewed project title")
        expected.find("o:htmlView", NS).text = view.replace(
            old_title, "MitoMapa canario: ocho islas, ocho piezas", 1,
        )
    elif iid in REVIEWED_VOCABULARY:
        before, original_markup = game_payloads(field(original, "htmlView"))
        after, current_markup = game_payloads(field(current, "htmlView"))
        if (field(original, "odeIdeviceTypeName") != "complete" or len(before) != 1
                or before[0].get("typeGame") != "Completa" or before[0].get("type") != 2):
            raise ValueError("The reviewed vocabulary mode differs: " + iid)
        permitted = without_project_authors(before)
        for name, (old_value, new_value) in REVIEWED_VOCABULARY[iid].items():
            if name == "textText":
                old_value, new_value = reviewed_escaped_text(old_value), reviewed_escaped_text(new_value)
            if before[0].get(name) != old_value:
                raise ValueError(f"The reviewed vocabulary source field differs: {iid}/{name}")
            permitted[0][name] = new_value
        old_instruction, new_instruction = REVIEWED_VOCABULARY[iid]["instructions"]
        old_text, new_text = REVIEWED_VOCABULARY[iid]["textText"]
        if original_markup.count(old_instruction) != 2 or original_markup.count(old_text) != 1:
            raise ValueError("The original vocabulary instructions differ: " + iid)
        expected_markup = original_markup.replace(old_text, new_text, 1).replace(old_instruction, new_instruction, 1)
        if after != permitted or current_markup != expected_markup:
            raise ValueError("The vocabulary changed outside its reviewed instructions and choices: " + iid)
        expected.find("o:htmlView", NS).text = field(current, "htmlView")
    elif field(original, "odeIdeviceTypeName") in {"puzzle", "quick-questions", "relate"}:
        before, original_markup = game_payloads(field(original, "htmlView"))
        after, current_markup = game_payloads(field(current, "htmlView"))
        if without_project_authors(before) != after or original_markup != current_markup:
            raise ValueError(f"The native game changed beyond project authorship: {iid}")
        expected.find("o:htmlView", NS).text = field(current, "htmlView")
    if etree.tostring(expected) != etree.tostring(current):
        raise ValueError(f"A native activity changed beyond the reviewed editorial fields: {iid}")
