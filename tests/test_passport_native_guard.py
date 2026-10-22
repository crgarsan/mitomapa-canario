"""Permit the reviewed badge artwork while preserving native game behavior."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from native_preservation import field, verify_component


NS = {"o": "http://www.intef.es/xsd/ode"}
RESOURCE = "{{context_path}}/content/resources/"
# Independent review expectations: no imports from the artwork mutator or guard.
BADGES = {
    "20260823155837TF1RWN": ("sol", "Pintadera de la luz", "tenerife", "Vasija de barro de Tenerife"),
    "20260823155837TF2UX8": ("seis_triangulos", "Pintadera de la memoria", "gran_canaria", "Vasija de barro de Gran Canaria"),
    "20260823155837TF3PNS": ("dentada", "Pintadera de Idafe", "la_palma", "Vasija de barro de La Palma"),
    "20260823155837TF4ICZ": ("triangulo", "Pintadera del encuentro", "la_gomera", "Vasija de barro de La Gomera"),
    "20260823155837TF58IT": ("circulos", "Pintadera de la niebla", "el_hierro", "Vasija de barro de El Hierro"),
    "20260823155837TF6TMM": ("doble_triangulo", "Pintadera de Mafasca", "fuerteventura", "Vasija de barro de Fuerteventura"),
    "20260823155837TF7K1Z": ("chevron", "Pintadera de Ico", "lanzarote", "Vasija de barro de Lanzarote"),
    "20260823155837TF8283": ("espiral_cuadrada", "Pintadera del horizonte", "la_graciosa", "Caracola de barro, símbolo contemporáneo de La Graciosa"),
}


def components(path):
    with ZipFile(path) as archive:
        tree = etree.fromstring(archive.read("content.xml"))
    return {field(node, "odeIdeviceId"): node for node in tree.findall(".//o:odeComponent", NS)}


def approved_badge(original):
    current = deepcopy(original)
    old_name, old_alt, slug, new_alt = BADGES[field(original, "odeIdeviceId")]
    old_src = RESOURCE + f"pintadera_{old_name}.webp"
    new_src = RESOURCE + f"insignia_{slug}.webp"
    before = json.loads(field(original, "jsonProperties"))["eXeIdeviceTextAfter"]
    after = before.replace(f'src="{old_src}" alt="{old_alt}"', f'src="{new_src}" alt="{new_alt}"', 1)
    current.find("o:jsonProperties", NS).text = field(original, "jsonProperties").replace(
        json.dumps(before, ensure_ascii=False), json.dumps(after, ensure_ascii=False), 1,
    )
    current.find("o:htmlView", NS).text = field(original, "htmlView").replace(
        f'src="{old_src}" alt="{old_alt}"', f'src="{new_src}" alt="{new_alt}"', 1,
    )
    return current


class PassportNativeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        version = json.loads((ROOT / "VERSION.json").read_text())
        cls.originals = components(ROOT / version["elpx_source"]["path"])
        cls.published = components(ROOT / version["download"]["path"])

    def test_all_eight_reviewed_badge_images_are_accepted(self):
        for iid in BADGES:
            with self.subTest(idevice=iid):
                try:
                    verify_component(self.originals[iid], approved_badge(self.originals[iid]), {})
                except ValueError as error:
                    self.fail(f"The reviewed badge artwork was rejected: {error}")

    def test_questions_solutions_messages_and_settings_remain_protected(self):
        iid = "20260823155837TF1RWN"
        mutations = {
            "question": lambda data: data["questionsGame"][0].update(question="Otra pregunta"),
            "solution": lambda data: data["questionsGame"][0].update(solution=1),
            "feedback": lambda data: data["questionsGame"][0].update(feedback="Otra explicación"),
            "message": lambda data: data["msgs"].update(msgTrue="Otra respuesta"),
            "instructions": lambda data: data.update(eXeGameInstructions="Otras instrucciones"),
            "attempts": lambda data: data.update(attemptsNumber=1),
            "score": lambda data: data.update(weighted=0),
            "evaluation": lambda data: data.update(evaluation=False),
            "time": lambda data: data.update(time=10),
        }
        for label, mutate in mutations.items():
            with self.subTest(change=label):
                current = approved_badge(self.originals[iid])
                data = json.loads(field(current, "jsonProperties"))
                mutate(data)
                current.find("o:jsonProperties", NS).text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
                with self.assertRaises(ValueError):
                    verify_component(self.originals[iid], current, {})

    def test_badge_dimensions_and_unrelated_html_remain_protected(self):
        iid = "20260823155837TF1RWN"
        for before, after in (('width="180"', 'width="181"'), ('Comprobar', 'Comprobar ahora')):
            with self.subTest(change=before):
                current = approved_badge(self.originals[iid])
                current.find("o:htmlView", NS).text = field(current, "htmlView").replace(before, after, 1)
                with self.assertRaises(ValueError):
                    verify_component(self.originals[iid], current, {})

    def test_unreviewed_image_sources_and_alternatives_are_rejected_in_both_fields(self):
        for iid, (_, _, slug, new_alt) in BADGES.items():
            new_src = RESOURCE + f"insignia_{slug}.webp"
            for field_name in ("jsonProperties", "htmlView"):
                for before, after in ((new_src, RESOURCE + "insignia_otra.webp"), (new_alt, "Otro texto alternativo")):
                    with self.subTest(idevice=iid, field=field_name, change=before):
                        current = approved_badge(self.originals[iid])
                        current.find("o:" + field_name, NS).text = field(current, field_name).replace(before, after, 1)
                        with self.assertRaises(ValueError):
                            verify_component(self.originals[iid], current, {})

    def test_component_identity_and_type_remain_protected(self):
        iid = "20260823155837TF1RWN"
        for key, value in (("odeIdeviceId", "unreviewed-id"), ("odeIdeviceTypeName", "text"), ("odePageId", "other-page")):
            with self.subTest(field=key):
                current = approved_badge(self.originals[iid])
                current.find("o:" + key, NS).text = value
                with self.assertRaises(ValueError):
                    verify_component(self.originals[iid], current, {})

    def test_passport_checklist_exception_still_allows_only_its_licence_footer(self):
        iid = "20260823155836CHKPAS"
        original = self.originals[iid]
        current = deepcopy(self.published[iid])
        verify_component(original, current, {})
        new_image = '<img src="' + RESOURCE + 'insignia_tenerife.webp" alt="Vasija de barro de Tenerife">'
        current.find("o:htmlView", NS).text = field(current, "htmlView").replace("</div>", new_image + "</div>", 1)
        with self.assertRaises(ValueError):
            verify_component(original, current, {})


if __name__ == "__main__":
    unittest.main()
