"""Choose the same eight open routes through the map or its existing list.

Runs the resource with its real CSP and Chromium, including small viewports.
The list hook may be called explicitly while navigation is being integrated.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
import threading
import unittest

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSP = next(line.split(":", 1)[1].strip() for line in (ROOT / "_headers").read_text().splitlines() if line.strip().startswith("Content-Security-Policy:"))
ROUTES = ("tenerife", "gran-canaria", "la-palma", "la-gomera", "el-hierro", "fuerteventura", "lanzarote", "la-graciosa")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class MapChoiceBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=shutil.which("chromium"), args=["--no-sandbox", "--disable-dev-shm-usage"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 1000}, reduced_motion="reduce")
        self.context.add_init_script("Math.random=()=>.999; window.confirm=()=>true")
        self.page = self.context.new_page()
        self.page.set_default_timeout(10000)
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open_islands(self, width=1280):
        self.page.set_viewport_size({"width": width, "height": 1000})
        # Hash navigation alone preserves the previous document and text size.
        self.page.goto("about:blank")
        self.page.goto(self.base + "#islas", wait_until="networkidle")
        self.page.evaluate("""() => {
          window.__originalIslandGrid=document.getElementById('islandGrid');
          const details=window.__originalIslandGrid.closest('details');
          window.MitoMapaExplorer.attachList?.(details);
        }""")

    def view(self, name):
        return self.page.get_by_role("button", name=name, exact=True)

    def test_mobile_starts_with_existing_eight_cards_and_reading_questions(self):
        self.open_islands(390)
        expect(self.view("Lista")).to_have_attribute("aria-pressed", "true")
        expect(self.view("Mapa")).to_have_attribute("aria-pressed", "false")
        expect(self.page.locator(".explore-map-viewport")).to_be_hidden()
        cards = self.page.locator("#islandGrid [data-route]")
        expect(cards).to_have_count(8)
        self.assertEqual(set(cards.evaluate_all("nodes=>nodes.map(n=>n.dataset.route)")), set(ROUTES))
        for card in cards.all():
            expect(card).to_be_visible()
            expect(card.locator(".explore-card-question")).to_contain_text("¿")
            self.assertTrue(card.locator(".card-body > span").first.text_content())
            self.assertTrue(card.is_enabled())
        self.assertTrue(self.page.evaluate("document.querySelector('.explore-view-switch').compareDocumentPosition(document.querySelector('#islandGrid')) & Node.DOCUMENT_POSITION_FOLLOWING"))
        self.page.evaluate("window.MitoMapaExplorer.attachList(document.querySelector('#islandGrid').closest('details'))")
        self.assertTrue(self.page.evaluate("window.__originalIslandGrid===document.getElementById('islandGrid')"))
        expect(self.page.locator("#islandGrid")).to_have_count(1)
        expect(self.page.locator(".explore-card-question")).to_have_count(8)

    def test_map_and_list_open_every_route_without_an_order_or_rewards(self):
        self.open_islands()
        expect(self.view("Mapa")).to_have_attribute("aria-pressed", "true")
        for view_name, selector in (("Mapa", ".explore-pin"), ("Lista", "#islandGrid [data-route]")):
            for route_id in reversed(ROUTES):
                self.page.evaluate("location.hash='#islas'")
                expect(self.page.locator("#exploreMap")).to_be_visible()
                self.view(view_name).click()
                choice = self.page.locator(f'{selector}[data-route="{route_id}"]')
                choice.focus()
                choice.press("Enter")
                expect(self.page.locator(f"#route-{route_id}")).to_be_visible()
                self.assertEqual(self.page.url, self.base + f"#isla/{route_id}/cuento")
                expect(self.page.locator("#passportCount")).to_have_text("0/8")

    def test_refresh_enriches_rebuilt_cards_and_keeps_game_answer_capture(self):
        self.open_islands(390)
        # Importing progress reconstructs these cards through the real renderer.
        self.page.evaluate("renderRoutes(); window.MitoMapaExplorer.refresh()")
        expect(self.page.locator("#islandGrid .explore-card-question")).to_have_count(8)
        self.page.evaluate("window.MitoMapaExplorer.refresh(); window.MitoMapaExplorer.refresh()")
        expect(self.page.locator("#islandGrid .explore-card-question")).to_have_count(8)
        self.page.get_by_role("button", name="Jugar con cinco pistas", exact=True).click()
        self.page.locator('#islandGrid [data-route="tenerife"]').click()
        expect(self.page.locator(".explore-feedback")).to_have_attribute("data-kind", "success")
        self.assertEqual(self.page.url, self.base + "#islas")

    def test_view_changes_keep_one_five_clue_game_and_list_answers_do_not_navigate(self):
        self.open_islands(390)
        before = self.page.evaluate("()=>({...localStorage})")
        self.page.get_by_role("button", name="Jugar con cinco pistas", exact=True).click()
        expect(self.page.locator("#exploreClue")).to_be_focused()
        expect(self.page.locator(".explore-counter")).to_have_text("Pista 1 de 5")
        self.page.locator('#islandGrid [data-route="gran-canaria"]').click()
        expect(self.page.locator(".explore-feedback")).to_have_attribute("data-kind", "retry")
        self.assertEqual(self.page.url, self.base + "#islas")
        self.page.get_by_role("button", name="Dame una pista de apoyo", exact=True).click()
        expect(self.page.locator("#exploreHint")).to_be_visible()
        switch = self.view("Mapa")
        switch.focus()
        switch.press("Enter")
        expect(switch).to_be_focused()
        self.page.locator('.explore-pin[data-route="tenerife"]').click()
        expect(self.page.locator(".explore-feedback")).to_have_attribute("data-kind", "success")
        self.view("Lista").click()
        expect(self.page.locator("#exploreHint")).to_be_visible()
        expect(self.page.locator(".explore-counter")).to_have_text("Pista 1 de 5")
        expect(self.page.locator('#islandGrid [data-route="tenerife"]')).to_have_class(re.compile("explore-card-found"))
        self.page.get_by_role("button", name="Siguiente pista", exact=True).click()
        for index, route_id in enumerate(ROUTES[1:5], start=2):
            expect(self.page.locator(".explore-counter")).to_have_text(f"Pista {index} de 5")
            self.page.locator(f'#islandGrid [data-route="{route_id}"]').click()
            expect(self.page.locator(".explore-feedback")).to_have_attribute("data-kind", "success")
            self.page.get_by_role("button", name="Terminar expedición" if index == 5 else "Siguiente pista", exact=True).click()
        expect(self.page.locator(".explore-counter")).to_contain_text("5 pistas completada")
        expect(self.page.locator("#passportCount")).to_have_text("0/8")
        self.assertEqual(self.page.evaluate("()=>({...localStorage})"), before)
        self.page.evaluate("window.MitoMapaExplorer.reset()")
        expect(self.page.locator(".explore-game")).to_be_hidden()
        self.page.locator('#islandGrid [data-route="la-graciosa"]').click()
        expect(self.page.locator("#route-la-graciosa")).to_be_visible()

    def test_whole_map_zoom_and_keyboard_choices_fit_small_and_large_text(self):
        for width in (320, 390, 1280):
            with self.subTest(width=width):
                self.open_islands(width)
                self.view("Mapa").click()
                viewport = self.page.locator(".explore-map-viewport")
                expect(viewport).to_be_visible()
                self.page.wait_for_function("[...document.querySelectorAll('.explore-pin-image')].every(image=>image.complete&&image.naturalWidth>0)")
                self.assertTrue(viewport.evaluate("node=>node.scrollWidth<=node.clientWidth+1"))
                self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"))
                for pin in self.page.locator(".explore-pin").all():
                    box = pin.bounding_box()
                    self.assertGreaterEqual(box["width"], 44)
                    self.assertGreaterEqual(box["height"], 44)
                zoom = self.page.get_by_role("button", name="Acercar mapa", exact=True)
                zoom.click()
                expect(zoom).to_be_focused()
                expect(zoom).to_have_attribute("aria-pressed", "true")
                if width < 760:
                    self.assertTrue(viewport.evaluate("node=>node.scrollWidth>node.clientWidth"))
                    self.page.get_by_role("button", name="Ver las islas hacia el este", exact=True).click()
                    self.page.wait_for_function("document.querySelector('.explore-map-viewport').scrollLeft>0")
                pin = self.page.locator('.explore-pin[data-route="la-graciosa"]')
                pin.focus()
                expect(pin).to_be_focused()
                self.assertTrue(pin.evaluate("node=>{const a=node.getBoundingClientRect(),b=node.closest('.explore-map-viewport').getBoundingClientRect();return a.left>=b.left-1&&a.right<=b.right+1}"))
                zoom.click()
                self.assertTrue(viewport.evaluate("node=>node.scrollWidth<=node.clientWidth+1"))
                self.view("Lista").click()
                self.page.evaluate("document.documentElement.style.fontSize='200%'")
                self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"))
                last = self.page.locator('#islandGrid [data-route="la-graciosa"]')
                last.focus()
                last.press("Enter")
                expect(self.page.locator("#route-la-graciosa")).to_be_visible()
