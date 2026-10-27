"""Exercise agreed routes, separate rewards and learner changes in Chromium.

Uses the real local resource and its teacher controls. No public site is used.
Requires Python Playwright and Chromium, like the other browser checks.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
import unittest

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PAIR = ["tenerife", "gran-canaria"]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class JourneyBrowserTest(unittest.TestCase):
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
        self.context = self.browser.new_context(accept_downloads=True)
        self.context.add_init_script("window.confirm=()=>true")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base, wait_until="networkidle")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open_tools(self):
        self.page.locator("#openTeacher").click()
        self.page.locator("#teacherToolsTab").click()
        self.open_route_choices()

    def open_route_choices(self):
        settings = self.page.locator("#agreedRouteSettings")
        if settings.get_attribute("open") is None:
            settings.locator("summary").click()

    def select_routes(self, *ids):
        for route_id in ids:
            self.page.locator(f'[data-agreed-route="{route_id}"]').check()

    def selected_routes(self):
        return self.page.locator("[data-agreed-route]:checked").evaluate_all(
            "nodes=>nodes.map(node=>node.dataset.agreedRoute)"
        )

    def review_routes(self, *ids):
        for route_id in ids:
            self.page.locator(f'[data-review-route="{route_id}"]').check()

    def change_stage(self, level):
        self.page.locator("#teacherGuideTab").click()
        for disclosure in self.page.locator("#teacherGuidePanel details").all():
            if (
                disclosure.locator(f'[data-learning-level="{level}"]').count()
                and disclosure.get_attribute("open") is None
            ):
                disclosure.locator(":scope > summary").click()
        self.page.locator(
            f'#teacherGuidePanel [data-learning-level="{level}"]'
        ).click()
        self.page.locator("#teacherToolsTab").click()
        self.open_route_choices()

    def import_progress(self, payload):
        self.page.locator("#teacherImportStatus").evaluate(
            "node=>{node.textContent=''}"
        )
        self.page.locator("#importProgressFile").set_input_files(
            {
                "name": "seguimiento.json",
                "mimeType": "application/json",
                "buffer": json.dumps(payload).encode(),
            }
        )
        self.page.wait_for_function("""()=>{
          const text=document.getElementById('teacherImportStatus').textContent;
          return text.includes('correctamente')||text.startsWith('No se pudo cargar');
        }""")
        self.assertIn(
            "correctamente", self.page.locator("#teacherImportStatus").text_content()
        )

    def test_two_reviewed_islands_complete_the_route_without_awarding_badges(self):
        self.open_tools()
        self.select_routes(*PAIR)
        self.assertIn("0/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.review_routes("tenerife")
        self.assertIn("1/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.assertIsNotNone(
            self.page.locator("#agreedRouteCompletion").get_attribute("hidden")
        )
        self.review_routes("gran-canaria")
        self.assertIn("2/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.assertIn("0/8", self.page.locator("#agreedRouteCollection").text_content())
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.page.locator("#closeTeacher").click()

        # Agreement is a learning goal, not a lock on the other six islands.
        self.page.goto(self.base + "#islas", wait_until="networkidle")
        self.page.locator("#exploreMap").get_by_role("button", name="Lista", exact=True).click()
        island_list = self.page.locator("#islandGrid").locator("xpath=ancestor::details[1]")
        if island_list.get_attribute("open") is None:
            island_list.locator(":scope > summary").click()
        cards = self.page.locator("#islandGrid [data-route]")
        self.assertEqual(cards.count(), 8)
        self.assertTrue(all(card.is_enabled() for card in cards.all()))
        self.page.locator('#islandGrid [data-route="lanzarote"]').click()
        self.assertTrue(self.page.locator("#route-lanzarote").is_visible())

        self.page.goto(self.base + "#recursos", wait_until="networkidle")
        self.page.locator("#resourcePassport > summary").click()
        self.assertTrue(self.page.locator("#agreedRouteCompletion").is_visible())
        self.assertIn("2 islas", self.page.locator("#agreedRouteCompletionText").text_content())
        self.assertIn("2/2", self.page.locator("#itinerarySummary").text_content())
        self.assertIn("0/8", self.page.locator("#itinerarySummary").text_content())
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")

        # Revising an agreed task invalidates its previous manual review.
        self.open_tools()
        self.page.locator('[data-task-route="tenerife"]').fill("Explicar la fuente elegida")
        self.page.locator('[data-task-route="tenerife"]').press("Tab")
        self.assertFalse(self.page.locator('[data-review-route="tenerife"]').is_checked())
        self.assertIn("1/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.assertIsNotNone(
            self.page.locator("#agreedRouteCompletion").get_attribute("hidden")
        )

    def test_agreement_and_review_are_independent_per_stage_and_survive_reload(self):
        self.open_tools()
        self.select_routes(*PAIR)
        self.review_routes("tenerife")
        self.change_stage("advanced")
        self.assertEqual(self.selected_routes(), [])
        self.assertEqual(self.page.locator("[data-review-route]:checked").count(), 0)
        self.select_routes("lanzarote")
        self.review_routes("lanzarote")
        self.assertIn("1/1", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.change_stage("middle")
        self.assertEqual(self.selected_routes(), PAIR)
        self.assertTrue(self.page.locator('[data-review-route="tenerife"]').is_checked())
        self.assertFalse(self.page.locator('[data-review-route="gran-canaria"]').is_checked())
        self.assertIn("1/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.page.reload(wait_until="networkidle")
        self.open_tools()
        self.assertEqual(self.selected_routes(), PAIR)
        self.assertIn("1/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
        self.change_stage("advanced")
        self.assertEqual(self.selected_routes(), ["lanzarote"])
        self.assertTrue(self.page.locator('[data-review-route="lanzarote"]').is_checked())

    def test_download_round_trip_and_legacy_import_replace_the_previous_learners_route(self):
        self.open_tools()
        self.select_routes(*PAIR)
        self.review_routes(*PAIR)
        self.change_stage("advanced")
        self.select_routes("lanzarote")
        self.review_routes("lanzarote")
        self.change_stage("middle")
        with self.page.expect_download() as download_info:
            self.page.locator("#exportProgress").click()
        exported = json.loads(Path(download_info.value.path()).read_text())
        self.assertEqual(exported["journey"]["levels"]["middle"], PAIR)
        self.assertEqual(exported["journey"]["levels"]["advanced"], ["lanzarote"])
        self.page.locator("#clearAgreedRoute").click()
        self.assertEqual(self.selected_routes(), [])
        self.import_progress(exported)
        self.assertEqual(self.selected_routes(), PAIR)
        self.assertIn("2/2", self.page.locator("#agreedRouteTeacherStatus").text_content())

        self.import_progress({
            "app": "mitomapa-canario", "version": "4.4.2", "learnerName": "Otra persona",
            "learningLevel": "middle",
            "progress": {"sourcePassed": [], "truthPassed": [], "earned": []},
        })
        self.assertEqual(self.selected_routes(), [])
        self.assertEqual(self.page.locator("#teacherLearnerName").input_value(), "Otra persona")
        self.assertEqual(self.page.locator("[data-review-route]:checked").count(), 0)
        self.assertIsNotNone(
            self.page.locator("#agreedRouteSummary").get_attribute("hidden")
        )
        self.assertIsNotNone(
            self.page.locator("#agreedRouteCompletion").get_attribute("hidden")
        )
        self.change_stage("advanced")
        self.assertEqual(self.selected_routes(), [])
        self.assertEqual(self.page.locator("[data-review-route]:checked").count(), 0)

    def test_reset_removes_the_agreed_route_and_reviews_in_every_stage(self):
        self.open_tools()
        self.select_routes(*PAIR)
        self.review_routes(*PAIR)
        self.change_stage("advanced")
        self.select_routes("lanzarote")
        self.review_routes("lanzarote")
        self.page.locator("#resetProgress").click()
        self.assertEqual(self.selected_routes(), [])
        self.assertEqual(self.page.locator("[data-review-route]:checked").count(), 0)
        self.assertIsNotNone(
            self.page.locator("#agreedRouteCompletion").get_attribute("hidden")
        )
        self.change_stage("middle")
        self.assertEqual(self.selected_routes(), [])
        self.assertEqual(self.page.locator("[data-review-route]:checked").count(), 0)
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.page.reload(wait_until="networkidle")
        self.open_tools()
        self.assertEqual(self.selected_routes(), [])

    def test_route_choices_support_keyboard_and_fit_mobile_and_desktop(self):
        for width in [320, 1280]:
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": 900})
                self.page.goto(self.base, wait_until="networkidle")
                self.page.locator("#openTeacher").click()
                self.page.locator("#teacherGuideTab").focus()
                self.page.keyboard.press("ArrowRight")
                self.assertTrue(self.page.locator("#teacherToolsTab").evaluate(
                    "node=>node===document.activeElement"
                ))
                self.assertFalse(self.page.locator("#teacherToolsPanel").is_hidden())
                summary = self.page.locator("#agreedRouteSettings > summary")
                summary.focus()
                summary.press("Enter")
                self.page.keyboard.press("Tab")
                first = self.page.locator("[data-agreed-route]").first
                self.assertTrue(first.evaluate("node=>node===document.activeElement"))
                self.page.keyboard.press("Space")
                self.assertTrue(first.is_checked())
                self.assertTrue(first.evaluate("node=>node===document.activeElement"))
                self.page.keyboard.press("Tab")
                second = self.page.locator("[data-agreed-route]").nth(1)
                self.assertTrue(second.evaluate("node=>node===document.activeElement"))
                self.page.keyboard.press("Space")
                self.assertTrue(second.is_checked())
                self.assertIn("0/2", self.page.locator("#agreedRouteTeacherStatus").text_content())
                for label in self.page.locator("#agreedRouteChoices label").all():
                    size = label.bounding_box()
                    self.assertGreaterEqual(size["height"], 44)
                    self.assertGreaterEqual(size["width"], 44)
                dimensions = self.page.evaluate("""()=>{
                  const dialog=document.getElementById('teacherDialog');
                  return {page:document.documentElement.scrollWidth,
                          viewport:innerWidth,dialog:dialog.scrollWidth,
                          available:dialog.clientWidth};
                }""")
                self.assertLessEqual(dimensions["page"], dimensions["viewport"] + 1)
                self.assertLessEqual(dimensions["dialog"], dimensions["available"] + 1)
                self.page.locator("#clearAgreedRoute").click()
                self.assertEqual(self.selected_routes(), [])


if __name__ == "__main__":
    unittest.main()
