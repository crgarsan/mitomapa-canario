"""Protect the publication review's native content and editorial requirements.

The ELPX and the website are separate resources. These checks inspect the
editable model as well as the generated HTML and search data, rather than
accepting a tidy-looking export with stale editor content.
"""

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
REMOVED_TEACHER_PAGES = {
    "GBC20261006CURRICULO", "GBC20261006METODO", "GBC20261006RECURSOS",
    "GBC20261006SEGUIMIENTO", "20260823155836LOCUT0",
}
GAMES = {"puzzle", "scrambled-list", "quick-questions", "trueorfalse", "relate", "complete"}
MEDIA = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".wav", ".opus", ".woff", ".woff2", ".ico"}
PLURAL = re.compile(r"\b(?:vosotr[oa]s|vuestro?s?|vuestra?s?|vais|habéis|sois|estáis|tenéis|podéis|debéis|sabéis|necesitéis|acordad|elegid|leed|escuchad|comparad|anotad|buscad|completad|compartid|trabajad|utilizad|realizad|formad|decid|escribid|recordad|revisad|señalad|explicad)\b", re.I)
EDITION = re.compile(r"\b(?:edici[oó]n|versi[oó]n|web|REA|aplicaci[oó]n)\s+(?:web\s+)?\d+\.\d+(?:\.\d+)?\b", re.I)


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
        for iid in games:
            with self.subTest(game=iid):
                original = self.old_components[iid]
                current = self.components[iid]
                before = fragment(field(original, "htmlView"))
                after = fragment(field(current, "htmlView"))
                old_data = before.xpath(".//*[contains(@class,'-DataGame')]")
                new_data = after.xpath(".//*[contains(@class,'-DataGame')]")
                self.assertEqual(len(old_data), len(new_data), iid)
                changed = False
                for old_node, new_node in zip(old_data, new_data, strict=True):
                    old_value = native_payload(payload_markup(old_node))
                    expected = without_project_credit(old_value)
                    self.assertEqual(native_payload(payload_markup(new_node)), expected, iid)
                    changed |= old_value != expected
                    # Compare all other HTML, not just the game data.
                    for node in (old_node, new_node):
                        for child in list(node):
                            node.remove(child)
                        node.text = "VERIFIED_NATIVE_GAME_DATA"
                if changed:
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
        for name, payload in self.baseline.items():
            if Path(name).suffix.lower() in MEDIA:
                with self.subTest(media=name):
                    self.assertEqual(self.files.get(name), payload)

    def test_cover_only_adds_authorship_license_and_two_decorative_rows(self):
        markup = "".join(text_markup(c) for c in page_components(self.pages[COVER]))
        document = fragment(markup)
        text = readable(markup)
        self.assertIn("MitoMapa canario", text)
        for author in AUTHORS:
            self.assertIn(author, text)
        self.assertIn("CC BY-SA 4.0", text)
        for unwanted in ("curricular", "Primaria", "Lengua Castellana", "Conocimiento del Medio", "TongApp", "El Museo Canario", "ImageGen", "Astra", "4.8.0"):
            self.assertNotIn(unwanted.casefold(), text.casefold())
        decorations = document.xpath(".//img[contains(@src,'pintadera')]")
        self.assertEqual(len(decorations), 8)
        self.assertTrue(all(image.get("alt") == "" for image in decorations))
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
                self.assertIn(" ".join(trace.text_content().split()), " ".join(moved[0].text_content().split()))
            if traces:
                self.assertFalse(fragment(text_markup(self.components[iid])).xpath(".//*[@data-source-route]"), iid)

    def test_web_is_only_an_external_extra_at_the_end(self):
        ordered = list(self.pages)
        self.assertEqual(ordered[-1], WEB_EXTRA)
        page = self.pages[WEB_EXTRA]
        self.assertIn("web", field(page, "pageName").casefold())
        markup = "".join(text_markup(c) for c in page_components(page))
        links = fragment(markup).xpath(".//a/@href")
        self.assertTrue(any(url.startswith("https://mitomapa-canario.cgarcias.workers.dev/") for url in links))
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


if __name__ == "__main__":
    unittest.main()
