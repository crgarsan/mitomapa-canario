"""Exercise the new reading formats and teacher-only help entry points."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSP = next(line.split(":", 1)[1].strip() for line in (ROOT / "_headers").read_text().splitlines()
           if line.strip().startswith("Content-Security-Policy:"))
SLUGS = ("tenerife", "gran-canaria", "la-palma", "la-gomera", "el-hierro",
         "fuerteventura", "lanzarote", "la-graciosa")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class StoryFormatsBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel="chromium", headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def test_each_island_has_two_views_permanent_pdf_and_optional_captions(self):
        self.page.goto(self.base, wait_until="networkidle")
        for slug in SLUGS:
            with self.subTest(island=slug):
                self.page.evaluate("slug => window.MitoMapaNavigation.go('isla/' + slug + '/cuento')", slug)
                route = self.page.locator(f"#route-{slug}")
                self.assertEqual(route.locator(".format-picker").count(), 1)
                self.assertTrue(route.get_by_role("radio", name="Audio y texto", exact=True).is_checked())
                pdf = route.locator(".format-pdf-download")
                self.assertTrue(pdf.is_visible())
                self.assertEqual(pdf.get_attribute("href"), f"media/{slug}/cuento-ilustrado.pdf")
                route.get_by_role("radio", name="Vídeo", exact=True).check()
                self.assertTrue(route.locator(".format-video-panel").is_visible())
                self.assertTrue(pdf.is_visible())
                state = route.locator("video").evaluate("video => ({paused:video.paused, autoplay:video.autoplay, defaults:[...video.querySelectorAll('track')].filter(t=>t.default).length, tracks:[...video.textTracks].map(t=>({lang:t.language,mode:t.mode}))})")
                self.assertTrue(state["paused"])
                self.assertFalse(state["autoplay"])
                self.assertEqual(state["defaults"], 0)
                self.assertEqual(state["tracks"], [{"lang": "es", "mode": "disabled"}])
                route.get_by_role("radio", name="Audio y texto", exact=True).check()
                self.assertTrue(route.locator(".route-grid").is_visible())
                self.assertTrue(route.locator(".narrator").is_visible())

    def test_quick_help_is_in_teacher_and_save_help_opens_tools_with_keyboard(self):
        self.page.goto(self.base + "#recursos", wait_until="networkidle")
        self.assertEqual(self.page.locator('[data-screen="recursos"] .resource-quick-help').count(), 0)
        self.assertEqual(self.page.get_by_text("Abre el apartado que buscas.", exact=True).count(), 0)
        self.page.locator("#openTeacher").click()
        help_block = self.page.locator("#teacherGuidePanel .resource-quick-help")
        self.assertTrue(help_block.is_visible())
        self.assertEqual(help_block.get_by_role("link", name="Cómo empezar y preparar la actividad").get_attribute("href"), "GUIA_DOCENTE.html")
        self.assertEqual(help_block.get_by_role("link", name="Cuaderno imprimible").get_attribute("href"), "downloads/Cuaderno_de_ruta_MitoMapa.html")
        help_block.get_by_role("button", name="Guardar o recuperar el trabajo").press("Enter")
        self.assertTrue(self.page.locator("#teacherToolsPanel").is_visible())
        self.assertEqual(self.page.locator("#teacherToolsTab").get_attribute("aria-selected"), "true")
        self.assertTrue(self.page.locator("#exportProgress").evaluate("button => document.activeElement === button"))

    def test_teacher_help_and_format_controls_fit_narrow_enlarged_text(self):
        self.page.goto(self.base + "#isla/la-palma/cuento", wait_until="networkidle")
        self.page.set_viewport_size({"width": 320, "height": 800})
        self.page.evaluate("document.documentElement.style.fontSize = '200%'")
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 321)
        self.page.locator("#openTeacher").click()
        boxes = self.page.locator("#teacherGuidePanel .resource-quick-help a, #teacherGuidePanel .resource-quick-help button, #teacherDialog [data-teacher-tab]").evaluate_all("elements => elements.map(e => ({text:e.textContent,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))")
        self.assertEqual(len(boxes), 5)
        for box in boxes:
            self.assertGreaterEqual(box["left"], -1, box)
            self.assertLessEqual(box["right"], 321, box)


if __name__ == "__main__":
    unittest.main()
