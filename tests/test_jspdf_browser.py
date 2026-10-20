"""Exercise archive-owned jsPDF loaders and browser-enforced SRI offline.

Run with ``python3 -m unittest discover -s tests -p test_jspdf_browser.py -v``.
Requires Python Playwright and system Chromium; missing tooling is an error.
Every browser URL is intercepted. The exact release fixture is checked against
an independent digest; no CDN, learner state, or real Electron bridge is used.
These tests execute the actual archive modules with their automatic iDevice
initialization suppressed. They cover the loader boundary and real PDF APIs,
not a complete eXeLearning editor or html2canvas/UI export workflow.
"""

import base64
from contextlib import contextmanager
import hashlib
from pathlib import Path
import shutil
import unittest
import zipfile

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/jspdf-4.2.1.umd.min.js"
VERSION = "4.2.1"
CDN_URL = "https://cdn.jsdelivr.net/npm/jspdf@4.2.1/dist/jspdf.umd.min.js"
INTEGRITY = (
    "sha384-qovJwSBbRDPP5cEjCp8S0UP66wrvnjaa60XMOGzTNanrThcr"
    "GfXfnZkvgY8N1KT3"
)
FIXTURE_SHA256 = "e6551fcdc32f09d6853b2c5126d18d01d9447e0da618a41a11ebeee0f6c20d54"
DOCUMENT_URL = "http://127.0.0.1/jspdf-tests.html"
GLOBALS = {
    "progress-report": "$eXeInforme",
    "checklist": "$eXeListaCotejo",
    "rubric": "$rubric",
}

STARTUP = """
window.$ = () => ({}); // Suppress document-ready iDevice initialization.
window.__ready = 0;
window.__errors = 0;
window.__fallback = null;
window.__bridgeCalls = 0;
window.__untrustedExecuted = false;
window.__untrustedSentinel = null;
window.electronAPI = {saveBufferAs: () => {window.__bridgeCalls++;}};
localStorage.setItem('audit-sentinel', 'synthetic-only');
"""

INVOKE = """globalName => {
    window[globalName].ensureJsPDF(
        () => {window.__ready++;},
        () => {window.__errors++; window.__fallback = 'png';}
    );
}"""

TAMPER_PREFIX = b"""
window.__untrustedExecuted = true;
window.__untrustedSentinel = localStorage.getItem('audit-sentinel');
window.electronAPI.saveBufferAs();
localStorage.setItem('audit-sentinel', 'changed-by-untrusted-response');
"""

CREATE_PDF = """async () => {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 96;
    const context = canvas.getContext('2d');
    context.fillStyle = '#fff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#159';
    context.fillRect(8, 8, 64, 32);
    const image = canvas.toDataURL('image/png');
    const pdf = new window.jspdf.jsPDF('p', 'mm', 'a4');
    const properties = pdf.getImageProperties(image);
    pdf.addImage(image, 'PNG', 10, 10, 40, 30);
    pdf.addPage();
    pdf.addImage(image, 'PNG', 10, 10, 40, 30);
    const bytes = new Uint8Array(pdf.output('arraybuffer'));
    const blob = pdf.output('blob');
    const blobBytes = new Uint8Array(await blob.arrayBuffer());
    return {
        version: window.jspdf.jsPDF.version,
        imageWidth: properties.width,
        imageHeight: properties.height,
        pageWidth: pdf.internal.pageSize.getWidth(),
        pageHeight: pdf.internal.pageSize.getHeight(),
        pages: pdf.getNumberOfPages(),
        bytes: bytes.length,
        header: new TextDecoder().decode(bytes.slice(0, 8)),
        blobType: blob.type,
        blobBytes: blobBytes.length,
        blobHeader: new TextDecoder().decode(blobBytes.slice(0, 8)),
        saveType: typeof pdf.save,
    };
}"""


class JsPdfBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = FIXTURE.read_bytes()
        digest = "sha384-" + base64.b64encode(
            hashlib.sha384(cls.release).digest()
        ).decode("ascii")
        if digest != INTEGRITY or hashlib.sha256(cls.release).hexdigest() != FIXTURE_SHA256:
            raise AssertionError("The jsPDF browser fixture differs from the verified release")

        cls.scripts = []
        cls.representatives = {}
        cls.variants = set()
        archives = sorted((ROOT / "downloads").glob("*.elpx"))
        # The 4.7.1 release also preserves the former current ELPX at a
        # versioned public URL. Its loaders need the same browser checks.
        if len(archives) != 13:
            raise AssertionError("Expected all thirteen public native ELPX archives")
        for path in archives:
            with zipfile.ZipFile(path) as archive:
                for kind in GLOBALS:
                    member = f"idevices/{kind}/{kind}.js"
                    if member not in archive.namelist():
                        continue
                    info = archive.getinfo(member)
                    if info.file_size > 1024 * 1024:
                        raise AssertionError(f"Unexpectedly large runtime member: {path.name}!{member}")
                    source = archive.read(info).decode("utf-8")
                    cls.scripts.append((path.name, kind, source))
                    cls.representatives.setdefault(kind, source)
                    cls.variants.add(hashlib.sha256(source.encode("utf-8")).hexdigest())
        # Includes the qualitative-checklist runtime of the current GobCan
        # edition, distinct from the checklist kept in older downloads.
        if len(cls.scripts) != 38 or len(cls.variants) != 5:
            raise AssertionError("Expected 38 native loader copies and five source variants")

        executable = shutil.which("chromium")
        if not executable:
            raise RuntimeError("System Chromium is required for jsPDF SRI browser tests")
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
        except Exception:
            cls.playwright.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    @contextmanager
    def page_for(self, sources, mode="valid"):
        context = self.browser.new_context(service_workers="block")
        page = context.new_page()
        requests = []
        unexpected = []
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        def intercept(route):
            url = route.request.url
            if url == DOCUMENT_URL:
                route.fulfill(
                    status=200,
                    content_type="text/html",
                    body="<!doctype html><html><head></head><body></body></html>",
                )
            elif url == CDN_URL:
                requests.append(url)
                if mode == "offline":
                    route.abort("internetdisconnected")
                    return
                body = TAMPER_PREFIX + self.release if mode == "tampered" else self.release
                headers = {"access-control-allow-origin": "*"}
                if mode == "no-cors":
                    # Playwright adds a permissive ACAO header when none is
                    # supplied. An explicit empty value prevents that helper
                    # and gives Chromium a response with no CORS permission.
                    headers = {"access-control-allow-origin": ""}
                content_type = "application/javascript"
                if mode == "non-javascript":
                    content_type = "application/json"
                    headers["x-content-type-options"] = "nosniff"
                route.fulfill(status=200, content_type=content_type, headers=headers, body=body)
            else:
                unexpected.append(url)
                route.abort()

        context.route("**/*", intercept)
        try:
            page.goto(DOCUMENT_URL)
            page.evaluate(STARTUP)
            for source in sources:
                page.add_script_tag(content=source)
            yield page, requests
        finally:
            context.close()
            self.assertEqual(unexpected, [], "An unapproved browser request was attempted")
            self.assertEqual(page_errors, [], "Archive runtime raised an unexpected JavaScript error")

    def invoke(self, page, kind):
        page.evaluate(INVOKE, GLOBALS[kind])

    def settled(self, page, count=1):
        page.wait_for_function(
            "count => window.__ready + window.__errors === count", arg=count, timeout=10000
        )
        return page.evaluate("({ready:window.__ready, errors:window.__errors})")

    def assert_failure(self, page):
        self.assertEqual(self.settled(page), {"ready": 0, "errors": 1})
        self.assertEqual(
            page.evaluate("""({
                executed: window.__untrustedExecuted,
                observedSentinel: window.__untrustedSentinel,
                bridgeCalls: window.__bridgeCalls,
                sentinel: localStorage.getItem('audit-sentinel'),
                hasJsPdf: Boolean(window.jspdf && window.jspdf.jsPDF),
                fallback: window.__fallback,
            })"""),
            {
                "executed": False,
                "observedSentinel": None,
                "bridgeCalls": 0,
                "sentinel": "synthetic-only",
                "hasJsPdf": False,
                "fallback": "png",
            },
        )

    def test_all_38_archive_loaders_accept_only_the_pinned_release(self):
        for archive, kind, source in self.scripts:
            with self.subTest(archive=archive, module=kind):
                with self.page_for([source]) as (page, requests):
                    self.invoke(page, kind)
                    self.assertEqual(self.settled(page), {"ready": 1, "errors": 0})
                    self.assertEqual(requests, [CDN_URL])
                    self.assertEqual(page.evaluate("window.jspdf.jsPDF.version"), VERSION)
                    self.assertEqual(
                        page.evaluate("""(() => {
                            const script = document.getElementById('jspdf-umd-loader');
                            return {src:script.src, integrity:script.integrity, crossOrigin:script.crossOrigin};
                        })()"""),
                        {"src": CDN_URL, "integrity": INTEGRITY, "crossOrigin": "anonymous"},
                    )

    def test_each_module_supports_real_two_page_png_pdf_output(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source]) as (page, requests):
                    self.invoke(page, kind)
                    self.assertEqual(self.settled(page), {"ready": 1, "errors": 0})
                    result = page.evaluate(CREATE_PDF)
                    self.assertEqual(result["version"], VERSION)
                    self.assertEqual((result["imageWidth"], result["imageHeight"]), (128, 96))
                    self.assertAlmostEqual(result["pageWidth"], 210, places=2)
                    self.assertAlmostEqual(result["pageHeight"], 297, places=2)
                    self.assertEqual(result["pages"], 2)
                    self.assertGreater(result["bytes"], 1000)
                    self.assertEqual(result["header"], "%PDF-1.3")
                    self.assertEqual(result["blobType"], "application/pdf")
                    self.assertEqual(result["blobBytes"], result["bytes"])
                    self.assertEqual(result["blobHeader"], "%PDF-1.3")
                    self.assertEqual(result["saveType"], "function")
                    self.assertEqual(requests, [CDN_URL])

    def test_existing_verified_global_needs_no_download(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source]) as (page, requests):
                    page.add_script_tag(content=self.release.decode("utf-8"))
                    page.evaluate("window.__existingJsPdf = window.jspdf.jsPDF")
                    self.invoke(page, kind)
                    self.assertEqual(self.settled(page), {"ready": 1, "errors": 0})
                    self.assertTrue(page.evaluate("window.jspdf.jsPDF === window.__existingJsPdf"))
                    self.assertEqual(requests, [])
                    self.assertEqual(page.locator("#jspdf-umd-loader").count(), 0)

    def test_concurrent_modules_share_one_script_and_download(self):
        for first, second in [
            ("progress-report", "checklist"),
            ("checklist", "rubric"),
            ("rubric", "progress-report"),
        ]:
            with self.subTest(first=first, second=second):
                sources = [self.representatives[first], self.representatives[second]]
                with self.page_for(sources) as (page, requests):
                    # Both calls happen in one task, before the asynchronous script loads.
                    page.evaluate("""names => {
                        for (const name of names) {
                            window[name].ensureJsPDF(
                                () => {window.__ready++;},
                                () => {window.__errors++;}
                            );
                        }
                    }""", [GLOBALS[first], GLOBALS[second]])
                    self.assertEqual(self.settled(page, 2), {"ready": 2, "errors": 0})
                    self.assertEqual(requests, [CDN_URL])
                    self.assertEqual(page.locator("#jspdf-umd-loader").count(), 1)

    def test_tampered_response_cannot_execute_or_access_synthetic_state(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source], "tampered") as (page, requests):
                    self.invoke(page, kind)
                    self.assert_failure(page)
                    self.assertEqual(requests, [CDN_URL])

    def test_cors_denial_rejects_even_the_verified_release(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source], "no-cors") as (page, requests):
                    self.invoke(page, kind)
                    self.assert_failure(page)
                    self.assertEqual(requests, [CDN_URL])

    def test_non_javascript_response_fails_without_execution(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source], "non-javascript") as (page, requests):
                    self.invoke(page, kind)
                    self.assert_failure(page)
                    self.assertEqual(requests, [CDN_URL])

    def test_offline_failure_reaches_existing_fallback_callback(self):
        for kind, source in self.representatives.items():
            with self.subTest(module=kind):
                with self.page_for([source], "offline") as (page, requests):
                    self.invoke(page, kind)
                    self.assert_failure(page)
                    self.assertEqual(requests, [CDN_URL])


if __name__ == "__main__":
    unittest.main()
