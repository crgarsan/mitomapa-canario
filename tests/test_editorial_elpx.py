"""Protect the publication review's native content and editorial requirements.

The ELPX and the website are separate resources. These checks inspect the
editable model as well as the generated HTML and search data, rather than
accepting a tidy-looking export with stale editor content.
"""

import base64
import copy
import json
from pathlib import Path
import posixpath
import re
import unittest
from urllib.parse import unquote, urlsplit
import zipfile

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
NS = {"o": "http://www.intef.es/xsd/ode"}
COVER = "GBC20261006PORTADA"
TEACHER = "20260823155836GUIAXU"
SOURCES = "GBC20261006FUENTES"
CREDITS = "20260823155836CREDJS"
WEB_EXTRA = "20261006EXPLORER440"
VERSION_COMPONENT = "20260929THISTORIAL39"
AUTHORS = ("Jesica Fortes Regalado", "Gloria Elsa González Martín", "Cristian García Santana")
PROJECT_AUTHORS = "; ".join(AUTHORS)
PASSPORT = "20260823155836CHKPAS"
PASSPORT_FOOTER = "MitoMapa canario · CC BY-SA 4.0"
BADGE_IMAGES = {
    "20260823155837TF1RWN": ("sol", "Pintadera de la luz", "tenerife", "Vasija de barro de Tenerife"),
    "20260823155837TF2UX8": ("seis_triangulos", "Pintadera de la memoria", "gran_canaria", "Vasija de barro de Gran Canaria"),
    "20260823155837TF3PNS": ("dentada", "Pintadera de Idafe", "la_palma", "Vasija de barro de La Palma"),
    "20260823155837TF4ICZ": ("triangulo", "Pintadera del encuentro", "la_gomera", "Vasija de barro de La Gomera"),
    "20260823155837TF58IT": ("circulos", "Pintadera de la niebla", "el_hierro", "Vasija de barro de El Hierro"),
    "20260823155837TF6TMM": ("doble_triangulo", "Pintadera de Mafasca", "fuerteventura", "Vasija de barro de Fuerteventura"),
    "20260823155837TF7K1Z": ("chevron", "Pintadera de Ico", "lanzarote", "Vasija de barro de Lanzarote"),
    "20260823155837TF8283": ("espiral_cuadrada", "Pintadera del horizonte", "la_graciosa", "Caracola de barro, símbolo contemporáneo de La Graciosa"),
}
REMOVED_TEACHER_PAGES = {
    "GBC20261006CURRICULO", "GBC20261006METODO", "GBC20261006RECURSOS",
    "GBC20261006SEGUIMIENTO", "20260823155836LOCUT0",
}
GAMES = {"puzzle", "scrambled-list", "quick-questions", "trueorfalse", "relate", "complete"}
MEDIA = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".wav", ".opus", ".woff", ".woff2", ".ico"}
PLURAL = re.compile(r"\b(?:vosotr[oa]s|vuestro?s?|vuestra?s?|vais|habéis|sois|estáis|tenéis|podéis|debéis|sabéis|necesitéis|acordad|elegid|leed|escuchad|comparad|anotad|buscad|completad|compartid|trabajad|utilizad|realizad|formad|decid|escribid|recordad|revisad|señalad|explicad)\b", re.I)
EDITION = re.compile(r"\b(?:edici[oó]n|versi[oó]n|web|REA|aplicaci[oó]n)\s+(?:web\s+)?\d+\.\d+(?:\.\d+)?\b", re.I)
NON_COMMERCIAL_LICENSE = re.compile(
    r"\b(?:CC[\s-]*)?BY[\s-]+NC(?:[\s-]+(?:SA|ND))?\b|creativecommons\.org/licenses/by-nc(?:-|/)", re.I,
)


def field(node, name):
    return node.findtext("o:" + name, default="", namespaces=NS)


def archive(path):
    with zipfile.ZipFile(path) as package:
        return {name: package.read(name) for name in package.namelist()}


def fragment(markup):
    return html.fragment_fromstring(markup or "<div></div>", create_parent=True)


def readable(markup):
    return " ".join(fragment(markup).text_content().split())


def page_components(page):
    return page.findall(".//o:odeComponent", NS)


def text_markup(component):
    if field(component, "odeIdeviceTypeName") != "text":
        return ""
    return json.loads(field(component, "jsonProperties"))["textTextarea"]


def search_data(files):
    source = files["search_index.js"].decode()
    return json.loads(source[source.index("{"):].rstrip(";\n"))


def native_payload(raw):
    """Decode the two formats used by the published native game runtimes."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        decoded_escape = re.sub(
            r"%u([0-9A-Fa-f]{4})|%([0-9A-Fa-f]{2})",
            lambda match: chr(int(match[1] or match[2], 16)), raw,
        )
        return json.loads("".join(chr(ord(char) ^ 146) for char in decoded_escape))


def payload_markup(node):
    # Relate stores raw JSON containing HTML instructions. HTML parsing turns
    # those instruction tags into children, so read the complete innerHTML.
    return (node.text or "") + "".join(html.tostring(child, encoding="unicode") for child in node)


def without_project_credit(value):
    """Change only the exact project credit; preserve questions and answers."""
    if isinstance(value, list):
        return [without_project_credit(child) for child in value]
    if isinstance(value, dict):
        return {key: "" if key == "author" and child == PROJECT_AUTHORS else without_project_credit(child)
                for key, child in value.items()}
    return value


def payload_strings(value, path="$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from payload_strings(child, path + "." + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from payload_strings(child, f"{path}[{index}]")


class EditorialElpxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = json.loads((ROOT / "VERSION.json").read_text())
        cls.files = archive(ROOT / cls.version["download"]["path"])
        cls.baseline = archive(ROOT / cls.version["elpx_source"]["path"])
        parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True)
        cls.tree = etree.fromstring(cls.files["content.xml"], parser)
        cls.old_tree = etree.fromstring(cls.baseline["content.xml"], parser)
        cls.pages = {field(page, "odePageId"): page for page in cls.tree.findall(".//o:odeNavStructure", NS)}
        cls.components = {field(c, "odeIdeviceId"): c for c in cls.tree.findall(".//o:odeComponent", NS)}
        cls.old_components = {field(c, "odeIdeviceId"): c for c in cls.old_tree.findall(".//o:odeComponent", NS)}
        cls.search = search_data(cls.files)

    def test_editorial_reorganisation_preserves_all_games_and_media(self):
        self.assertEqual(len(self.pages), 34)
        self.assertEqual(len(self.components), 118)
        self.assertEqual(set(self.components), set(self.old_components))
        self.assertFalse(REMOVED_TEACHER_PAGES & self.pages.keys())
        games = {iid for iid, node in self.components.items() if field(node, "odeIdeviceTypeName") in GAMES}
        self.assertEqual(len(games), 42)
        changed_games = 0
        changed_badges = 0
        changed_vocabulary = 0
        for iid in games:
            with self.subTest(game=iid):
                original = self.old_components[iid]
                current = self.components[iid]
                if iid in BADGE_IMAGES:
                    old_name, old_alt, slug, new_alt = BADGE_IMAGES[iid]
                    prefix = "{{context_path}}/content/resources/"
                    old_image = f'src="{prefix}pintadera_{old_name}.webp" alt="{old_alt}"'
                    new_image = f'src="{prefix}insignia_{slug}.webp" alt="{new_alt}"'
                    expected = copy.deepcopy(original)
                    for name in ("jsonProperties", "htmlView"):
                        before_image, after_image = old_image, new_image
                        if name == "jsonProperties":
                            before_image = json.dumps(before_image, ensure_ascii=False)[1:-1]
                            after_image = json.dumps(after_image, ensure_ascii=False)[1:-1]
                        self.assertEqual(field(expected, name).count(before_image), 1)
                        expected.find("o:" + name, NS).text = field(expected, name).replace(before_image, after_image, 1)
                        expected.find("o:" + name, NS).text = field(expected, name).replace(
                            "<strong>" + old_alt + "</strong>",
                            "<strong>" + old_alt.replace("Pintadera", "Pieza", 1) + "</strong>", 1,
                        )
                    self.assertEqual(etree.tostring(expected), etree.tostring(current), iid)
                    changed_badges += 1
                    continue
                before = fragment(field(original, "htmlView"))
                after = fragment(field(current, "htmlView"))
                old_data = before.xpath(".//*[contains(@class,'-DataGame')]")
                new_data = after.xpath(".//*[contains(@class,'-DataGame')]")
                self.assertEqual(len(old_data), len(new_data), iid)
                changed = False
                vocabulary = field(original, "odeIdeviceTypeName") == "complete"
                for old_node, new_node in zip(old_data, new_data, strict=True):
                    old_value = native_payload(payload_markup(old_node))
                    expected = without_project_credit(old_value)
                    current_value = native_payload(payload_markup(new_node))
                    if vocabulary:
                        self.assertEqual(current_value["wordsErrors"], "")
                        self.assertEqual(current_value["type"], 2)
                        self.assertIn("Selecciona", current_value["instructions"])
                        restored = copy.deepcopy(current_value)
                        for key in ("instructions", "textText", "wordsErrors"):
                            restored[key] = expected[key]
                        self.assertEqual(restored, expected, iid)
                        self.assertNotEqual(current_value["textText"], old_value["textText"])
                        changed_vocabulary += 1
                    else:
                        self.assertEqual(current_value, expected, iid)
                        changed |= old_value != expected
                    # Compare all other HTML, not just the game data.
                    for node in (old_node, new_node):
                        for child in list(node):
                            node.remove(child)
                        node.text = "VERIFIED_NATIVE_GAME_DATA"
                if vocabulary:
                    old_markup = html.tostring(before, encoding="unicode")
                    new_markup = html.tostring(after, encoding="unicode")
                    def text_field(value):
                        return re.sub(r'%u([0-9A-Fa-f]{4})|%([0-9A-Fa-f]{2})',
                                      lambda match: chr(int(match[1] or match[2], 16)), value)
                    expected_markup = old_markup.replace(text_field(old_value["textText"]), text_field(current_value["textText"]), 1)
                    expected_markup = expected_markup.replace(old_value["instructions"], current_value["instructions"], 1)
                    self.assertEqual(expected_markup, new_markup, iid)
                    old_component = copy.deepcopy(original)
                    new_component = copy.deepcopy(current)
                    old_component.find("o:htmlView", NS).text = "VERIFIED_NATIVE_VOCABULARY"
                    new_component.find("o:htmlView", NS).text = "VERIFIED_NATIVE_VOCABULARY"
                    self.assertEqual(etree.tostring(old_component), etree.tostring(new_component), iid)
                elif changed:
                    self.assertIn(field(original, "odeIdeviceTypeName"), {"puzzle", "quick-questions", "relate"})
                    changed_games += 1
                    self.assertEqual(html.tostring(before), html.tostring(after), iid)
                    old_component = copy.deepcopy(original)
                    new_component = copy.deepcopy(current)
                    old_component.find("o:htmlView", NS).text = "VERIFIED_NATIVE_GAME_HTML"
                    new_component.find("o:htmlView", NS).text = "VERIFIED_NATIVE_GAME_HTML"
                    self.assertEqual(etree.tostring(old_component), etree.tostring(new_component), iid)
                else:
                    self.assertEqual(etree.tostring(original), etree.tostring(current), iid)
        self.assertEqual(changed_games, 25)
        self.assertEqual(changed_badges, 8)
        self.assertEqual(changed_vocabulary, 8)
        for name, payload in self.baseline.items():
            if name in {"screenshot.png", "content/resources/screenshot.png"}:
                continue
            if Path(name).suffix.lower() in MEDIA:
                with self.subTest(media=name):
                    self.assertEqual(self.files.get(name), payload)

    def test_publication_thumbnail_and_editor_metadata_use_the_current_cover(self):
        specification = self.version["elpx_thumbnail"]
        image = (ROOT / specification["path"]).read_bytes()
        for name in ("screenshot.png", "content/resources/screenshot.png"):
            with self.subTest(thumbnail=name):
                self.assertTrue(self.files[name] == image, "Published thumbnail differs from the reviewed cover")
        self.assertTrue(image != self.baseline["screenshot.png"], "Published thumbnail still depicts the old cover")
        screenshot = self.tree.findtext(".//o:odeProperty[o:key='pp_screenshot']/o:value", namespaces=NS)
        self.assertTrue(screenshot == "data:image/png;base64," + base64.b64encode(image).decode("ascii"),
                        "Editor preview differs from the published thumbnail")

    def test_cover_has_four_pintaderas_above_the_original_map_and_four_below(self):
        markup = "".join(text_markup(c) for c in page_components(self.pages[COVER]))
        document = fragment(markup)
        text = readable(markup)
        self.assertIn("MitoMapa canario", text)
        for author in AUTHORS:
            self.assertIn(author, text)
        self.assertIn("CC BY-SA 4.0", text)
        for unwanted in ("curricular", "Primaria", "Lengua Castellana", "Conocimiento del Medio", "TongApp", "El Museo Canario", "ImageGen", "Astra", self.version["rea_exelearning_version"]):
            self.assertNotIn(unwanted.casefold(), text.casefold())
        decorations = document.xpath(".//img[contains(@src,'pintadera')]")
        self.assertEqual(len(decorations), 8)
        self.assertTrue(all(image.get("alt") == "" for image in decorations))
        map_images = document.xpath(".//img[substring(@src,string-length(@src)-string-length('mapa_canarias.webp')+1)='mapa_canarias.webp']")
        self.assertEqual(len(map_images), 1)
        map_image = map_images[0]
        self.assertEqual(map_image.get("src"), "{{context_path}}/content/resources/mapa_canarias.webp")
        self.assertTrue(map_image.get("alt"))
        visuals = document.xpath(".//img[contains(@src,'pintadera') or substring(@src,string-length(@src)-string-length('mapa_canarias.webp')+1)='mapa_canarias.webp']")
        self.assertEqual(visuals[:4], decorations[:4])
        self.assertIs(visuals[4], map_image)
        self.assertEqual(visuals[5:], decorations[4:])
        references = document.xpath(".//a/@href")
        self.assertTrue(references)
        self.assertTrue(all(url.startswith("https://creativecommons.org/licenses/by-sa/4.0/") for url in references), references)

    def test_project_names_and_edition_are_not_repeated_throughout_activities(self):
        self.assertIn(VERSION_COMPONENT, self.components)
        current_version_seen = False
        for pid, page in self.pages.items():
            for component in page_components(page):
                iid = field(component, "odeIdeviceId")
                markup = text_markup(component)
                if not markup:
                    continue
                document = fragment(markup)
                text = readable(markup)
                accessible = " ".join(document.xpath(".//@aria-label | .//@alt | .//@title"))
                if pid not in {COVER, CREDITS}:
                    for author in AUTHORS:
                        self.assertNotIn(author, text + " " + accessible, iid)
                self.assertIsNone(re.search(r"\bOA\b", text), iid)
                self.assertIsNone(PLURAL.search(text), iid)
                if iid != VERSION_COMPONENT:
                    self.assertIsNone(EDITION.search(text), (iid, EDITION.findall(text)))
                    self.assertNotIn(self.version["rea_exelearning_version"], text, iid)
                else:
                    current_version_seen = self.version["rea_exelearning_version"] in text
        self.assertTrue(current_version_seen)
        for page in self.search.values():
            document = html.fromstring(self.files[page["fileUrl"]])
            footers = document.xpath("//*[@id='siteUserFooter']")
            for footer in footers:
                self.assertFalse(any(author in footer.text_content() for author in AUTHORS))
                self.assertNotIn(self.version["rea_exelearning_version"], footer.text_content())

    def test_teacher_materials_share_one_page_in_collapsible_boxes(self):
        teacher = self.pages[TEACHER]
        old_pages = {field(p, "odePageId"): p for p in self.old_tree.findall(".//o:odeNavStructure", NS)}
        old_ids = {field(c, "odeIdeviceId") for pid in REMOVED_TEACHER_PAGES | {TEACHER} for c in page_components(old_pages[pid])}
        # The historical-names source box belongs with the collected sources.
        moved_source = "20260929TNOMBRES39"
        self.assertEqual({field(c, "odeIdeviceId") for c in page_components(teacher)}, old_ids - {moved_source})
        self.assertIn(moved_source, {field(c, "odeIdeviceId") for c in page_components(self.pages[SOURCES])})
        blocks = teacher.findall(".//o:odePagStructure", NS)
        # eXe calls each editable box an odePagStructure.
        self.assertGreaterEqual(len(blocks), 7)
        for block in blocks:
            props = {field(prop, "key"): field(prop, "value") for prop in block.findall("o:odePagStructureProperties/o:odePagStructureProperty", NS)}
            self.assertEqual(props.get("allowToggle"), "true", field(block, "odeBlockId"))
            self.assertEqual(props.get("minimized"), "true", field(block, "odeBlockId"))
        exported = html.fromstring(self.files[self.search[TEACHER]["fileUrl"]])
        boxes = exported.xpath("//article[contains(concat(' ',normalize-space(@class),' '),' box ')]")
        self.assertEqual(len(boxes), len(blocks))
        for box in boxes:
            self.assertIn("minimized", box.get("class", "").split())
            self.assertTrue(box.xpath("./header//button[contains(@class,'box-toggle')]"))

    def test_teacher_guide_does_not_confuse_the_native_passport_with_web_unlocks(self):
        guide = readable(text_markup(self.components["20260823155837TGUID1"]))
        self.assertNotIn("Reunir las ocho desbloquea el gran reto", guide)
        self.assertNotIn("superarlo permite preparar el diploma", guide)
        self.assertIn("marquen manualmente el pasaporte", guide)
        self.assertIn("itinerario corto sin recorrer las ocho", guide)

    def test_image_sources_mark_original_history_and_the_current_decorative_role(self):
        section = fragment(text_markup(self.components["GBCTFUENTES"])).xpath(".//*[@id='fuentes-imagenes']")[0]
        paragraphs = section.xpath("./div/p")
        decoration = next(p for p in paragraphs if "Las pintaderas se inspiran" in p.text_content())
        self.assertNotIn("como símbolos del pasaporte", decoration.text_content())
        self.assertIn("Se conservan como elementos decorativos del recurso", decoration.text_content())
        self.assertIn("https://www.elmuseocanario.com/images/documentospdf/pintaderaselmuseocanario.pdf",
                      decoration.xpath(".//a/@href"))
        history = [p for p in paragraphs if "Generación: agosto de 2026" in p.text_content()]
        self.assertEqual(len(history), 1)
        self.assertTrue(history[0].text_content().startswith("Historial de la edición original: "))

    def test_story_sources_and_uncertainties_are_collected_in_source_boxes(self):
        markup = "".join(text_markup(c) for c in page_components(self.pages[SOURCES]))
        source_document = fragment(markup)
        self.assertGreaterEqual(len(source_document.xpath(".//details[summary]")), 8)
        collected = set(source_document.xpath(".//a/@href"))
        routes = source_document.xpath(".//*[@data-source-route]/@data-source-route")
        self.assertEqual(set(routes), {"tenerife", "gran-canaria", "la-palma", "la-gomera", "el-hierro", "fuerteventura", "lanzarote", "la-graciosa"})
        for iid, original in self.old_components.items():
            old_markup = text_markup(original)
            old_document = fragment(old_markup)
            traces = old_document.xpath(".//*[@data-source-route]")
            for trace in traces:
                for reference in trace.xpath(".//a/@href"):
                    self.assertIn(reference, collected, (iid, reference))
                # The complete caution/adaptation text must survive its move.
                moved = source_document.xpath(".//*[@data-source-route=$route]", route=trace.get("data-source-route"))
                self.assertTrue(moved)
                # Preserve the complete source note, allowing only the
                # terminology replacement explicitly requested for this edition.
                expected_trace = " ".join(trace.text_content().split()).replace(
                    "origen indígena", "origen aborigen")
                self.assertIn(expected_trace, " ".join(moved[0].text_content().split()))
            if traces:
                self.assertFalse(fragment(text_markup(self.components[iid])).xpath(".//*[@data-source-route]"), iid)

    def test_web_is_only_an_external_extra_at_the_end(self):
        ordered = list(self.pages)
        self.assertEqual(ordered[-1], WEB_EXTRA)
        page = self.pages[WEB_EXTRA]
        self.assertIn("web", field(page, "pageName").casefold())
        markup = "".join(text_markup(c) for c in page_components(page))
        links = fragment(markup).xpath(".//a/@href")
        self.assertTrue(any(url.startswith("https://mitomapacanario.org/") for url in links))
        for component in self.components.values():
            markup = text_markup(component)
            self.assertFalse(fragment(markup).xpath(".//iframe"), field(component, "odeIdeviceId"))
            self.assertNotIn("{{context_path}}/content/resources/mitomapa/index.html", markup)
            self.assertNotIn("{{context_path}}/content/resources/mitomapa/valoracion.html", markup)
        self.assertNotIn("content/resources/mitomapa/index.html", self.files)
        self.assertNotIn("content/resources/mitomapa/scripts.js", self.files)

    def test_the_eight_story_narratives_survive_the_editorial_move_of_sources(self):
        stories = 0
        for iid, original in self.old_components.items():
            old_document = fragment(text_markup(original))
            if not old_document.xpath(".//*[@data-source-route]"):
                continue
            paragraphs = []
            collecting = False
            for child in old_document:
                if child.tag == "blockquote":
                    collecting = True
                    continue
                if collecting and child.tag in {"h2", "h3", "section"}:
                    break
                if collecting and child.tag == "p":
                    paragraphs.append(" ".join(child.text_content().split()))
            self.assertGreaterEqual(len(paragraphs), 4, iid)
            current_document = fragment(text_markup(self.components[iid]))
            current_paragraphs = [" ".join(node.text_content().split()) for node in current_document if node.tag == "p"]
            self.assertIn(paragraphs[0], current_paragraphs, iid)
            start = current_paragraphs.index(paragraphs[0])
            self.assertEqual(current_paragraphs[start:start + len(paragraphs)], paragraphs, iid)
            stories += 1
        self.assertEqual(stories, 8)

    def test_editable_preview_search_export_and_navigation_are_consistent(self):
        self.assertEqual(set(self.search), set(self.pages))
        checked = 0
        for pid, entry in self.search.items():
            document = html.fromstring(self.files[entry["fileUrl"]])
            export_dir = posixpath.dirname(entry["fileUrl"])
            links = document.xpath("//nav[@id='siteNav']//a/@href")
            destinations = {posixpath.normpath(posixpath.join(export_dir, urlsplit(url).path)) for url in links}
            self.assertEqual(destinations, {p["fileUrl"] for p in self.search.values()}, pid)
            for block in entry["blocks"].values():
                for iid, search_idevice in block["idevices"].items():
                    component = self.components[iid]
                    markup = text_markup(component)
                    if not markup:
                        continue
                    expected = readable(markup)
                    self.assertEqual(readable(field(component, "htmlView")), expected, iid)
                    self.assertEqual(readable(search_idevice["htmlView"]), expected, iid)
                    exported = document.xpath("//*[@id=$id]", id=iid)
                    self.assertEqual(len(exported), 1, iid)
                    self.assertEqual(" ".join(exported[0].text_content().split()), expected, iid)
                    for url in fragment(markup).xpath(".//@href | .//@src | .//@poster"):
                        if url.startswith("exe-node:"):
                            self.assertIn(url.removeprefix("exe-node:").split("#", 1)[0], self.pages, (iid, url))
                        elif url.startswith("{{context_path}}/"):
                            self.assertNotIn("#", url, iid)
                            self.assertNotIn("?", url, iid)
                            self.assertIn(unquote(url.removeprefix("{{context_path}}/")), self.files, (iid, url))
                    checked += 1
        self.assertEqual(checked, 63)

    def test_license_and_acknowledgements_are_explicit(self):
        properties = {field(p, "key"): field(p, "value") for p in self.tree.findall(".//o:odeProperty", NS)}
        self.assertIn("share alike 4.0", properties["pp_license"].casefold())
        self.assertNotIn("non-commercial", properties["pp_license"].casefold())
        self.assertNotIn("noncommercial", properties["pp_license"].casefold())
        credits = " ".join(readable(text_markup(c)) for c in page_components(self.pages[CREDITS]))
        credit_links = fragment("".join(text_markup(c) for c in page_components(self.pages[CREDITS]))).xpath(".//a/@href")
        self.assertIn("https://creativecommons.org/licenses/by-sa/4.0/deed.es", credit_links)
        self.assertRegex(credits.casefold(), r"(?:cc by-sa 4\.0|reconocimiento-compartirigual 4\.0)")
        self.assertRegex(credits.casefold(), r"agradeci")
        for area in ("históric", "técnic", "didáctic"):
            self.assertIn(area, credits.casefold())

    def test_all_activity_payloads_use_no_active_noncommercial_licence(self):
        # Native checklists and the progress report also have DataGame data;
        # checking only the 42 game iDevices misses the passport's report footer.
        checked = {"editable-preview": 0, "search": 0, "export": 0}
        for page in self.search.values():
            document = html.fromstring(self.files[page["fileUrl"]])
            for block in page["blocks"].values():
                for iid, entry in block["idevices"].items():
                    exported = document.xpath("//*[@id=$id]", id=iid)
                    self.assertEqual(len(exported), 1, iid)
                    representations = {
                        "editable-preview": field(self.components[iid], "htmlView"),
                        "search": entry["htmlView"],
                        "export": html.tostring(exported[0], encoding="unicode"),
                    }
                    for representation, markup in representations.items():
                        nodes = fragment(markup).xpath(".//*[contains(@class,'-DataGame')]")
                        for node in nodes:
                            payload = native_payload(payload_markup(node))
                            for path, text in payload_strings(payload):
                                self.assertIsNone(NON_COMMERCIAL_LICENSE.search(text), (iid, representation, path, text))
                            if iid == PASSPORT:
                                self.assertEqual(payload["footer"], PASSPORT_FOOTER, representation)
                            checked[representation] += 1
        self.assertEqual(checked, {"editable-preview": 44, "search": 44, "export": 44})

    def test_passport_changes_only_its_legacy_licence_and_collection_labels(self):
        original = self.old_components[PASSPORT]
        current = self.components[PASSPORT]
        self.assertEqual(field(original, "odeIdeviceTypeName"), "checklist")
        before = fragment(field(original, "htmlView"))
        after = fragment(field(current, "htmlView"))
        old_nodes = before.xpath(".//*[contains(@class,'listacotejo-DataGame')]")
        new_nodes = after.xpath(".//*[contains(@class,'listacotejo-DataGame')]")
        self.assertEqual(len(old_nodes), 1)
        self.assertEqual(len(new_nodes), 1)
        expected = native_payload(payload_markup(old_nodes[0]))
        self.assertEqual(expected["footer"], "MitoMapa canario · CC BY-NC-SA 4.0")
        expected["footer"] = PASSPORT_FOOTER
        expected["title"] = "Pasaporte de piezas"
        expected["levels"][0]["item"] = "Pasaporte de piezas"
        for level in expected["levels"][1:]:
            level["item"] = level["item"].replace("Pintadera", "Pieza")
        expected["msgs"]["msgList"] = "pasaporte de piezas"
        self.assertEqual(native_payload(payload_markup(new_nodes[0])), expected)
        for node in (old_nodes[0], new_nodes[0]):
            for child in list(node):
                node.remove(child)
            node.text = "VERIFIED_PASSPORT_DATA"
        self.assertEqual(html.tostring(before), html.tostring(after))
        old_component = copy.deepcopy(original)
        new_component = copy.deepcopy(current)
        old_component.find("o:htmlView", NS).text = "VERIFIED_PASSPORT_HTML"
        new_component.find("o:htmlView", NS).text = "VERIFIED_PASSPORT_HTML"
        self.assertEqual(etree.tostring(old_component), etree.tostring(new_component))


if __name__ == "__main__":
    unittest.main()
