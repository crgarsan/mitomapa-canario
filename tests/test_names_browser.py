"""Exercise the optional island-name map in real Chromium.

These checks cover interaction, accessibility and preservation of the supplied
map geometry. They do not establish historical certainty or classroom efficacy.
Only the local resource is served; no public site is used or changed.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import threading
import unittest

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CSP = next(
    line.split(":", 1)[1].strip()
    for line in (ROOT / "_headers").read_text().splitlines()
    if line.strip().startswith("Content-Security-Policy:")
)
ISLANDS = {
    "el-hierro": (15.3, 74.8),
    "la-palma": (18, 41.7),
    "la-gomera": (28.1, 61),
    "tenerife": (38.9, 54.9),
    "gran-canaria": (53.6, 66.9),
    "fuerteventura": (76.7, 51.5),
    "lanzarote": (84.3, 28.3),
    "la-graciosa": (85.7, 21.5),
}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class NamesBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=shutil.which("chromium"),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 1800}, has_touch=True
        )
        self.context.add_init_script("window.confirm=()=>true")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base + "#nombres-islas", wait_until="networkidle")
        expect(self.page.locator("#namesMapGame")).to_be_visible()

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def card(self, island):
        return self.page.locator(f'[data-name-card="{island}"]')

    def island(self, island):
        return self.page.locator(f'[data-name-island="{island}"]')

    def place(self, name, island=None):
        self.card(name).click()
        self.island(island or name).click()

    def placed_count(self):
        return self.page.locator('[data-name-island][data-placed="true"]').count()

    def assert_empty(self):
        self.assertEqual(self.placed_count(), 0)
        self.assertEqual(
            self.page.locator('[data-name-island][data-reference="true"]').count(), 0
        )
        self.assertEqual(
            self.page.locator('[data-name-card][aria-pressed="true"]').count(), 0
        )

    def storage(self):
        return self.page.evaluate("()=>({...localStorage})")

    def start_mouse_drag(self, island):
        card = self.card(island)
        card.scroll_into_view_if_needed()
        box = card.bounding_box()
        start = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        self.page.mouse.move(*start)
        self.page.mouse.down()
        self.page.mouse.move(start[0] + 20, start[1] + 20, steps=3)
        expect(self.page.locator(".names-drag-ghost")).to_be_visible()
        return start

    def test_juegos_entry_and_deep_link_are_open_without_pintaderas(self):
        expect(self.page.locator('[data-nav="juegos"]')).to_have_attribute(
            "aria-current", "page"
        )
        expect(self.page.locator("#namesMapTitle")).to_be_visible()
        self.assertEqual(self.page.locator("[data-name-card]").count(), 8)
        self.assertEqual(self.page.locator("[data-name-island]").count(), 8)
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.page.locator('#namesMapGame a[href="#juegos"]').click()
        expect(self.page.locator("#namesMapGame")).to_be_hidden()
        entry = self.page.locator('[data-screen="juegos"] a[href="#nombres-islas"]')
        expect(entry).to_be_visible()
        entry.click()
        expect(self.page.locator("#namesMapGame")).to_be_visible()
        self.assertEqual(self.page.url, self.base + "#nombres-islas")
        self.page.reload(wait_until="networkidle")
        expect(self.page.locator("#namesMapGame")).to_be_visible()
        expect(self.page.locator("#namesMapTitle")).to_be_focused()

    def test_wrong_attempt_retry_and_completion_do_not_award_or_persist(self):
        before = self.storage()
        self.place("tenerife", "el-hierro")
        self.assertEqual(self.placed_count(), 0)
        self.assertTrue(self.page.locator("#namesFeedback").text_content().strip())
        self.island("tenerife").click()
        expect(self.island("tenerife")).to_have_attribute("data-placed", "true")
        for island in ISLANDS:
            if island != "tenerife":
                self.place(island)
        self.assertEqual(self.placed_count(), 8)
        expect(self.page.locator("#namesProgress")).to_contain_text(
            re.compile(r"(?:ocho|8) fichas")
        )
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.assertEqual(self.page.locator(".reward.show").count(), 0)
        self.assertEqual(self.storage(), before)
        self.page.reload(wait_until="networkidle")
        self.assert_empty()

    def test_reference_is_distinct_from_personal_attempts_and_reset(self):
        self.place("tenerife")
        self.page.locator("#namesReference").click()
        self.assertEqual(self.placed_count(), 1)
        self.assertGreaterEqual(
            self.page.locator('[data-name-island][data-reference="true"]').count(), 7
        )
        expect(self.page.locator("#namesFeedback")).to_contain_text(
            re.compile("referencia", re.IGNORECASE)
        )
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.page.locator("#namesReset").click()
        self.assert_empty()
        self.place("la-graciosa")
        expect(self.island("la-graciosa")).to_have_attribute("data-placed", "true")

    def test_keyboard_and_select_alternative_need_no_dragging(self):
        card = self.card("tenerife")
        card.focus()
        card.press("Space")
        expect(card).to_have_attribute("aria-pressed", "true")
        expect(card).to_be_focused()
        self.page.locator("#namesHint").click()
        expect(self.page.locator("#namesFeedback")).to_have_attribute("data-kind", "hint")
        self.assertEqual(self.placed_count(), 0)
        card.focus()
        card.press("Escape")
        expect(card).to_have_attribute("aria-pressed", "false")
        card.press("Enter")
        target = self.island("tenerife")
        self.page.locator("#namesShowCurrent").uncheck()
        # Hiding the visual help must keep every destination identifiable to AT.
        expect(target).to_have_attribute("aria-label", re.compile("Tenerife"))
        target.focus()
        target.press("Space")
        expect(target).to_have_attribute("data-placed", "true")
        expect(target).to_be_focused()

        select = self.page.locator("#namesNameSelect")
        disclosure = select.locator("xpath=ancestor::details[1]")
        summary = disclosure.locator(":scope > summary")
        summary.focus()
        summary.press("Enter")
        expect(select).to_be_visible()
        select.focus()
        select.select_option("lanzarote")
        self.page.locator("#namesIslandSelect").select_option("lanzarote")
        button = self.page.locator("#namesPlaceButton")
        button.focus()
        button.press("Enter")
        expect(self.island("lanzarote")).to_have_attribute("data-placed", "true")
        self.assertEqual(self.placed_count(), 2)

    def test_real_mouse_drag_and_cancel_on_reset_or_navigation(self):
        self.start_mouse_drag("tenerife")
        target = self.island("tenerife").bounding_box()
        self.page.mouse.move(
            target["x"] + target["width"] / 2,
            target["y"] + target["height"] / 2,
            steps=12,
        )
        self.page.mouse.up()
        expect(self.island("tenerife")).to_have_attribute("data-placed", "true")
        expect(self.page.locator(".names-drag-ghost")).to_have_count(0)
        self.page.locator("#namesReset").click()
        self.start_mouse_drag("la-palma")
        self.page.evaluate("window.MitoMapaNames.reset()")
        expect(self.page.locator(".names-drag-ghost")).to_have_count(0)
        self.page.mouse.up()
        self.assert_empty()
        self.start_mouse_drag("la-gomera")
        self.page.evaluate("location.hash='#juegos'")
        expect(self.page.locator("#namesMapGame")).to_be_hidden()
        expect(self.page.locator(".names-drag-ghost")).to_have_count(0)
        self.page.mouse.up()
        self.page.locator('[data-screen="juegos"] a[href="#nombres-islas"]').click()
        self.assertEqual(self.placed_count(), 0)

    def test_real_touch_drag_places_a_name(self):
        self.card("tenerife").scroll_into_view_if_needed()
        card = self.card("tenerife").bounding_box()
        target = self.island("tenerife").bounding_box()
        start = {"x": card["x"] + card["width"] / 2,
                 "y": card["y"] + card["height"] / 2}
        end = {"x": target["x"] + target["width"] / 2,
               "y": target["y"] + target["height"] / 2}
        session = self.context.new_cdp_session(self.page)
        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [start]})
        for step in range(1, 9):
            point = {key: start[key] + (end[key] - start[key]) * step / 8 for key in start}
            session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [point]})
        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        expect(self.island("tenerife")).to_have_attribute("data-placed", "true")
        session.detach()

    def test_global_reset_and_import_clear_the_previous_learners_practice(self):
        self.place("tenerife")
        self.page.locator("#openTeacher").click()
        self.page.locator("#teacherToolsTab").click()
        self.page.locator("#resetProgress").click()
        self.assert_empty()
        self.page.locator("#closeTeacher").click()
        self.place("la-palma")
        self.page.locator("#namesReference").click()
        self.page.locator("#importProgressFile").set_input_files({
            "name": "seguimiento.json", "mimeType": "application/json",
            "buffer": json.dumps({
                "app": "mitomapa-canario", "version": "4.4.2",
                "learningLevel": "middle", "learnerName": "Otra persona",
                "progress": {"sourcePassed": [], "truthPassed": [], "earned": []},
            }).encode(),
        })
        self.page.wait_for_function("""()=>document.getElementById('teacherImportStatus')
            .textContent.includes('correctamente')""")
        self.assert_empty()
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")

    def test_map_geometry_and_targets_survive_mobile_reflow(self):
        for width in [320, 390, 1280]:
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": 1000})
                self.page.reload(wait_until="networkidle")
                geometry = self.page.locator("#namesMapImage").evaluate("""svg=>{
                    const box=svg.getBoundingClientRect(),view=svg.viewBox.baseVal;
                    const image=svg.querySelector('image');
                    return {width:box.width,height:box.height,viewWidth:view.width,
                        viewHeight:view.height,href:image.getAttribute('href'),
                        imageWidth:Number(image.getAttribute('width')),
                        imageHeight:Number(image.getAttribute('height')),
                        anchors:[...svg.querySelectorAll('[data-name-anchor]')].map(n=>({
                            id:n.dataset.nameAnchor,x:Number(n.getAttribute('cx')),
                            y:Number(n.getAttribute('cy'))}))};
                }""")
                self.assertEqual((geometry["viewWidth"], geometry["viewHeight"]), (3000, 1514))
                self.assertEqual((geometry["imageWidth"], geometry["imageHeight"]), (3000, 1514))
                self.assertTrue(geometry["href"].endswith("assets/images/mapa_canarias.webp"))
                self.assertAlmostEqual(geometry["width"] / geometry["height"], 3000 / 1514, places=3)
                self.assertEqual(len(geometry["anchors"]), 8)
                for anchor in geometry["anchors"]:
                    expected = ISLANDS[anchor["id"]]
                    self.assertAlmostEqual(anchor["x"] / 30, expected[0], places=2)
                    self.assertAlmostEqual(anchor["y"] / 15.14, expected[1], places=2)

                # Revealed names include longer labels than the initial targets.
                # They must fit the same cartelas without colliding.
                self.page.locator("#namesReference").click()
                boxes = []
                for target in self.page.locator("[data-name-island]").all():
                    box = target.bounding_box()
                    self.assertGreaterEqual(box["width"], 44)
                    self.assertGreaterEqual(box["height"], 44)
                    boxes.append(box)
                for index, first in enumerate(boxes):
                    for second in boxes[index + 1:]:
                        overlap_x = min(first["x"] + first["width"], second["x"] + second["width"]) - max(first["x"], second["x"])
                        overlap_y = min(first["y"] + first["height"], second["y"] + second["height"]) - max(first["y"], second["y"])
                        self.assertTrue(overlap_x <= 0 or overlap_y <= 0, (first, second))
                dimensions = self.page.evaluate("""()=>({
                    page:document.documentElement.scrollWidth,viewport:innerWidth,
                    map:document.getElementById('namesMapViewport').scrollWidth,
                    available:document.getElementById('namesMapViewport').clientWidth})""")
                self.assertLessEqual(dimensions["page"], dimensions["viewport"] + 1)
                if dimensions["map"] > dimensions["available"]:
                    viewport = self.page.locator("#namesMapViewport")
                    self.assertEqual(viewport.get_attribute("tabindex"), "0")
                    self.assertEqual(viewport.get_attribute("role"), "region")
                    self.assertTrue(viewport.get_attribute("aria-label"))
                    self.assertIn(viewport.evaluate("node=>getComputedStyle(node).overflowX"), ["auto", "scroll"])


if __name__ == "__main__":
    unittest.main()
