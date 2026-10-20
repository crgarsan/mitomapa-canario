"""Exercise the reviewed native ELPX export without contacting other services."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from urllib.parse import urljoin, urlsplit
import zipfile

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
COVER = "GBC20261006PORTADA"
TEACHER = "20260823155836GUIAXU"
SOURCES = "GBC20261006FUENTES"
WEB_EXTRA = "20261006EXPLORER440"
TENERIFE = "20260823155836ISL1QG"
RETOS = "GBC20261006RETOS1"
TALLER = "GBC20261006TALLER1"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class EditorialElpxBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="mitomapa-editorial-browser-")
        cls.folder = Path(cls.temporary.name)
        version = json.loads((ROOT / "VERSION.json").read_text())
        with zipfile.ZipFile(ROOT / version["download"]["path"]) as package:
            for name in package.namelist():
                target = cls.folder / name
                if not target.resolve().is_relative_to(cls.folder.resolve()):
                    raise AssertionError("Archive member escapes the export folder")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(package.read(name))
        source = (cls.folder / "search_index.js").read_text()
        cls.search = json.loads(source[source.index("{"):].rstrip(";\n"))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(cls.folder)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=shutil.which("chromium"), args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temporary.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 900})
        self.external = []
        self.context.route("**/*", self.route)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def route(self, route):
        parsed = urlsplit(route.request.url)
        if parsed.scheme in {"data", "blob"} or parsed.hostname == "127.0.0.1":
            route.continue_()
        else:
            self.external.append(route.request.url)
            route.abort()

    def open_page(self, pid):
        self.page.goto(self.base + self.search[pid]["fileUrl"], wait_until="networkidle")

    def teacher_mode(self):
        switch = self.page.locator("#teacher-mode-toggler")
        if switch.count() and switch.is_visible():
            switch.check()

    def test_cover_has_four_pintaderas_above_and_below_the_uncropped_map(self):
        for width in (320, 1280):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": 1000})
                self.open_page(COVER)
                images = self.page.locator("#GBCTPORTADA img[src*='pintadera']")
                expect(images).to_have_count(8)
                for image in images.all():
                    expect(image).to_have_attribute("alt", "")
                    self.assertTrue(image.evaluate("img=>img.complete&&img.naturalWidth>0"))
                boxes = images.evaluate_all("imgs=>imgs.map(img=>{const r=img.getBoundingClientRect();return {top:Math.round(r.top),bottom:r.bottom,left:r.left,right:r.right}})")
                rows = {}
                for box in boxes:
                    rows[box["top"]] = rows.get(box["top"], 0) + 1
                    self.assertGreaterEqual(box["left"], 0)
                    self.assertLessEqual(box["right"], width + 1)
                self.assertEqual(sorted(rows.values()), [4, 4])
                map_image = self.page.locator("#GBCTPORTADA img[src$='mapa_canarias.webp']")
                expect(map_image).to_have_count(1)
                expect(map_image).to_be_visible()
                geometry = map_image.evaluate("""img=>{const r=img.getBoundingClientRect();return {
                    loaded:img.complete&&img.naturalWidth>0,naturalWidth:img.naturalWidth,
                    naturalHeight:img.naturalHeight,width:r.width,height:r.height,
                    top:r.top,bottom:r.bottom,left:r.left,right:r.right,
                    objectFit:getComputedStyle(img).objectFit}}""")
                self.assertTrue(geometry["loaded"])
                self.assertEqual((geometry["naturalWidth"], geometry["naturalHeight"]), (3000, 1514))
                self.assertAlmostEqual(geometry["width"] / geometry["height"], 3000 / 1514, delta=.01)
                self.assertNotEqual(geometry["objectFit"], "cover")
                self.assertGreaterEqual(geometry["left"], 0)
                self.assertLessEqual(geometry["right"], width + 1)
                self.assertTrue(all(box["bottom"] <= geometry["top"] for box in boxes[:4]))
                self.assertTrue(all(box["top"] >= geometry["bottom"] for box in boxes[4:]))
                self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"))

    def test_teacher_boxes_and_source_sections_open_with_keyboard(self):
        self.open_page(TEACHER)
        self.teacher_mode()
        boxes = self.page.locator("article.box")
        self.assertGreaterEqual(boxes.count(), 7)
        for box in boxes.all():
            content = box.locator(":scope > .box-content")
            expect(content).to_be_hidden()
            toggle = box.locator(":scope > header button.box-toggle")
            toggle.focus()
            toggle.press("Enter")
            expect(content).to_be_visible()
            self.page.wait_for_function("()=>window.$exeExport && !$exeExport.isTogglingBox")
            toggle.press("Space")
            expect(content).to_be_hidden()
            self.page.wait_for_function("()=>window.$exeExport && !$exeExport.isTogglingBox")
        self.open_page(SOURCES)
        for box in self.page.locator("article.box").all():
            content = box.locator(":scope > .box-content")
            if content.is_hidden():
                box.locator(":scope > header button.box-toggle").click()
        details = self.page.locator("#GBCTFUENTES details")
        self.assertGreaterEqual(details.count(), 8)
        first = details.first
        summary = first.locator(":scope > summary")
        summary.focus()
        summary.press("Enter")
        expect(first).to_have_attribute("open", "")
        summary.press("Space")
        self.assertFalse(first.evaluate("node=>node.open"))

    def test_story_retains_working_media_and_links_to_tasks_and_collected_sources(self):
        self.open_page(TENERIFE)
        story = self.page.locator('[id="20260823155836ST1CG9"]')
        image = story.locator("img[src*='scene_tenerife']")
        expect(image).to_be_visible()
        self.assertTrue(image.evaluate("img=>img.complete&&img.naturalWidth>0"))
        audio = story.locator("audio")
        expect(audio).to_have_count(2)
        for element in audio.all():
            source = element.get_attribute("src")
            resolved = urljoin(self.page.url, source)
            self.assertTrue(resolved.startswith(self.base), resolved)
            response = self.context.request.get(resolved)
            self.assertTrue(response.ok, source)
            self.assertGreater(len(response.body()), 1024)
        links = story.locator("a[href]")
        destinations = {urlsplit(link.get_attribute("href")).path for link in links.all()}
        for pid in (RETOS, TALLER, SOURCES):
            expected = Path(self.search[pid]["fileUrl"]).name
            self.assertTrue(any(Path(path).name == expected for path in destinations), (pid, destinations))
        source_link = story.locator(f'a[href*="{Path(self.search[SOURCES]["fileUrl"]).name}"]').first
        source_link.click()
        expect(self.page.locator("#fuentes-tenerife")).to_be_visible()
        self.open_page(TENERIFE)
        story = self.page.locator('[id="20260823155836ST1CG9"]')
        task = story.locator(f'a[href$="{Path(self.search[RETOS]["fileUrl"]).name}"]').first
        task.click()
        self.assertTrue(self.page.url.endswith(self.search[RETOS]["fileUrl"]))
        quiz = self.page.locator("[data-idevice-type='quick-questions']").first
        if quiz.is_hidden():
            quiz.locator("xpath=ancestor::article[1]").locator(":scope > header button.box-toggle").click()
            self.page.wait_for_function("()=>window.$exeExport && !$exeExport.isTogglingBox")
        expect(quiz).to_be_visible()
        visible_text = self.page.locator("body").inner_text()
        for author in ("Jesica Fortes Regalado", "Gloria Elsa González Martín", "Cristian García Santana"):
            self.assertNotIn(author, visible_text)
        self.assertFalse(self.external)

    def test_final_extra_is_a_link_without_an_embedded_web_application(self):
        self.open_page(WEB_EXTRA)
        expect(self.page.locator("iframe")).to_have_count(0)
        link = self.page.locator('[id="20261006TEXPLORER440"] a[href^="https://mitomapa-canario.cgarcias.workers.dev/"]')
        expect(link).to_be_visible()
        expect(link).to_have_attribute("target", "_blank")
        self.assertFalse(self.external)


if __name__ == "__main__":
    unittest.main()
