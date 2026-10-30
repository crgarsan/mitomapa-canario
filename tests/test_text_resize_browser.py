"""Dialogs keep their text and keyboard controls usable with enlarged text."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright
from test_navigation_accessibility_browser import QuietCspHandler, ROOT


class TextResizeBrowserTests(unittest.TestCase):
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
        self.context = self.browser.new_context(viewport={"width": 320, "height": 800})
        self.context.route(
            "**/*", lambda route: route.continue_()
            if urlsplit(route.request.url).hostname in ("127.0.0.1", None)
            else route.abort()
        )
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base, wait_until="networkidle")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def configure(self, width, scale, motion):
        self.page.set_viewport_size({"width": width, "height": 800})
        self.page.emulate_media(reduced_motion=motion)
        self.page.evaluate("scale => document.documentElement.style.fontSize = `${scale * 100}%`", scale)

    def assert_contained(self, locator, local_scroll=False):
        geometry = locator.evaluate("""element => {
          const rect = element.getBoundingClientRect();
          return {left: rect.left, right: rect.right, top: rect.top,
            bottom: rect.bottom, client: element.clientWidth, scroll: element.scrollWidth};
        }""")
        self.assertGreaterEqual(geometry["left"], -1, geometry)
        self.assertLessEqual(geometry["right"], self.page.viewport_size["width"] + 1, geometry)
        if not local_scroll:
            self.assertLessEqual(geometry["scroll"], geometry["client"] + 1, geometry)

    def screenshot(self, name):
        destination = os.environ.get("TEXT_RESIZE_SCREENSHOTS")
        if destination:
            Path(destination).mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(Path(destination) / name))

    def test_dialog_content_and_close_reflow_without_clipping(self):
        # Losing intrinsic-size constraints or header wrapping must expose overflow.
        for width, scale, motion in ((320, 2, "reduce"), (390, 1, "no-preference"), (1280, 1, "reduce")):
            for kind in ("Passport", "Teacher"):
                with self.subTest(width=width, scale=scale, dialog=kind):
                    self.configure(width, scale, motion)
                    opener = self.page.locator(f"#open{kind}")
                    opener.click()
                    dialog = self.page.locator(f"#{kind.lower()}Dialog")
                    close = self.page.locator(f"#close{kind}")
                    expect(dialog).to_be_visible()
                    close.focus()
                    expect(close).to_be_focused()
                    self.screenshot(f"dialog-{kind.lower()}-{width}-{scale}.png")
                    try:
                        self.assert_contained(dialog)
                        self.assert_contained(dialog.locator(".dialog-head"))
                        self.assert_contained(close)
                        rect = close.bounding_box()
                        self.assertGreaterEqual(rect["y"], 3, rect)
                        self.assertLessEqual(rect["y"] + rect["height"], 797, rect)
                        self.assertEqual(close.evaluate("getComputedStyle(document.activeElement).outlineStyle"), "solid")
                        # Scroll to the end, then bring the focused close back into view.
                        dialog.evaluate("element => element.scrollTop = element.scrollHeight")
                        close.focus()
                        close.scroll_into_view_if_needed()
                        self.assert_contained(close)
                        self.page.keyboard.press("Enter")
                        expect(dialog).not_to_be_visible()
                        expect(opener).to_be_focused()
                    finally:
                        self.page.keyboard.press("Escape")

    def test_teacher_tabs_wrap_and_keyboard_table_scrolling_stays_local(self):
        # A tab's label must fit its own button, not spill into its neighbour.
        for width, scale in ((320, 2), (390, 1), (1280, 1)):
            with self.subTest(width=width, scale=scale):
                self.configure(width, scale, "reduce")
                self.page.locator("#openTeacher").click()
                dialog = self.page.locator("#teacherDialog")
                guide = dialog.locator("#teacherGuideTab")
                tools = dialog.locator("#teacherToolsTab")
                try:
                    self.assert_contained(guide)
                    self.assert_contained(tools)
                    guide.focus()
                    self.page.keyboard.press("ArrowRight")
                    expect(tools).to_be_focused()
                    expect(tools).to_have_attribute("aria-selected", "true")
                    expect(dialog.locator("#teacherToolsPanel")).to_be_visible()
                    self.assert_contained(dialog)
                    table = dialog.locator(".teacher-table-wrap")
                    self.assert_contained(table, local_scroll=True)
                    table.focus()
                    expect(table).to_be_focused()
                    if table.evaluate("element => element.scrollWidth > element.clientWidth"):
                        self.page.keyboard.press("ArrowRight")
                        self.page.wait_for_function("element => element.scrollLeft > 0", arg=table.element_handle())
                        self.assertGreater(table.evaluate("element => element.scrollLeft"), 0)
                    self.assertEqual(self.page.evaluate("scrollX"), 0)
                    self.screenshot(f"teacher-tools-{width}-{scale}.png")
                    self.assertTrue(table.evaluate("""element => {
                      const rect = element.getBoundingClientRect();
                      const hit = document.elementFromPoint(rect.left + rect.width / 2,
                        Math.max(0, rect.top) + Math.min(rect.height, innerHeight) / 2);
                      return element.contains(hit);
                    }"""), "The sticky header must not obscure the focused teacher table")
                    tools.focus()
                    self.page.keyboard.press("ArrowLeft")
                    expect(guide).to_be_focused()
                    expect(guide).to_have_attribute("aria-selected", "true")
                    self.page.keyboard.press("Escape")
                    expect(dialog).not_to_be_visible()
                    expect(self.page.locator("#openTeacher")).to_be_focused()
                finally:
                    self.page.keyboard.press("Escape")


if __name__ == "__main__":
    unittest.main()
