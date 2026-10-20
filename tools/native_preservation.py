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
ATTACHMENT_LABELS = {
    "Cuaderno_de_ruta_MitoMapa_4_0.html": ("Mi cuaderno de ruta", "Planifica las tareas y registra lectura, fuentes, creación, revisión y cierre. HTML para imprimir o adaptar en un editor de textos."),
    "Rubrica_lectura_MitoMapa_4_0.html": ("Pauta cualitativa de lectura e impresión", "Criterios y descriptores cualitativos con espacio para evidencias, avances y un siguiente paso; sin puntuaciones."),
    "Rubrica_MitoMapa_4_0.csv": ("Pauta cualitativa editable", "CSV con criterios y descriptores cualitativos para seleccionar y adaptar al trabajo acordado; sin puntuaciones."),
}


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


def verify_component(original, current, files):
    """Allow only reviewed author, attachment and passport-footer changes."""
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
    elif iid == PASSPORT_ID:
        before, original_markup = game_payloads(field(original, "htmlView"))
        after, current_markup = game_payloads(field(current, "htmlView"))
        if (field(original, "odeIdeviceTypeName") != "checklist" or len(before) != 1
                or before[0].get("footer") != "MitoMapa canario · CC BY-NC-SA 4.0"):
            raise ValueError("The passport differs from the reviewed native checklist")
        permitted = deepcopy(before)
        permitted[0]["footer"] = "MitoMapa canario · CC BY-SA 4.0"
        if permitted != after or original_markup != current_markup:
            raise ValueError("The native passport changed beyond its reviewed licence footer")
        expected.find("o:htmlView", NS).text = field(current, "htmlView")
    elif field(original, "odeIdeviceTypeName") in {"puzzle", "quick-questions", "relate"}:
        before, original_markup = game_payloads(field(original, "htmlView"))
        after, current_markup = game_payloads(field(current, "htmlView"))
        if without_project_authors(before) != after or original_markup != current_markup:
            raise ValueError(f"The native game changed beyond project authorship: {iid}")
        expected.find("o:htmlView", NS).text = field(current, "htmlView")
    if etree.tostring(expected) != etree.tostring(current):
        raise ValueError(f"A native activity changed beyond the reviewed editorial fields: {iid}")
