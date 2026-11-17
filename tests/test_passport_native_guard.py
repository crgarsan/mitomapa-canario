"""Permit the reviewed badge artwork while preserving native game behavior."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from editorial_elpx import encode_native_payload
from native_preservation import field, game_payloads, verify_component


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
PASSPORT = "20260823155836CHKPAS"
FINAL_CHECKLIST = "20260823155837CHKFIN"
CREATION_CHECKLISTS = tuple(f"20260823155837CHKCR{index}" for index in range(1, 9))


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
    old_label = f"<strong>{old_alt}</strong>"
    new_label = f'<strong>{old_alt.replace("Pintadera", "Pieza", 1)}</strong>'
    after = after.replace(old_label, new_label, 1)
    current.find("o:jsonProperties", NS).text = field(original, "jsonProperties").replace(
        json.dumps(before, ensure_ascii=False), json.dumps(after, ensure_ascii=False), 1,
    )
    current.find("o:htmlView", NS).text = field(original, "htmlView").replace(
        f'src="{old_src}" alt="{old_alt}"', f'src="{new_src}" alt="{new_alt}"', 1,
    ).replace(old_label, new_label, 1)
    return current


def with_payload(original, payload):
    current = deepcopy(original)
    view = field(original, "htmlView")
    document = html.fragment_fromstring(view, create_parent=True)
    nodes = document.xpath(".//div[contains(@class, 'DataGame')]")
    if len(nodes) != 1:
        raise AssertionError("The native test fixture must contain one game payload")
    encoded = nodes[0].text_content()
    replacement = encode_native_payload(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    current.find("o:htmlView", NS).text = view.replace(encoded, replacement, 1)
    return current


def approved_checklist(original):
    payloads, _ = game_payloads(field(original, "htmlView"))
    data = deepcopy(payloads[0])
    iid = field(original, "odeIdeviceId")
    data["msgs"]["msgList"] = "pasaporte de piezas"
    if iid == PASSPORT:
        data["footer"] = "MitoMapa canario · CC BY-SA 4.0"
        data["title"] = "Pasaporte de piezas"
        data["levels"][0]["item"] = "Pasaporte de piezas"
        for level in data["levels"][1:]:
            level["item"] = level["item"].replace("Pintadera", "Pieza", 1)
    elif iid == FINAL_CHECKLIST:
        data["title"] = "Revisión del museo de piezas"
        data["levels"][0]["item"] = "Revisión del museo de piezas"
    elif iid not in CREATION_CHECKLISTS:
        raise AssertionError("The test helper must only update reviewed checklists")
    return with_payload(original, data)


class PassportNativeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        version = json.loads((ROOT / "VERSION.json").read_text())
        cls.originals = components(ROOT / version["elpx_source"]["path"])

    def test_all_eight_reviewed_badge_images_are_accepted(self):
        for iid in BADGES:
            with self.subTest(idevice=iid):
                try:
                    verify_component(self.originals[iid], approved_badge(self.originals[iid]), {})
                except ValueError as error:
                    self.fail(f"The reviewed badge artwork was rejected: {error}")

    def test_only_the_exact_reviewed_reward_label_is_accepted(self):
        for iid, (_, old_alt, _, _) in BADGES.items():
            new_label = f'<strong>{old_alt.replace("Pintadera", "Pieza", 1)}</strong>'
            for field_name in ("jsonProperties", "htmlView"):
                with self.subTest(idevice=iid, field=field_name):
                    current = approved_badge(self.originals[iid])
                    current.find("o:" + field_name, NS).text = field(current, field_name).replace(
                        new_label, "<strong>Otra pieza</strong>", 1,
                    )
                    with self.assertRaises(ValueError):
                        verify_component(self.originals[iid], current, {})

    def test_reviewed_piece_names_are_accepted_in_all_ten_checklists(self):
        for iid in (PASSPORT, FINAL_CHECKLIST, *CREATION_CHECKLISTS):
            with self.subTest(idevice=iid):
                try:
                    verify_component(self.originals[iid], approved_checklist(self.originals[iid]), {})
                except ValueError as error:
                    self.fail(f"The reviewed checklist labels were rejected: {error}")

    def test_checklist_academic_criteria_levels_scoring_and_other_messages_are_preserved(self):
        mutations = {
            "academic item": lambda data: data["levels"][1].update(item="Otro criterio académico"),
            "level type": lambda data: data["levels"][1].update(type="99"),
            "level depth": lambda data: data["levels"][1].update(nivel="2"),
            "points": lambda data: data["levels"][1].update(points="1"),
            "score": lambda data: data.update(useScore=True),
            "save setting": lambda data: data.update(saveData=False),
            "other message": lambda data: data["msgs"].update(msgDelete="¿Borrar?"),
            "subtitle": lambda data: data.update(subtitle="Otra instrucción"),
            "unreviewed title": lambda data: data.update(title="Otro título"),
            "footer": lambda data: data.update(footer="Otro pie"),
        }
        for iid in (PASSPORT, FINAL_CHECKLIST, *CREATION_CHECKLISTS):
            approved = approved_checklist(self.originals[iid])
            approved_payload, _ = game_payloads(field(approved, "htmlView"))
            for label, mutate in mutations.items():
                with self.subTest(idevice=iid, change=label):
                    data = deepcopy(approved_payload[0])
                    mutate(data)
                    with self.assertRaises(ValueError):
                        verify_component(self.originals[iid], with_payload(approved, data), {})

    def test_factual_pintadera_answer_in_fuerteventura_stays_unchanged(self):
        iid = "20260823155837QC6OQI"
        original = self.originals[iid]
        payloads, _ = game_payloads(field(original, "htmlView"))
        data = deepcopy(payloads[0])
        data["author"] = ""
        for question in data["questionsGame"]:
            question["author"] = ""
        self.assertEqual(data["questionsGame"][0]["options"][3], "Una pintadera")
        verify_component(original, with_payload(original, data), {})
        data["questionsGame"][0]["options"][3] = "Una pieza"
        with self.assertRaises(ValueError):
            verify_component(original, with_payload(original, data), {})

    def test_download_component_accepts_only_the_reviewed_project_title(self):
        iid = "20260930IDESCARGA40"
        original = self.originals[iid]
        current = deepcopy(original)
        current.find("o:htmlView", NS).text = field(original, "htmlView").replace(
            "MitoMapa canario: ocho islas, ocho pintaderas",
            "MitoMapa canario: ocho islas, ocho piezas", 1,
        )
        try:
            verify_component(original, current, {})
        except ValueError as error:
            self.fail(f"The reviewed download title was rejected: {error}")
        for before, after in (
            ('href="exe-package:elp"', 'href="otro.elpx"'),
            ("Descargar el archivo .elpx", "Descargar otro archivo"),
            ("Información general sobre este recurso educativo", "Otra información"),
        ):
            with self.subTest(change=before):
                invalid = deepcopy(current)
                invalid.find("o:htmlView", NS).text = field(invalid, "htmlView").replace(before, after, 1)
                with self.assertRaises(ValueError):
                    verify_component(original, invalid, {})

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

    def test_passport_checklist_label_exception_does_not_allow_images(self):
        iid = PASSPORT
        original = self.originals[iid]
        current = approved_checklist(original)
        new_image = '<img src="' + RESOURCE + 'insignia_tenerife.webp" alt="Vasija de barro de Tenerife">'
        current.find("o:htmlView", NS).text = field(current, "htmlView").replace("</div>", new_image + "</div>", 1)
        with self.assertRaises(ValueError):
            verify_component(original, current, {})


if __name__ == "__main__":
    unittest.main()
