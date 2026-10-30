"""Regress creative edits through real controls and persisted browser state."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
import unittest

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ["early", "middle", "advanced", "secondary"]
WORKSHOP_KEY = "mitomapa-canario-cuaderno-v1"
ITINERARY_KEY = "mitomapa-canario-itinerarios-v1"
CSP = next(line.split(":", 1)[1].strip() for line in (ROOT / "_headers").read_text().splitlines()
           if line.strip().startswith("Content-Security-Policy:"))


class QuietCspHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class PersistentStateBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietCspHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=shutil.which("chromium"),
                                                     args=["--no-sandbox", "--disable-dev-shm-usage"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
        self.context.add_init_script("window.confirm=()=>true")
        self.page = self.context.new_page()
        self.page.set_default_timeout(7000)
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base, wait_until="networkidle")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def seed(self, *, level="advanced", text="", route="tenerife"):
        # A previous student's locally saved, manually reviewed work, read by
        # normal startup; all subsequent edits use the actual form controls.
        review = {stage: {"relation": "reviewed"} for stage in LEVELS}
        workbook = {"routes": {route: {"text": text, "creation": bool(text),
                                       "secondaryText": "Una producción anterior", "secondaryCreation": True,
                                       "creationReviewV1": review}}}
        itineraries = {stage: {route: {"reviewed": True, "selectedTasks": ["creation"]}} for stage in LEVELS}
        self.page.evaluate("""([workbook, itineraries, level]) => {
          localStorage.clear();
          localStorage.setItem('mitomapa-canario-cuaderno-v1', JSON.stringify(workbook));
          localStorage.setItem('mitomapa-canario-itinerarios-v1', JSON.stringify(itineraries));
          localStorage.setItem('mitomapa-canario-preferencias-v3', JSON.stringify({learningLevel: level}));
        }""", [workbook, itineraries, level])
        self.page.evaluate("route=>history.replaceState(null, '', '#isla/'+route+'/taller')", route)
        self.page.reload(wait_until="networkidle")
        self.assertEqual(self.page.locator("body").get_attribute("data-learning-level"), level)
        self.page.locator(f'#activity-{route} [data-activity-tab="creation"]').click()

    def state(self, route="tenerife"):
        return self.page.evaluate("([key, id])=>JSON.parse(localStorage.getItem(key)).routes[id]", [WORKSHOP_KEY, route])

    def reviewed(self, route="tenerife"):
        return self.page.evaluate("([key, id])=>Object.fromEntries(Object.entries(JSON.parse(localStorage.getItem(key))).map(([level, entries])=>[level, entries[id].reviewed]))", [ITINERARY_KEY, route])

    def canvas(self):
        return self.page.locator("#activity-gran-canaria canvas")

    def pixels(self):
        return self.canvas().evaluate("node=>node.toDataURL('image/png')")

    def stationary_gesture(self):
        canvas = self.canvas()
        canvas.scroll_into_view_if_needed()
        box = canvas.bounding_box()
        self.page.mouse.move(box["x"] + 80, box["y"] + 80)
        self.page.mouse.down()
        # Some devices emit pointermove even when coordinates do not change.
        self.page.mouse.move(box["x"] + 80, box["y"] + 80)
        self.page.mouse.up()

    def stroke(self):
        canvas = self.canvas()
        canvas.scroll_into_view_if_needed()
        box = canvas.bounding_box()
        self.page.mouse.move(box["x"] + 80, box["y"] + 80)
        self.page.mouse.down()
        self.page.mouse.move(box["x"] + 130, box["y"] + 100, steps=4)
        self.page.mouse.up()

    def test_criterion_edit_invalidates_only_its_stage(self):
        # Catch a criterion handler using broad shared-production invalidation.
        for level in LEVELS:
            with self.subTest(level=level):
                self.seed(level=level, text="Una idea compartida")
                self.page.locator('#activity-tenerife [data-creation-review="relation"]').select_option("in_progress")
                self.assertEqual(self.reviewed(), {stage: stage != level for stage in LEVELS})
                state = self.state()
                self.assertTrue(state["creation"])
                self.assertTrue(state["secondaryCreation"])
                self.assertEqual({stage: state["creationReviewV1"][stage]["relation"] for stage in LEVELS},
                                 {stage: "in_progress" if stage == level else "reviewed" for stage in LEVELS})

    def test_shared_primary_text_edit_invalidates_every_primary_stage(self):
        self.seed(text="Una idea compartida")
        self.page.locator('#activity-tenerife [data-primary-text]').fill("Una idea compartida revisada")
        self.assertEqual(self.reviewed(), {"early": False, "middle": False, "advanced": False, "secondary": True})
        state = self.state()
        self.assertFalse(state["creation"])
        self.assertTrue(state["secondaryCreation"])
        self.assertEqual({level: state["creationReviewV1"][level]["relation"] for level in LEVELS},
                         {"early": "in_progress", "middle": "in_progress", "advanced": "in_progress", "secondary": "reviewed"})

    def test_secondary_text_edit_preserves_primary_reviews_and_preparation(self):
        self.seed(level="secondary", text="Una idea compartida")
        self.page.locator('#activity-tenerife [data-secondary-text]').fill("Una producción revisada de Secundaria")
        self.assertEqual(self.reviewed(), {"early": True, "middle": True, "advanced": True, "secondary": False})
        state = self.state()
        self.assertTrue(state["creation"])
        self.assertFalse(state["secondaryCreation"])
        self.assertEqual(state["creationReviewV1"]["middle"]["relation"], "reviewed")
        self.assertEqual(state["creationReviewV1"]["secondary"]["relation"], "in_progress")

    def test_returning_from_either_story_preserves_both_creative_islands(self):
        self.page.evaluate("window.MitoMapaNavigation.go('crear')")
        self.page.locator("#creative-first-island").select_option("tenerife")
        self.page.locator("#creative-second-island").select_option("el-hierro")
        for name, route in [("Tenerife", "tenerife"), ("El Hierro", "el-hierro")]:
            self.page.locator("#creative-first-island").select_option("tenerife")
            self.page.locator("#creative-second-island").select_option("el-hierro")
            with self.subTest(story=route):
                self.page.get_by_role("button", name=f"Volver al cuento de {name}", exact=True).click()
                self.page.locator(f'#route-{route} a[href="#crear"]').click()
                self.assertEqual(self.page.locator("#creative-first-island").input_value(), "tenerife")
                self.assertEqual(self.page.locator("#creative-second-island").input_value(), "el-hierro")
                expect(self.page.locator(".creative-route-context")).to_contain_text("Tenerife y El Hierro")

    def test_explicit_creative_choices_replace_previous_selection_and_reset_clears_it(self):
        self.page.evaluate("window.MitoMapaNavigation.go('crear')")
        self.page.locator("#creative-first-island").select_option("tenerife")
        self.page.locator("#creative-second-island").select_option("el-hierro")
        self.page.evaluate("window.MitoMapaLearning.setClosureRoutes(['la-palma', 'lanzarote'])")
        self.assertEqual(self.page.locator("#creative-first-island").input_value(), "la-palma")
        self.assertEqual(self.page.locator("#creative-second-island").input_value(), "lanzarote")
        self.page.locator("#creative-second-island").select_option("")
        expect(self.page.locator(".creative-route-context")).to_contain_text("La Palma.")
        self.page.evaluate("resetProgress()")
        self.assertEqual(self.page.locator("#creative-first-island").input_value(), "")
        self.assertEqual(self.page.locator("#creative-second-island").input_value(), "")
        self.page.evaluate("window.MitoMapaNavigation.go('isla/la-gomera/cuento')")
        self.page.locator('#route-la-gomera a[href="#crear"]').click()
        self.assertEqual(self.page.locator("#creative-first-island").input_value(), "la-gomera")
        self.assertEqual(self.page.locator("#creative-second-island").input_value(), "")

    def test_direct_creation_load_and_reload_restore_the_saved_agreed_pair(self):
        self.page.evaluate("""() => {
          localStorage.clear();
          localStorage.setItem('mitomapa-canario-preferencias-v3',JSON.stringify({learningLevel:'advanced',lastRouteId:'tenerife'}));
          localStorage.setItem('mitomapa-canario-ruta-acordada-v1',JSON.stringify({version:1,levels:{advanced:['la-palma','lanzarote']}}));
          history.replaceState(null,'','#crear');
        }""")
        self.page.reload(wait_until="networkidle")
        for visit in ("direct load", "reload", "return"):
            with self.subTest(visit=visit):
                self.assertEqual(self.page.locator("#creative-first-island").input_value(),"la-palma")
                self.assertEqual(self.page.locator("#creative-second-island").input_value(),"lanzarote")
            if visit == "direct load":
                self.page.reload(wait_until="networkidle")
            elif visit == "reload":
                self.page.evaluate("window.MitoMapaNavigation.go('inicio');window.MitoMapaNavigation.go('crear')")

    def test_direct_creation_without_an_agreement_keeps_the_last_island_fallback(self):
        self.page.evaluate("""() => {
          localStorage.clear();
          localStorage.setItem('mitomapa-canario-preferencias-v3',JSON.stringify({learningLevel:'advanced',lastRouteId:'tenerife'}));
          history.replaceState(null,'','#crear');
        }""")
        self.page.reload(wait_until="networkidle")
        self.assertEqual(self.page.locator("#creative-first-island").input_value(),"tenerife")
        self.assertEqual(self.page.locator("#creative-second-island").input_value(),"")

    def test_stationary_click_keeps_blank_drawing_empty_and_cannot_prepare_it(self):
        self.seed(route="gran-canaria")
        pixels = self.pixels()
        before = self.state("gran-canaria")
        self.stationary_gesture()
        self.assertEqual(self.pixels(), pixels)
        self.assertEqual(self.state("gran-canaria"), before)
        self.page.locator("#activity-gran-canaria .activity-save-creation").click()
        self.assertFalse(self.state("gran-canaria")["creation"])
        self.assertFalse(self.state("gran-canaria").get("drawingHasInk", False))
        expect(self.page.locator('#activity-gran-canaria [data-activity-panel="creation"] .activity-panel-status')).to_contain_text("Haz un dibujo")

    def test_stationary_click_preserves_prepared_reviewed_drawing_and_undo_history(self):
        self.seed(route="gran-canaria")
        self.stroke()
        self.page.locator("#activity-gran-canaria .activity-save-creation").click()
        self.page.locator('#activity-gran-canaria [data-creation-review="relation"]').select_option("reviewed")
        self.page.locator("#openTeacher").click()
        self.page.locator("#teacherToolsTab").click()
        self.page.locator('[data-review-route="gran-canaria"]').check()
        self.page.locator("#closeTeacher").click()
        before = self.state("gran-canaria")
        pixels = self.pixels()
        reviews = self.reviewed("gran-canaria")
        self.stationary_gesture()
        self.assertEqual(self.pixels(), pixels)
        self.assertEqual(self.state("gran-canaria"), before)
        self.assertEqual(self.reviewed("gran-canaria"), reviews)
        self.page.locator("#activity-gran-canaria .draw-undo").click()
        self.page.wait_for_function("()=>!getWorkshopRouteState('gran-canaria').drawingHasInk")
        self.assertFalse(self.state("gran-canaria")["creation"])

    def test_real_stroke_undo_clear_and_written_alternative_still_work(self):
        self.seed(route="gran-canaria")
        blank = self.pixels()
        self.stroke()
        self.assertNotEqual(self.pixels(), blank)
        self.assertTrue(self.state("gran-canaria")["drawingHasInk"])
        self.page.locator("#activity-gran-canaria .activity-save-creation").click()
        self.assertTrue(self.state("gran-canaria")["creation"])
        self.page.locator("#activity-gran-canaria .draw-undo").click()
        self.page.wait_for_function("()=>!getWorkshopRouteState('gran-canaria').drawingHasInk")
        self.stroke()
        self.page.locator("#activity-gran-canaria .draw-clear").click()
        self.assertIsNone(self.state("gran-canaria")["drawing"])
        self.assertFalse(self.state("gran-canaria")["drawingHasInk"])
        self.page.locator('#activity-gran-canaria [data-primary-text]').fill("El tibicena aparece entre las tabaibas")
        self.page.locator("#activity-gran-canaria .activity-save-creation").click()
        self.assertTrue(self.state("gran-canaria")["creation"])


if __name__ == "__main__":
    unittest.main()
