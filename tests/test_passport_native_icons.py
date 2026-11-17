"""Check the native insignias where the editor and game runtime consume them."""

import json
from pathlib import Path
import sys
import unittest

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from release_support import read_zip
from sync_current_elpx import build_current, field, native_structure


# Independent publication expectations: changing the transform's table must not
# silently change what the saved editor model or the exported games display.
ICONS = (
    ("tenerife", "Tenerife", "TF1RWN", "sol"),
    ("gran_canaria", "Gran Canaria", "TF2UX8", "seis_triangulos"),
    ("la_palma", "La Palma", "TF3PNS", "dentada"),
    ("la_gomera", "La Gomera", "TF4ICZ", "triangulo"),
    ("el_hierro", "El Hierro", "TF58IT", "circulos"),
    ("fuerteventura", "Fuerteventura", "TF6TMM", "doble_triangulo"),
    ("lanzarote", "Lanzarote", "TF7K1Z", "chevron"),
    ("la_graciosa", "La Graciosa", "TF8283", "espiral_cuadrada"),
)
SELECTORS = ("20260823155836TINTRO", "20260823155836TITINW")


def fragment(markup):
    return html.fragment_fromstring(markup, create_parent=True)


class NativePassportIconsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.version = build_current()
        cls.components = native_structure(cls.files)["components"]
        cls.baseline = read_zip((ROOT / cls.version["elpx_source"]["path"]).read_bytes())
        cls.original_components = native_structure(cls.baseline)["components"]
        raw = cls.files["search_index.js"].decode()
        cls.search = json.loads(raw[raw.index("{"):].rstrip(";\n"))
        cls.entries = {
            iid: (page, entry)
            for page in cls.search.values()
            for block in page["blocks"].values()
            for iid, entry in block["idevices"].items()
        }

    def test_eight_rewards_use_approved_images_in_editor_search_and_runtime_json(self):
        for slug, island, suffix, old_name in ICONS:
            iid = "20260823155837" + suffix
            source = "{{context_path}}/content/resources/insignia_" + slug + ".webp"
            alternative = ("Caracola de barro, símbolo contemporáneo de La Graciosa"
                           if slug == "la_graciosa" else "Vasija de barro de " + island)
            props = json.loads(field(self.components[iid], "jsonProperties"))
            page, search = self.entries[iid]
            exported = html.fromstring(self.files[page["fileUrl"]]).xpath("//*[@id=$iid]", iid=iid)[0]
            runtime = json.loads(exported.get("data-idevice-json-data"))
            representations = {
                "editor": (props["eXeIdeviceTextAfter"], source),
                "preview": (field(self.components[iid], "htmlView"), source),
                "search-editor": (json.loads(search["jsonProperties"])["eXeIdeviceTextAfter"], source),
                "search-preview": (search["htmlView"], source.replace("{{context_path}}/", "../")),
                "export": (html.tostring(exported, encoding="unicode"), source.replace("{{context_path}}/", "../")),
                "runtime": (runtime["eXeIdeviceTextAfter"], source.replace("{{context_path}}/", "../")),
            }
            for name, (markup, expected_source) in representations.items():
                with self.subTest(island=island, representation=name):
                    images = fragment(markup).xpath(".//img")
                    self.assertEqual(len(images), 1)
                    self.assertEqual(images[0].get("src"), expected_source)
                    self.assertEqual(images[0].get("alt"), alternative)
                    self.assertEqual((images[0].get("width"), images[0].get("height")), ("180", "180"))
            self.assertEqual(runtime, json.loads(field(self.components[iid], "jsonProperties").replace("{{context_path}}/", "../")))
            self.assertNotIn("pintadera_" + old_name + ".webp", html.tostring(exported, encoding="unicode"))

    def test_selectors_change_only_image_sources(self):
        expected_sources = ["{{context_path}}/content/resources/insignia_" + row[0] + ".webp" for row in ICONS]
        for iid in SELECTORS:
            old = json.loads(field(self.original_components[iid], "jsonProperties"))["textTextarea"]
            current = json.loads(field(self.components[iid], "jsonProperties"))["textTextarea"]
            old_images = fragment(old).xpath(".//a/img")
            images = fragment(current).xpath(".//a/img")
            self.assertEqual(len(images), 8)
            for image, original, expected in zip(images, old_images, expected_sources, strict=True):
                self.assertEqual(image.attrib, {**original.attrib, "src": expected})
                self.assertEqual(image.getparent().get("href"), original.getparent().get("href"))
            page, entry = self.entries[iid]
            exported = html.fromstring(self.files[page["fileUrl"]]).xpath("//*[@id=$iid]", iid=iid)[0]
            self.assertEqual(exported.xpath(".//a/img/@src"), [src.replace("{{context_path}}/", "../") for src in expected_sources])
            self.assertEqual(json.loads(entry["jsonProperties"])["textTextarea"], current)

    def test_new_resources_have_one_native_copy_and_old_media_are_unchanged(self):
        resources = {"content/resources/insignia_" + row[0] + ".webp" for row in ICONS}
        self.assertEqual({name for name in self.files if Path(name).name.startswith("insignia_")}, resources)
        inventory = self.files["libs/elpx-manifest.js"].decode()
        for name in resources:
            self.assertEqual(self.files[name], (ROOT / "assets/images" / Path(name).name).read_bytes())
            self.assertIn(name, inventory)
        for name, payload in self.baseline.items():
            # Only the project's two stored previews are refreshed separately.
            if name in {"screenshot.png", "content/resources/screenshot.png"}:
                continue
            if Path(name).suffix.lower() in {".webp", ".png", ".mp3", ".svg"}:
                self.assertEqual(self.files[name], payload, name)
        cover = json.loads(field(self.components["GBCTPORTADA"], "jsonProperties"))["textTextarea"]
        self.assertEqual(len(fragment(cover).xpath(".//img[contains(@src,'pintadera_')]")), 8)
        self.assertNotIn("insignia_", cover)

    def test_sources_include_shared_credits_without_thumbnails(self):
        credits = (ROOT / "assets/passport_icon_credits.html").read_text()
        self.assertFalse(fragment(credits).xpath(".//img"))
        source = self.components["GBCTFUENTES"]
        markup = json.loads(field(source, "jsonProperties"))["textTextarea"]
        expected = " ".join(fragment(credits).text_content().split())
        self.assertIn(expected, " ".join(fragment(markup).text_content().split()))
        for _, _, _, old_name in ICONS:
            self.assertIn("pintadera_" + old_name + ".webp", markup)


if __name__ == "__main__":
    unittest.main()
