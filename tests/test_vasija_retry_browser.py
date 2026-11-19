"""Recover vessel metadata on reopening, using the real ES/EN UI and CSP."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CSP = next(line.split(":", 1)[1].strip() for line in (ROOT / "_headers").read_text().splitlines()
           if line.strip().startswith("Content-Security-Policy:"))
ISLANDS = {"tenerife", "gran-canaria", "la-palma", "lanzarote", "fuerteventura", "la-gomera", "el-hierro"}
EDITIONS = (
    ("es", "index.html#recursos", "assets/vasija/ficha.json", "assets/vasijas/coleccion.json"),
    ("en", "index-en.html?lang=en#recursos", "assets/vasija/ficha-en.json", "assets/vasijas/coleccion-en.json"),
)


def json_response(payload):
    def handler(route):
        route.fulfill(status=200, content_type="application/json", body=payload)
    return handler


class QuietCspHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        gate = self.server.delays.get(urlsplit(self.path).path)
        if gate is not None:
            gate.wait(timeout=15)
        super().do_GET()

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class VasijaRetryBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietCspHandler, directory=str(ROOT)))
        cls.server.delays = {}
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

    @contextmanager
    def edition(self, entry, ficha, catalog):
        with self.browser.new_context(viewport={"width": 1280, "height": 900}) as context:
            context.route("**/*", lambda route: route.continue_()
                          if route.request.url.startswith(self.base) else route.abort())
            page = context.new_page()
            page.set_default_timeout(3000)
            counts = {ficha: 0, catalog: 0}
            errors = []

            def count(request):
                for path in counts:
                    if request.url == self.base + path:
                        counts[path] += 1

            page.on("request", count)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(self.base + entry, wait_until="networkidle")
            expect(page.locator("#resourceVasija > summary")).to_be_visible()
            try:
                yield page, counts
            finally:
                for gate in self.server.delays.values():
                    gate.set()
                self.server.delays.clear()
            self.assertEqual(errors, [])

    def open(self, page):
        page.locator("#resourceVasija > summary").click()
        expect(page.locator("#resourceVasija")).to_have_attribute("open", "")
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")

    def reopen(self, page):
        page.locator("#resourceVasija > summary").click()
        expect(page.locator("#resourceVasija")).not_to_have_attribute("open", "")
        # The toggle event is queued by the browser; let closing finish before
        # opening again rather than coalescing both native events.
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
        self.open(page)

    def ready(self, page, expected):
        expect(page.locator("#resourceVasija [data-vasija-open]:visible")).to_have_count(expected)
        expect(page.locator("#vasijaSelect option")).to_have_count(expected)

    def all_models(self, page):
        self.ready(page, 7)
        self.assertEqual(set(page.locator("#vasijaSelect option").evaluate_all(
            "options => options.map(option => option.value)")), ISLANDS)

    def fallbacks(self, page, islands):
        for island in islands:
            tile = page.locator(f'[data-vasija-open="{island}"]').locator("xpath=ancestor::li[1]")
            expect(tile.locator("[data-vasija-still]")).to_be_visible()
            expect(tile.locator("a[download]")).to_be_visible()
            self.assertTrue(tile.locator("a[download]").get_attribute("href").endswith(".stl"))

    def test_reopening_retries_only_the_failed_catalog_and_deduplicates_options(self):
        # A permanent attempted flag, refetching the successful ficha, or adding
        # its option again would break this recovery without a page reload.
        for language, entry, ficha, catalog in EDITIONS:
            with self.subTest(language=language), self.edition(entry, ficha, catalog) as (page, counts):
                page.route(self.base + catalog, lambda route: route.abort(), times=1)
                self.open(page)
                self.ready(page, 1)
                self.fallbacks(page, ISLANDS - {"tenerife"})
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 1, catalog: 1})
                self.reopen(page)
                self.all_models(page)
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 1, catalog: 2})
                for _ in range(2):
                    self.reopen(page)
                    self.all_models(page)
                    page.wait_for_load_state("networkidle")
                    self.assertEqual(counts, {ficha: 1, catalog: 2})

    def test_reopening_retries_only_the_failed_tenerife_ficha(self):
        # Caching both loaders as one result loses Tenerife after its own error.
        for language, entry, ficha, catalog in EDITIONS:
            with self.subTest(language=language), self.edition(entry, ficha, catalog) as (page, counts):
                page.route(self.base + ficha, lambda route: route.abort(), times=1)
                self.open(page)
                self.ready(page, 6)
                self.fallbacks(page, {"tenerife"})
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 1, catalog: 1})
                self.reopen(page)
                self.all_models(page)
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 2, catalog: 1})

    def test_reopening_while_requests_are_in_flight_does_not_duplicate_them(self):
        # Resetting the attempt flag on close starts parallel metadata fetches.
        for language, entry, ficha, catalog in EDITIONS:
            with self.subTest(language=language), self.edition(entry, ficha, catalog) as (page, counts):
                gate = threading.Event()
                self.server.delays = {"/" + ficha: gate, "/" + catalog: gate}
                with page.expect_request(self.base + ficha), page.expect_request(self.base + catalog):
                    self.open(page)
                self.fallbacks(page, ISLANDS)
                self.reopen(page)
                page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
                self.assertEqual(counts, {ficha: 1, catalog: 1})
                gate.set()
                self.all_models(page)
                self.reopen(page)
                self.all_models(page)
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 1, catalog: 1})

    def test_reopening_retries_a_failed_resource_while_the_other_is_in_flight(self):
        # A global in-flight guard loses a retry even after that resource has
        # failed. A stale first error must not overwrite the recovered ficha.
        for language, entry, ficha, catalog in EDITIONS:
            for failed, delayed in ((ficha, catalog), (catalog, ficha)):
                with self.subTest(language=language, failed=failed), self.edition(entry, ficha, catalog) as (page, counts):
                    gate = threading.Event()
                    self.server.delays = {"/" + delayed: gate}
                    page.route(self.base + failed, lambda route: route.abort(), times=1)
                    with page.expect_event("requestfailed", predicate=lambda request: request.url == self.base + failed):
                        self.open(page)
                    page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
                    self.reopen(page)
                    page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
                    gate.set()
                    self.all_models(page)
                    self.assertEqual(counts, {failed: 2, delayed: 1})
                    expected = json.loads((ROOT / ficha).read_text())["modelDimensions"]
                    expect(page.locator('#vasijaTenerifeFicha [data-vasija-field="modelDimensions"]')).to_have_text(expected)
                    self.reopen(page)
                    self.all_models(page)
                    page.wait_for_load_state("networkidle")
                    self.assertEqual(counts, {failed: 2, delayed: 1})

    def test_partial_collection_keeps_valid_models_and_retries_missing_ones(self):
        # Valid items remain available, but a partial list cannot permanently
        # cache the collection or duplicate those items on the next attempt.
        for language, entry, ficha, catalog in EDITIONS:
            with self.subTest(language=language), self.edition(entry, ficha, catalog) as (page, counts):
                partial_catalog = json.loads((ROOT / catalog).read_text())[:1]
                page.route(self.base + catalog, json_response(json.dumps(partial_catalog)), times=1)
                self.open(page)
                self.ready(page, 2)
                page.wait_for_load_state("networkidle")
                self.reopen(page)
                self.all_models(page)
                page.wait_for_load_state("networkidle")
                self.assertEqual(counts, {ficha: 1, catalog: 2})

    def test_persistent_failure_retries_once_per_reopen_without_an_automatic_loop(self):
        # A retry timer or recursive retry would produce extra failed requests
        # while the same UI remains open, instead of waiting for the next visit.
        for language, entry, ficha, catalog in EDITIONS:
            with self.subTest(language=language), self.edition(entry, ficha, catalog) as (page, counts):
                page.route(self.base + catalog, lambda route: route.abort())
                self.open(page)
                for attempt in (1, 2, 3):
                    self.ready(page, 1)
                    page.wait_for_load_state("networkidle")
                    self.assertEqual(counts, {ficha: 1, catalog: attempt})
                    self.fallbacks(page, ISLANDS - {"tenerife"})
                    if attempt < 3:
                        self.reopen(page)

    def test_invalid_catalog_remains_retryable_without_exposing_invalid_models(self):
        # A fulfilled response is not a usable collection if JSON, its shape,
        # or the required fields of the six expected models are invalid.
        invalid = ("{", '{"items":[]}', '[{"id":"gran-canaria","title":"Incomplete"}]')
        for language, entry, ficha, catalog in EDITIONS:
            for payload in invalid:
                with self.subTest(language=language, payload=payload), self.edition(entry, ficha, catalog) as (page, counts):
                    page.route(self.base + catalog, json_response(payload), times=1)
                    self.open(page)
                    self.ready(page, 1)
                    self.fallbacks(page, ISLANDS - {"tenerife"})
                    page.wait_for_load_state("networkidle")
                    self.reopen(page)
                    self.all_models(page)
                    page.wait_for_load_state("networkidle")
                    self.assertEqual(counts, {ficha: 1, catalog: 2})

    def test_invalid_tenerife_ficha_keeps_existing_validators_and_can_recover(self):
        # Treating a failed validation as success either exposes untrusted
        # metadata or prevents replacing the unavailable ficha on reopening.
        for language, entry, ficha, catalog in EDITIONS:
            valid = json.loads((ROOT / ficha).read_text())
            invalid = (("malformed JSON", "{"),
                       ("missing required field", json.dumps({**valid, "adaptations": ""})),
                       ("unsafe reference", json.dumps({**valid, "referenceUrl": "http://example.invalid/"})),
                       ("wrong badge", json.dumps({**valid, "badgePath": "unexpected.webp"})))
            for kind, payload in invalid:
                with self.subTest(language=language, invalid=kind), self.edition(entry, ficha, catalog) as (page, counts):
                    page.route(self.base + ficha, json_response(payload), times=1)
                    self.open(page)
                    self.ready(page, 6)
                    self.fallbacks(page, {"tenerife"})
                    page.wait_for_load_state("networkidle")
                    self.reopen(page)
                    self.all_models(page)
                    page.wait_for_load_state("networkidle")
                    self.assertEqual(counts, {ficha: 2, catalog: 1})
                    page.locator("#resourceVasija .vasija-ficha > summary").click()
                    expect(page.locator("#vasijaBadgeFigure")).to_be_visible()


if __name__ == "__main__":
    unittest.main()
