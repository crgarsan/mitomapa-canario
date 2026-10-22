"""Keep collection labels distinct from archaeological content and game rules."""

from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from native_preservation import field, game_payloads
from release_support import read_zip
from sync_current_elpx import build_current, native_structure

NS = {"o": "http://www.intef.es/xsd/ode"}
STORIES = ("20260823155836ST1CG9", "20260823155837ST28I4", "20260823155837ST3GFP", "20260823155837ST48OR", "20260823155837ST577Q", "20260823155837ST6CHF", "20260823155837ST7CGH", "20260823155837ST8IN6")
TF = tuple("20260823155837" + suffix for suffix in ("TF1RWN", "TF2UX8", "TF3PNS", "TF4ICZ", "TF58IT", "TF6TMM", "TF7K1Z", "TF8283"))
CHECKLISTS = ("20260823155836CHKPAS", *("20260823155837CHKCR" + str(i) for i in range(1, 9)), "20260823155837CHKFIN")
FUNCTIONAL_TEXTS = ("GBCTPORTADA", "20260823155836TINTRO", "20260823155836TITINW", "20260823155836TPASSI", *STORIES, "20260823155837TFINTI", "20260930IRUBRICA40", "20260823155837TGUID1", "20260929TIMAGEN39", "20260823155837TCRED0")
INFOGRAPHIC = "https://www3.gobiernodecanarias.org/medusa/ecoescuela/recursosdigitales/files/formidable/6/cd-03-0000079-infografia-simple-doble-formato-historia-tipos-de-ceramica-por-isla.pdf"


class NativeCollectionCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.version = build_current()
        cls.components = native_structure(cls.files)["components"]
        cls.baseline = read_zip((ROOT / cls.version["elpx_source"]["path"]).read_bytes())
        cls.original = native_structure(cls.baseline)["components"]
        cls.tree = etree.fromstring(cls.files["content.xml"])
        raw = cls.files["search_index.js"].decode()
        cls.search = json.loads(raw[raw.index("{"):].rstrip(";\n"))
        cls.entries = {iid: (page, entry) for page in cls.search.values() for block in page["blocks"].values() for iid, entry in block["idevices"].items()}

    def test_functional_text_navigation_and_project_name_use_pieces(self):
        title = self.tree.findtext(".//o:odeProperty[o:key='pp_title']/o:value", namespaces=NS)
        self.assertEqual(title, "MitoMapa canario: ocho islas, ocho piezas")
        manifest = self.files["libs/elpx-manifest.js"].decode().split("window.__ELPX_MANIFEST__=", 1)[1].rstrip(";\n")
        self.assertEqual(json.loads(manifest)["projectTitle"], title)
        for page in self.search.values():
            export = html.fromstring(self.files[page["fileUrl"]])
            for heading in export.xpath("//p[@class='package-title']"):
                self.assertEqual(heading.text_content(), title)
        for iid in FUNCTIONAL_TEXTS:
            markup = json.loads(field(self.components[iid], "jsonProperties"))["textTextarea"]
            with self.subTest(component=iid):
                self.assertNotRegex(html.fragment_fromstring(markup, create_parent=True).text_content(), r"(?i)\bpintaderas?\b")
        for tag in ("pageName", "blockName"):
            for node in self.tree.findall(".//o:" + tag, NS):
                self.assertNotRegex(node.text or "", r"(?i)\bpintaderas?\b")

    def test_reward_labels_change_without_changing_questions_or_rules(self):
        for iid in TF:
            before = json.loads(field(self.original[iid], "jsonProperties"))
            after = json.loads(field(self.components[iid], "jsonProperties"))
            with self.subTest(component=iid):
                self.assertNotRegex(html.fragment_fromstring(after["eXeIdeviceTextAfter"], create_parent=True).text_content(), r"(?i)\bpintaderas?\b")
                self.assertIn("Pieza", after["eXeIdeviceTextAfter"])
                before.pop("eXeIdeviceTextAfter")
                after.pop("eXeIdeviceTextAfter")
                self.assertEqual(before, after)

    def test_checklist_changes_are_limited_to_exact_collection_labels(self):
        for iid in CHECKLISTS:
            before = game_payloads(field(self.original[iid], "htmlView"))[0][0]
            after = game_payloads(field(self.components[iid], "htmlView"))[0][0]
            expected = deepcopy(before)
            expected["msgs"]["msgList"] = "pasaporte de piezas"
            if iid == "20260823155836CHKPAS":
                expected["footer"] = "MitoMapa canario · CC BY-SA 4.0"
                expected["title"] = "Pasaporte de piezas"
                expected["levels"][0]["item"] = "Pasaporte de piezas"
                for row in expected["levels"][1:]:
                    row["item"] = row["item"].replace("Pintadera", "Pieza")
            elif iid == "20260823155837CHKFIN":
                expected["title"] = "Revisión del museo de piezas"
                expected["levels"][0]["item"] = "Revisión del museo de piezas"
            with self.subTest(component=iid):
                self.assertEqual(after, expected)

    def test_editor_search_export_and_game_runtime_use_the_same_labels(self):
        for iid in (*TF, *CHECKLISTS):
            component = self.components[iid]
            page, entry = self.entries[iid]
            export = html.fromstring(self.files[page["fileUrl"]]).xpath("//*[@id=$iid]", iid=iid)[0]
            if iid in TF:
                props = json.loads(field(component, "jsonProperties"))
                runtime = json.loads(export.get("data-idevice-json-data"))
                self.assertEqual(runtime, json.loads(field(component, "jsonProperties").replace("{{context_path}}/", "../")))
                self.assertEqual(entry["jsonProperties"], field(component, "jsonProperties"))
                self.assertIn("Pieza", props["eXeIdeviceTextAfter"])
            else:
                expected = game_payloads(field(component, "htmlView"))[0]
                self.assertEqual(game_payloads(entry["htmlView"])[0], expected)
                self.assertEqual(game_payloads(html.tostring(export, encoding="unicode"))[0], expected)

    def test_no_functional_mentions_remain_in_other_native_views_or_attachments(self):
        # The source download iDevice renders the project title outside JSON.
        # Inspect static HTML as well as the editor text and hidden game data.
        legitimate = {"GBCTFUENTES", "20260929THISTORIAL39", "20260823155837QC6OQI"}
        for iid, component in self.components.items():
            if iid in legitimate:
                continue
            _, view = game_payloads(field(component, "htmlView"))
            with self.subTest(component=iid):
                self.assertNotRegex(html.fragment_fromstring(view or "<div></div>", create_parent=True).text_content(), r"(?i)\bpintaderas?\b")
        for name, payload in self.files.items():
            if name.startswith("content/resources/") and name.endswith(".html"):
                with self.subTest(attachment=name):
                    self.assertNotRegex(html.fromstring(payload).text_content(), r"(?i)\bpintaderas?\b")

    def test_archaeological_sources_factual_option_and_media_keep_their_names(self):
        original = game_payloads(field(self.original["20260823155837QC6OQI"], "htmlView"))[0][0]
        current = game_payloads(field(self.components["20260823155837QC6OQI"], "htmlView"))[0][0]
        expected_questions = deepcopy(original["questionsGame"])
        for question in expected_questions:
            if question.get("author") == "Jesica Fortes Regalado; Gloria Elsa González Martín; Cristian García Santana":
                question["author"] = ""
        self.assertEqual(current["questionsGame"], expected_questions)
        self.assertEqual(current["questionsGame"][0]["options"][3], "Una pintadera")
        source = json.loads(field(self.components["GBCTFUENTES"], "jsonProperties"))["textTextarea"]
        document = html.fragment_fromstring(source, create_parent=True)
        self.assertIn("El Museo Canario", document.text_content())
        self.assertIn("[Documento sobre pintaderas]", document.text_content())
        self.assertIn("Las pintaderas originales se conservan como elementos decorativos.", document.text_content())
        resources = document.xpath(".//details[@id='ceramica-pasaporte']")
        self.assertEqual(len(resources), 1)
        self.assertEqual(len(document.xpath(".//*[@id='ceramica-pasaporte']")), 1)
        self.assertIn(INFOGRAPHIC, resources[0].xpath(".//a/@href"))
        for name, payload in self.baseline.items():
            if Path(name).suffix.lower() in {".webp", ".png", ".mp3", ".svg"}:
                self.assertEqual(self.files[name], payload, name)


if __name__ == "__main__":
    unittest.main()
