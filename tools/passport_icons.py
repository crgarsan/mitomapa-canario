"""Add the approved passport illustrations without replacing shared pintaderas."""

from pathlib import Path


NS = {"o": "http://www.intef.es/xsd/ode"}
PREFIX = "{{context_path}}/content/resources/"
SELECTORS = ("20260823155836TINTRO", "20260823155836TITINW")
ICONS = (
    ("tenerife", "Tenerife", "TF1RWN", "sol", "Pintadera de la luz"),
    ("gran_canaria", "Gran Canaria", "TF2UX8", "seis_triangulos", "Pintadera de la memoria"),
    ("la_palma", "La Palma", "TF3PNS", "dentada", "Pintadera de Idafe"),
    ("la_gomera", "La Gomera", "TF4ICZ", "triangulo", "Pintadera del encuentro"),
    ("el_hierro", "El Hierro", "TF58IT", "circulos", "Pintadera de la niebla"),
    ("fuerteventura", "Fuerteventura", "TF6TMM", "doble_triangulo", "Pintadera de Mafasca"),
    ("lanzarote", "Lanzarote", "TF7K1Z", "chevron", "Pintadera de Ico"),
    ("la_graciosa", "La Graciosa", "TF8283", "espiral_cuadrada", "Pintadera del horizonte"),
)
TF_ICON_IDS = frozenset("20260823155837" + row[2] for row in ICONS)


def replace_once(value, before, after):
    if value.count(before) != 1:
        raise ValueError("The native insignia differs from its reviewed image reference: " + before)
    return value.replace(before, after, 1)


def apply_passport_icons(files, root, components):
    """Change only image URLs, plus the approved alternatives on eight rewards."""
    for slug, island, suffix, old_name, old_alt in ICONS:
        filename = "insignia_" + slug + ".webp"
        resource = "content/resources/" + filename
        payload = (Path(root) / "assets/images" / filename).read_bytes()
        if resource in files and files[resource] != payload:
            raise ValueError("An existing native resource conflicts with the approved insignia: " + resource)
        files[resource] = payload
        old_source = PREFIX + "pintadera_" + old_name + ".webp"
        new_source = PREFIX + filename
        iid = "20260823155837" + suffix
        alternative = ("Caracola de barro, símbolo contemporáneo de La Graciosa"
                       if slug == "la_graciosa" else "Vasija de barro de " + island)
        for cid in (*SELECTORS, iid):
            for name in ("jsonProperties", "htmlView"):
                node = components[cid].find("o:" + name, NS)
                value = replace_once(node.text, old_source, new_source)
                if cid == iid:
                    quote = '\\"' if name == "jsonProperties" else '"'
                    value = replace_once(value, "alt=" + quote + old_alt + quote,
                                         "alt=" + quote + alternative + quote)
                node.text = value
