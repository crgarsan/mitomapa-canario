"""Exercise feedback entry and narrow-screen navigation with the published CSP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CSP = next(
    line.split(":", 1)[1].strip()
    for line in (ROOT / "_headers").read_text().splitlines()
    if line.strip().startswith("Content-Security-Policy:")
)


class QuietCspHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class NavigationAccessibilityBrowserTests(unittest.TestCase):
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
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        self.context.route(
            "**/*",
            lambda route: route.continue_()
            if urlsplit(route.request.url).hostname in ("127.0.0.1", None)
            else route.abort(),
        )
        self.page = self.context.new_page()
        self.errors = []
        self.policy_errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on(
            "console",
            lambda message: self.policy_errors.append(message.text)
            if message.type == "error" and "Content Security Policy" in message.text
            else None,
        )

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def test_legacy_feedback_entry_opens_feedback_under_published_csp(self):
        self.page.goto(self.base + "valoracion.html", wait_until="networkidle")
        expect(self.page).to_have_url(self.base + "index.html#studentFeedback", timeout=3000)
        expect(self.page.locator("#resourceFeedback")).to_have_attribute("open", "")
        expect(self.page.locator("#feedbackTitle")).to_be_visible()
        self.assertEqual(self.policy_errors, [])

    def test_narrow_navigation_keeps_enlarged_labels_and_teacher_in_view(self):
        self.page.goto(self.base, wait_until="networkidle")
        for width, text_scale in ((320, 2), (320, 1), (390, 1), (640, 2), (1280, 1)):
            with self.subTest(width=width, text_scale=text_scale):
                self.page.set_viewport_size({"width": width, "height": 800})
                self.page.evaluate(
                    "scale => document.documentElement.style.fontSize = `${scale * 100}%`",
                    text_scale,
                )
                self.page.evaluate('window.MitoMapaNavigation.go("inicio")')
                geometry = self.page.evaluate("""() => {
                  const box = element => {
                    const rect = element.getBoundingClientRect();
                    return {left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom};
                  };
                  return {
                    width: innerWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    controls: ["openPassport", "openTeacher"].map(id => ({id, ...box(document.getElementById(id))})),
                    links: [...document.querySelectorAll('.main-navigation a')].map(link => {
                      const range = document.createRange();
                      range.selectNodeContents(link);
                      return {label: link.textContent.trim(), outer: box(link), text: box(range)};
                    })
                  };
                }""")
                self.assertLessEqual(geometry["scrollWidth"], width + 1)
                for control in geometry["controls"]:
                    self.assertGreaterEqual(control["left"], -1, control)
                    self.assertLessEqual(control["right"], width + 1, control)
                for link in geometry["links"]:
                    self.assertGreaterEqual(link["text"]["left"], link["outer"]["left"] - 1, link)
                    self.assertLessEqual(link["text"]["right"], link["outer"]["right"] + 1, link)
                self.page.locator("#openTeacher").click()
                expect(self.page.locator("#teacherDialog")).to_be_visible()
                self.page.keyboard.press("Escape")
                expect(self.page.locator("#teacherDialog")).not_to_be_visible()
                self.assertEqual(self.page.evaluate("scrollX"), 0)

    def test_feedback_entry_keeps_a_manual_link_without_javascript(self):
        with self.browser.new_context(java_script_enabled=False) as context:
            context.route(
                "**/*",
                lambda route: route.continue_()
                if urlsplit(route.request.url).hostname in ("127.0.0.1", None)
                else route.abort(),
            )
            page = context.new_page()
            page.goto(self.base + "valoracion.html", wait_until="domcontentloaded")
            link = page.get_by_role("link", name="abre el Explorador")
            expect(link).to_be_visible()
            link.click()
            self.assertEqual(urlsplit(page.url).path, "/index.html")
            expect(page.locator(".noscript-note")).to_be_visible()

    def test_route_content_reflows_without_widening_the_page(self):
        self.page.emulate_media(reduced_motion="reduce")
        self.page.goto(self.base, wait_until="networkidle")
        islands = (
            "tenerife", "gran-canaria", "la-palma", "la-gomera",
            "el-hierro", "fuerteventura", "lanzarote", "la-graciosa",
        )
        screens = ["islas", "puzle", "comparar", "recursos"] + [
            f"isla/{island}/{step}"
            for island in islands for step in ("cuento", "retos", "taller")
        ]
        for width, text_scale in ((320, 2), (320, 1), (390, 1), (640, 2)):
            self.page.set_viewport_size({"width": width, "height": 800})
            self.page.evaluate(
                "scale => document.documentElement.style.fontSize = `${scale * 100}%`",
                text_scale,
            )
            for screen in screens:
                with self.subTest(width=width, text_scale=text_scale, screen=screen):
                    self.page.evaluate("screen => window.MitoMapaNavigation.go(screen)", screen)
                    if screen == "recursos":
                        self.page.locator("details.resource-disclosure").evaluate_all(
                            "details => details.forEach(element => element.open = true)"
                        )
                    self.page.evaluate("scrollTo(0, 0)")
                    self.assertLessEqual(
                        self.page.evaluate("document.documentElement.scrollWidth"), width + 1
                    )


if __name__ == "__main__":
    unittest.main()
