"""Exercise voluntary learning supports against real routes and the published CSP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
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
ISLANDS = [
    "tenerife", "gran-canaria", "la-palma", "la-gomera", "el-hierro",
    "fuerteventura", "lanzarote", "la-graciosa",
]
# Independent semantic expectations: each destination must actually contain the
# evidence needed for that question, rather than merely reproduce an ID table.
FRAGMENT_EVIDENCE = {
    "tenerife": {
        "source": ["había atrapado a Magec", "pedía ayuda a Achamán", "una línea dorada"],
        "quiz": ["había atrapado a Magec", "cerró la entrada del volcán", "Dácil cuidaba cabras"],
    },
    "gran-canaria": {
        "source": ["Entre las tabaibas", "Juntos levantaron las teas", "huellas grandes"],
        "quiz": ["sendero de barranco", "llamó a los demás pastores", "huellas grandes"],
    },
    "la-palma": {
        "source": ["parecía sostener el cielo", "el grupo se alejó", "gran narradora"],
        "quiz": ["En Benahoare", "gran narradora", "el grupo se alejó"],
    },
    "la-gomera": {
        "source": ["odres hechos con piel de cabra", "familias temían", "falta de escucha"],
        "quiz": ["en Tenerife, vivía Jonay", "falta de escucha", "familias temían"],
    },
    "el-hierro": {
        "source": ["se convertía en gotas", "se apoderaran de la fuente", "continuaron contando"],
        "quiz": ["se convertía en gotas", "para no desperdiciar", "continuaron contando"],
    },
    "fuerteventura": {
        "source": ["lo utilizaron para encender", "la luz también se detuvo", "cumplieron su promesa"],
        "quiz": ["dos pastores llamados", "La luz avanzó detrás", "cumplieron su promesa"],
    },
    "lanzarote": {
        "source": ["su piel era más clara", "una esponja mojada", "debía ponerse en peligro"],
        "quiz": ["no celebró la prueba", "Una anciana", "La inteligencia y la solidaridad"],
    },
    "la-graciosa": {
        "source": ["era grumete", "más lejos parecía estar", "algunos mapas incluyeron"],
        "quiz": ["marcó el lugar en su carta", "solo quedaba el mar", "era grumete"],
    },
}


class QuietCspHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class LearningSupportBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietCspHandler, directory=str(ROOT))
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
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 900})
        self.page = self.context.new_page()
        self.page.emulate_media(reduced_motion="reduce")
        self.errors = []
        self.policy_errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on(
            "console", lambda message: self.policy_errors.append(message.text)
            if message.type == "error" and "Content Security Policy" in message.text else None,
        )
        self.page.goto(self.base, wait_until="networkidle")
        # Before coordinator integration, load the real module from this origin.
        if not self.page.evaluate("Boolean(window.MitoMapaLearning)"):
            if (ROOT / "aprendizaje.js").is_file():
                self.page.add_script_tag(url=self.base + "aprendizaje.js")
        self.assertTrue(self.page.evaluate("Boolean(window.MitoMapaLearning)"), "Learning module missing")
        if not self.page.locator('link[href*="aprendizaje.css"]').count():
            self.page.add_style_tag(url=self.base + "aprendizaje.css")
        self.page.evaluate("""() => {
          if (!document.querySelector('.learning-geography')) {
            window.MitoMapaLearning.init({openStory: (id, options) => {
              window.MitoMapaNavigation.go(`isla/${id}/cuento`);
              const target = document.getElementById(options.paragraphId);
              if (target && document.getElementById(`route-${id}`).contains(target)) target.focus();
            }});
          }
          routes.forEach(route => window.MitoMapaLearning.enhance(ensureRoute(route.id), route));
        }""")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])
        self.assertEqual(self.policy_errors, [])

    def open_question(self, route_id="tenerife", kind="source", index=0, show_help=True):
        self.page.evaluate("""([id, kind, index]) => {
          window.MitoMapaNavigation.go(`isla/${id}/retos`);
          const section = document.getElementById(`route-${id}`);
          if (kind === 'quiz') section.querySelector('[data-route-flow-quiz-target="verdad"]').click();
          document.getElementById(`${kind}-${id}`)._showQuestion(index);
        }""", [route_id, kind, index])
        question = self.page.locator(f"#{kind}-{route_id} .question").nth(index)
        disclosure = question.locator(".learning-help")
        if show_help and disclosure.get_attribute("open") is None:
            disclosure.locator(":scope > summary").click()
        return question

    def test_hints_are_graduated_and_available_before_answering(self):
        question = self.open_question(show_help=False)
        help_box = question.locator(".learning-help")
        self.assertEqual(help_box.evaluate("node => node.tagName"), "DETAILS")
        self.assertIsNone(help_box.get_attribute("open"))
        expect(help_box.get_by_text("Ayudas para pensar y explicar", exact=True)).to_be_visible()
        help_box.locator(":scope > summary").click()
        expect(help_box.locator(".learning-hint-one")).to_be_hidden()
        expect(help_box.locator(".learning-hint-two")).to_be_hidden()
        expect(help_box.locator(".learning-explanation")).to_be_hidden()
        help_box.get_by_role("button", name="Pista 1", exact=True).click()
        expect(help_box.locator(".learning-hint-one")).to_be_visible()
        expect(help_box.locator(".learning-hint-one")).to_contain_text("párrafo 2")
        expect(help_box.locator(".learning-hint-two")).to_be_hidden()
        help_box.get_by_role("button", name="Pista 2", exact=True).click()
        expect(help_box.locator(".learning-hint-two")).to_contain_text("entrañas del volcán")
        expect(help_box.locator(".learning-explanation")).to_be_hidden()
        self.assertEqual(question.locator("input:checked").count(), 0)
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        help_box.get_by_role("button", name="Ver explicación", exact=True).click()
        expect(help_box.locator(".learning-explanation")).to_contain_text("Guayota había encerrado")

    def test_every_question_returns_to_its_real_narrative_paragraph(self):
        for route_id, groups in FRAGMENT_EVIDENCE.items():
            self.assertEqual(self.page.locator(f"#route-{route_id} .story > p[data-learning-fragment]").count(), 7)
            for kind, evidence in groups.items():
                for index, expected_text in enumerate(evidence):
                    with self.subTest(route=route_id, kind=kind, question=index):
                        question = self.open_question(route_id, kind, index)
                        question.get_by_role("button", name="Volver al fragmento del cuento", exact=True).click()
                        target = self.page.locator(f"#route-{route_id} .story > p[data-learning-fragment]:focus")
                        expect(target).to_be_visible()
                        expect(target).to_be_focused()
                        expect(target).to_contain_text(expected_text)
                        self.assertFalse(target.evaluate("node => node.matches('.story-intro,.route-meta') || Boolean(node.closest('.radar'))"))
                        self.assertGreater(len(target.text_content()), 60)

    def test_feedback_keeps_explanation_voluntary_and_treats_text_safely(self):
        question = self.open_question(kind="quiz")
        result = self.page.evaluate("""() => window.MitoMapaLearning.feedback(
          'tenerife', 'quiz', 0, false, '<img src=x onerror=alert(1)> explicación', 'Pista del dato')""")
        self.assertIn("Revisen", result)
        help_box = question.locator(".learning-help")
        expect(help_box.locator(".learning-explanation")).to_be_hidden()
        help_box.get_by_role("button", name="Ver explicación", exact=True).click()
        expect(help_box.locator(".learning-explanation")).to_have_text("<img src=x onerror=alert(1)> explicación")
        self.assertEqual(help_box.locator("img").count(), 0)
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")

    def test_justification_and_source_guide_use_the_existing_evidence_field(self):
        question = self.open_question()
        expect(question.locator(".learning-oral-prompt")).to_contain_text("cuaderno")
        expect(question.locator(".learning-oral-prompt")).to_contain_text("palabras del fragmento")
        self.page.evaluate("setLearningLevel('advanced')")
        self.page.evaluate("window.MitoMapaNavigation.go('isla/tenerife/taller')")
        self.page.locator('[data-activity-tab="research"]').first.click()
        guide = self.page.locator("#learning-source-guide-tenerife")
        self.assertEqual(guide.evaluate("node => node.tagName"), "DETAILS")
        self.assertIsNone(guide.get_attribute("open"))
        guide.get_by_text("Cómo contrastar una fuente", exact=True).click()
        expect(guide).to_contain_text("autor")
        expect(guide).to_contain_text("límite")
        evidence = self.page.locator("#activity-tenerife [data-research-evidence]")
        self.assertIn("learning-source-reminder-tenerife", evidence.get_attribute("aria-describedby"))
        expect(self.page.locator("#learning-source-reminder-tenerife")).to_contain_text("Todavía no")
        self.assertIn("El cuento", evidence.get_attribute("placeholder"))
        self.assertEqual(self.page.locator("#activity-tenerife [data-activity-panel=research] textarea").count(), 1)
        evidence.fill("Fuente: Teide. Contraste: la recreación no demuestra el episodio anterior a la conquista.")
        self.assertIn("Fuente: Teide", self.page.evaluate("getWorkshopRouteState('tenerife').researchEvidence"))

    def test_creative_closure_reuses_project_and_is_available_with_zero_pieces(self):
        self.page.evaluate("""() => {
          const node = window.MitoMapaLearning.buildClosure();
          document.querySelector('main').append(node);
          node.hidden = false;
          node.removeAttribute('data-screen');
        }""")
        closure = self.page.locator("#creativeClosure")
        expect(closure).to_be_visible()
        self.assertEqual(self.page.locator(".final-project").count(), 1)
        self.assertEqual(closure.locator(".final-project").count(), 1)
        self.assertEqual(self.page.locator("#finalContent .final-project").count(), 0)
        expect(closure).to_contain_text("una o dos islas")
        expect(closure).to_contain_text("otro grupo de su aula")
        expect(closure.locator(".creative-example")).to_contain_text("recreación")
        expect(closure.locator(".creative-review")).to_contain_text("qué mejorarían")
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.assertNotIn("unlocked", self.page.locator("#finalContent").get_attribute("class"))
        before = self.page.evaluate("JSON.stringify(localStorage)")
        closure.get_by_label("Primera isla").select_option("la-graciosa")
        closure.get_by_label("Segunda isla (opcional)").select_option("lanzarote")
        expect(closure.locator(".creative-route-context")).to_contain_text("La Graciosa y Lanzarote")
        expect(closure.locator(".creative-route-note")).to_contain_text("caracola contemporánea")
        self.assertEqual(self.page.evaluate("JSON.stringify(localStorage)"), before)
        self.assertEqual(closure.locator("textarea,input").count(), 0)

    def test_textual_geography_practice_is_optional_and_does_not_award_progress(self):
        self.page.evaluate("window.MitoMapaNavigation.go('puzle')")
        practice = self.page.locator(".learning-geography")
        expect(practice.locator(":scope > summary")).to_be_visible()
        practice.locator(":scope > summary").click()
        expect(practice).to_contain_text("sin arrastrar")
        for name in ("Tenerife", "Gran Canaria", "La Palma", "La Gomera", "El Hierro", "Fuerteventura", "Lanzarote", "La Graciosa"):
            expect(practice).to_contain_text(name)
        self.assertEqual(practice.locator("select").count(), 7)
        before = self.page.evaluate("JSON.stringify(localStorage)")
        practice.locator("select").first.select_option("noroeste")
        practice.get_by_role("button", name="Comparar con la referencia textual").click()
        expect(practice.locator(".learning-geography-feedback").first).to_contain_text("Coincide")
        self.assertEqual(self.page.evaluate("JSON.stringify(localStorage)"), before)
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")

    def test_learning_controls_reflow_at_320_pixels_and_enlarged_text(self):
        self.page.set_viewport_size({"width": 320, "height": 900})
        self.page.evaluate("document.documentElement.style.fontSize='200%'")
        question = self.open_question()
        for button in question.locator(".learning-help button").all():
            button.focus()
            expect(button).to_be_focused()
            button.click()
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 321)
        self.page.evaluate("""() => {
          const closure = window.MitoMapaLearning.buildClosure();
          document.querySelector('main').append(closure);
          closure.hidden = false;
          closure.removeAttribute('data-screen');
        }""")
        self.page.locator(".creative-example > summary").click()
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 321)
        self.page.evaluate("window.MitoMapaNavigation.go('puzle')")
        self.page.locator(".learning-geography > summary").click()
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 321)

    def test_reset_closes_supports_and_discards_temporary_choices(self):
        question = self.open_question()
        for name in ("Pista 1", "Pista 2", "Ver explicación"):
            question.get_by_role("button", name=name, exact=True).click()
        before = self.page.evaluate("JSON.stringify(localStorage)")
        self.page.evaluate("""() => {
          const practice = document.querySelector('.learning-geography');
          practice.open = true;
          practice.querySelector('select').value = 'noroeste';
          practice.querySelector('.learning-geography-feedback').textContent = 'Elección anterior';
          const closure = window.MitoMapaLearning.buildClosure();
          document.querySelector('main').append(closure);
          window.MitoMapaLearning.setClosureRoutes(['la-graciosa', 'lanzarote']);
          closure.querySelector('.creative-example').open = true;
          window.MitoMapaLearning.reset();
        }""")
        help_box = question.locator(".learning-help")
        self.assertIsNone(help_box.get_attribute("open"))
        for selector in (".learning-hint-one", ".learning-hint-two", ".learning-explanation"):
            expect(help_box.locator(selector)).to_be_hidden()
            self.assertIsNotNone(help_box.locator(selector).get_attribute("hidden"))
        self.assertEqual(help_box.locator('[aria-expanded="true"]').count(), 0)
        self.assertIsNone(self.page.locator(".learning-geography").get_attribute("open"))
        self.assertEqual(self.page.locator(".learning-geography select").first.input_value(), "")
        self.assertEqual(self.page.locator(".learning-geography-feedback").first.text_content(), "")
        self.assertEqual(self.page.locator("#creative-first-island").input_value(), "")
        self.assertEqual(self.page.locator("#creative-second-island").input_value(), "")
        self.assertIsNone(self.page.locator(".creative-example").get_attribute("open"))
        self.assertEqual(self.page.evaluate("JSON.stringify(localStorage)"), before)
        self.page.evaluate("""() => {
          window.MitoMapaNavigation.go('puzle');
          const practice = document.querySelector('.learning-geography');
          practice.open = true;
          const reference = practice.querySelector('.learning-geography-reference');
          reference.open = true;
          reference.querySelector('summary').focus();
          window.MitoMapaLearning.reset();
        }""")
        expect(self.page.locator(".learning-geography > summary")).to_be_focused()


if __name__ == "__main__":
    unittest.main()
