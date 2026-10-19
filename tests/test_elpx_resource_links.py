"""Catch native resource links that the eXe importer reads as missing files."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import unittest
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent.parent
NAMESPACE = {"o": "http://www.intef.es/xsd/ode"}
RESOURCE_PREFIX = "{{context_path}}/content/resources/"


class ResourceLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src", "poster") and value and value.startswith(RESOURCE_PREFIX):
                self.links.append(value)


class ElpxResourceLinkTests(unittest.TestCase):
    def test_native_editable_and_preview_links_are_importable(self):
        with zipfile.ZipFile(ROOT / "downloads/MitoMapa_canario_GobCan.elpx") as archive:
            names = set(archive.namelist())
            root = ET.fromstring(archive.read("content.xml"))
            checked = 0
            for component in root.findall(".//o:odeComponent", NAMESPACE):
                identifier = component.findtext("o:odeIdeviceId", namespaces=NAMESPACE)
                preview = component.findtext("o:htmlView", default="", namespaces=NAMESPACE)
                properties = component.findtext("o:jsonProperties", default="{}", namespaces=NAMESPACE)
                editable = json.loads(properties or "{}").get("textTextarea", "")
                for representation, markup in (("preview", preview), ("editable", editable)):
                    parser = ResourceLinks()
                    parser.feed(markup)
                    for reference in parser.links:
                        with self.subTest(idevice=identifier, representation=representation, reference=reference):
                            # The legacy resource collector includes #fragment in
                            # its filename lookup; resolve routing in a real HTML
                            # entry point instead of an iDevice resource URL.
                            self.assertNotIn("#", reference, "eXe treats this fragment as part of the filename")
                            self.assertNotIn("?", reference, "Native resource filenames must not contain queries")
                            relative = reference.removeprefix("{{context_path}}/")
                            self.assertIn(unquote(urlsplit(relative).path), names)
                            checked += 1
            self.assertGreater(checked, 50, "The test must inspect the real resource links")


if __name__ == "__main__":
    unittest.main()
