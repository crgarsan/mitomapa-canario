"""Local, fictitious learner-session regressions in both published languages."""
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest

from playwright.sync_api import expect, sync_playwright
from media_browser import launch_media_browser
from test_persistent_state_browser import QuietCspHandler

ROOT = Path(__file__).resolve().parents[1]
RETENTION_MS = 15 * 24 * 60 * 60 * 1000
TEST_TIME_MS = 1795176000000


class LearnerSessionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietCspHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = launch_media_browser(cls.playwright)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def open(self, context, language, *, now=None, clock=False):
        page = context.new_page()
        page.set_default_timeout(7000)
        if clock:
            page.clock.install(time=now / 1000)
        elif now is not None:
            page.clock.set_fixed_time(now / 1000)
        page.goto(self.base + ("index-en.html?lang=en" if language == "en" else "index.html?lang=es"),
                  wait_until="networkidle")
        self.wait_for_app(page)
        return page

    def wait_for_app(self, page):
        # The core loads after retention preparation. DOM readiness avoids
        # evaluating an expression under CSP or mistaking hoisted functions
        # for a mounted application.
        page.locator("body.navigation-ready").wait_for(state="visible")

    def retention(self, page):
        self.wait_for_app(page)
        return page.evaluate("""() => {
            const generation = localStorage.getItem('mitomapa-canario-sesion-v1');
            const key = 'mitomapa-canario-caducidad-v1';
            const scoped = generation ? 'mitomapa-canario-sesion-v1:' + generation + ':' + key : key;
            return {generation, record: JSON.parse(localStorage.getItem(scoped))};
        }""")

    def set_retention_start(self, page, started_at):
        page.evaluate("""startedAt => {
            const generation = localStorage.getItem('mitomapa-canario-sesion-v1');
            const key = 'mitomapa-canario-caducidad-v1';
            const scoped = generation ? 'mitomapa-canario-sesion-v1:' + generation + ':' + key : key;
            localStorage.setItem(scoped, JSON.stringify({startedAt}));
        }""", started_at)

    def workshop(self, page):
        self.wait_for_app(page)
        page.evaluate("window.MitoMapaNavigation.go('isla/tenerife/taller')")
        page.locator('#activity-tenerife [data-activity-tab="creation"]').click()
        return page.locator('#activity-tenerife [data-primary-text]')

    def payload(self):
        return {"app": "mitomapa-canario", "schemaVersion": 1, "learningLevel": "advanced",
                "learnerName": "Equipo ficticio B", "progress": {},
                "workshop": {"routes": {"tenerife": {"text": "Trabajo ficticio B"}}}}

    def seed(self, page):
        page.evaluate("""() => {
            localStorage.setItem('mitomapa-canario-preferencias-v3', JSON.stringify({
              learnerName:'Equipo ficticio A', learningLevel:'advanced'}));
            localStorage.setItem('mitomapa-canario-cuaderno-v1', JSON.stringify({
              routes:{tenerife:{text:'Trabajo ficticio A'}}}));
        }""")
        page.reload(wait_until="networkidle")
        self.wait_for_app(page)

    def tools(self, page):
        self.wait_for_app(page)
        page.locator("#openTeacher").click()
        page.locator("#teacherToolsTab").click()

    def export(self, page):
        with page.expect_download() as downloaded:
            page.locator("#exportProgress").click()
        return json.loads(Path(downloaded.value.path()).read_text())

    def deny_storage_reads(self, page, boundary):
        # Change only the browser-storage boundary. Installing on this page
        # keeps the denial in effect after the app's guarded reload, while a
        # fresh page in the same context can later retry real storage access.
        scripts = {
            "getItem": """(() => {
                const get = Storage.prototype.getItem;
                Storage.prototype.getItem = function() {
                    throw new DOMException('Fictitious read denial', 'SecurityError');
                };
                window.restoreTestStorageAccess = () => { Storage.prototype.getItem = get; };
            })();""",
            "localStorage": """(() => {
                const descriptor = Object.getOwnPropertyDescriptor(window, 'localStorage');
                Object.defineProperty(window, 'localStorage', {
                    configurable: true,
                    get() { throw new DOMException('Fictitious access denial', 'SecurityError'); }
                });
                window.restoreTestStorageAccess = () => {
                    Object.defineProperty(window, 'localStorage', descriptor);
                };
            })();""",
        }
        script = scripts[boundary]
        page.add_init_script(script)
        page.evaluate(script)

    def assert_expired_read_denied_work_is_empty(self, page, context, language, deadline):
        # Old work must disappear without any user action that could itself
        # trigger a session check.
        expect(page.locator('#activity-tenerife [data-primary-text]')).not_to_be_visible()
        self.wait_for_app(page)
        expect(page.locator("#storageNotice")).to_be_visible()
        self.assertFalse(page.evaluate("document.body.inert"))
        # Read denial also prevents restoring the preferred stage. Choose it
        # through the real control before checking the lazy workshop fields.
        page.locator("a.brand").click()
        page.locator("#readingSettings > summary").click()
        page.locator('.experience-tools button[data-learning-level="advanced"]').click()
        expect(self.workshop(page)).to_have_value("")
        self.tools(page)
        expect(page.locator("#teacherLearnerName")).to_have_value("")
        result = self.export(page)
        self.assertEqual(result["learnerName"], "")
        self.assertFalse(result["workshop"]["routes"].get("tenerife", {}).get("text"))
        fields = page.locator("input, textarea").evaluate_all("nodes => nodes.map(node => node.value).join('|')")
        for old_value in ("Equipo ficticio A", "Trabajo ficticio A", "Equipo ficticio B", "Trabajo ficticio B"):
            self.assertNotIn(old_value, fields)

        # The page-specific denial remains active over another reload. A blank
        # but usable learner view must remain, rather than reviving the old DOM.
        page.reload(wait_until="domcontentloaded")
        self.wait_for_app(page)
        expect(page.locator("#storageNotice")).to_be_visible()
        page.locator("a.brand").click()
        page.locator("#readingSettings > summary").click()
        page.locator('.experience-tools button[data-learning-level="advanced"]').click()
        expect(self.workshop(page)).to_have_value("")
        self.tools(page)
        expect(page.locator("#teacherLearnerName")).to_have_value("")
        self.assertEqual(self.export(page)["learnerName"], "")

        # Once storage is readable again, its still-expired record must also
        # prevent the saved learner from reappearing in a new document.
        recovered = self.open(context, language, now=deadline + 1)
        recovered.locator("a.brand").click()
        recovered.locator("#readingSettings > summary").click()
        recovered.locator('.experience-tools button[data-learning-level="advanced"]').click()
        expect(self.workshop(recovered)).to_have_value("")
        self.tools(recovered)
        expect(recovered.locator("#teacherLearnerName")).to_have_value("")
        result = self.export(recovered)
        self.assertEqual(result["learnerName"], "")
        self.assertFalse(result["workshop"]["routes"].get("tenerife", {}).get("text"))

    def test_reset_and_import_replace_work_across_languages(self):
        for source, other_language in (("es", "en"), ("en", "es")):
            with self.subTest(source=source), self.browser.new_context(reduced_motion="reduce") as context:
                context.add_init_script("window.confirm=()=>true")
                first = self.open(context, source)
                self.seed(first)
                second = self.open(context, other_language)
                self.tools(second)
                expect(second.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                self.tools(first)
                first.locator("#resetProgress").click()
                expect(first.locator("#teacherLearnerName")).to_have_value("")
                expect(second.locator("#teacherDialog")).not_to_be_visible()
                self.tools(second)
                expect(second.locator("#teacherLearnerName")).to_have_value("")
                self.assertEqual(self.export(second)["learnerName"], "")
                first.locator("#importProgressFile").set_input_files({"name": "ficticio.json",
                    "mimeType": "application/json", "buffer": json.dumps(self.payload()).encode()})
                expect(first.locator("#teacherLearnerName")).to_have_value("Equipo ficticio B")
                expect(second.locator("#teacherDialog")).not_to_be_visible()
                self.tools(second)
                result = self.export(second)
                self.assertEqual(result["learnerName"], "Equipo ficticio B")
                self.assertEqual(result["workshop"]["routes"]["tenerife"]["text"], "Trabajo ficticio B")

    def test_import_failure_preserves_existing_work_in_both_languages(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                context.add_init_script("window.confirm=()=>true")
                page = self.open(context, language)
                self.seed(page)
                self.tools(page)
                before = page.evaluate("({...localStorage})")
                page.evaluate("""() => {
                    const set = Storage.prototype.setItem; let writes = 0;
                    Storage.prototype.setItem = function(key,value) {
                      if (++writes > 2) throw new DOMException('Full','QuotaExceededError');
                      return set.call(this,key,value);
                    };
                }""")
                page.locator("#importProgressFile").set_input_files({"name": "ficticio.json",
                    "mimeType": "application/json", "buffer": json.dumps(self.payload()).encode()})
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                page.wait_for_function("() => !document.getElementById('teacherImportStatus').textContent.includes('correctamente') && document.getElementById('teacherImportStatus').textContent.length > 0")
                self.assertEqual(page.evaluate("({...localStorage})"), before)
                self.assertEqual(self.export(page)["workshop"]["routes"]["tenerife"]["text"], "Trabajo ficticio A")

    def test_reset_invalidates_a_pending_import_in_both_languages(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                context.add_init_script("window.confirm=()=>true")
                page = self.open(context, language)
                self.seed(page)
                self.tools(page)
                page.evaluate("""text => {
                  const file=new File([text],'ficticio.json',{type:'application/json'});
                  file.text=()=>new Promise(resolve=>window.finishImport=()=>resolve(text));
                  window.pendingImport=importProgressFile(file);
                }""", json.dumps(self.payload()))
                page.evaluate("() => resetProgress()")
                page.evaluate("() => {finishImport();return pendingImport;}")
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                self.assertFalse(self.export(page)["workshop"]["routes"].get("tenerife", {}).get("text"))

    def test_stale_tabs_cannot_export_or_print_old_work_in_both_languages(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language)
                self.seed(page)
                downloads, prints = [], []
                page.on("download", lambda download: downloads.append(download))
                page.expose_function("recordUnexpectedPrint", lambda: prints.append(True))
                page.evaluate("""() => {
                  window.print=()=>window.recordUnexpectedPrint();
                  localStorage.setItem('mitomapa-canario-sesion-v1','l-'+'c'.repeat(32));
                  exportProgress();printPassport();
                }""")
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                self.assertEqual(downloads, [])
                self.assertEqual(prints, [])

    def test_native_print_hides_work_when_session_cannot_be_verified(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page=self.open(context,language)
                self.seed(page)
                page.evaluate("window.MitoMapaNavigation.go('isla/tenerife/taller')")
                page.locator('#activity-tenerife [data-activity-tab="creation"]').click()
                expect(page.locator('#activity-tenerife [data-primary-text]')).to_have_value('Trabajo ficticio A')
                page.emulate_media(media="print")
                visibility=page.evaluate("""() => {
                  const get=Storage.prototype.getItem;
                  Storage.prototype.getItem=function(key){
                    if(key==='mitomapa-canario-sesion-v1')throw new DOMException('Denied','SecurityError');
                    return get.call(this,key);
                  };
                  window.dispatchEvent(new Event('beforeprint'));
                  return getComputedStyle(document.querySelector('#activity-tenerife [data-primary-text]')).visibility;
                }""")
                self.assertEqual(visibility,'hidden')
                page.evaluate("window.dispatchEvent(new Event('afterprint'))")
                page.emulate_media(media="screen")
                self.assertEqual(page.locator('#activity-tenerife [data-primary-text]').input_value(),'Trabajo ficticio A')

    def test_fifteen_day_expiry_removes_old_work_before_startup_in_both_languages(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language)
                self.seed(page)
                page.evaluate("""() => {
                    const generation = localStorage.getItem('mitomapa-canario-sesion-v1');
                    const key = 'mitomapa-canario-caducidad-v1';
                    const scoped = generation ? 'mitomapa-canario-sesion-v1:' + generation + ':' + key : key;
                    localStorage.setItem(scoped, JSON.stringify({startedAt: Date.now() - 1296000000}));
                    localStorage.setItem('mitomapa-language', 'en');
                    localStorage.setItem('mitomapa-canario-lectura-v1', JSON.stringify({scale: 1.4}));
                    localStorage.setItem('unrelated-application', 'keep');
                }""")
                page.reload(wait_until="networkidle")
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                expect(page.locator("body")).to_have_attribute("data-learning-level", "advanced")
                exported = self.export(page)
                self.assertEqual(exported["learnerName"], "")
                self.assertFalse(exported["workshop"]["routes"].get("tenerife", {}).get("text"))
                remaining = page.evaluate("JSON.stringify({...localStorage})")
                self.assertNotIn("Equipo ficticio A", remaining)
                self.assertNotIn("Trabajo ficticio A", remaining)
                self.assertEqual(page.evaluate("localStorage.getItem('unrelated-application')"), "keep")
                self.assertEqual(page.evaluate("localStorage.getItem('mitomapa-language')"), language)
                self.assertEqual(page.evaluate("JSON.parse(localStorage.getItem('mitomapa-canario-lectura-v1')).scale"), 1.4)

    def test_undated_work_gets_one_fixed_window_across_reloads_and_languages(self):
        for language, other_language in (("es", "en"), ("en", "es")):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                # Model an installation predating the retention feature.
                page.evaluate("localStorage.removeItem('mitomapa-canario-caducidad-v1')")
                page.reload(wait_until="networkidle")
                original = self.retention(page)
                self.assertEqual(original["record"], {"startedAt": TEST_TIME_MS})

                page.clock.set_fixed_time((TEST_TIME_MS + 24 * 60 * 60 * 1000) / 1000)
                page.reload(wait_until="networkidle")
                self.assertEqual(self.retention(page), original)
                other = self.open(context, other_language, now=TEST_TIME_MS + 7 * 24 * 60 * 60 * 1000)
                self.tools(other)
                expect(other.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                self.assertEqual(self.retention(other), original)
                other.locator("#closeTeacher").click()
                self.workshop(other).fill("Trabajo ficticio A revisado")
                other.clock.set_fixed_time((TEST_TIME_MS + 14 * 24 * 60 * 60 * 1000) / 1000)
                other.reload(wait_until="domcontentloaded")
                expect(self.workshop(other)).to_have_value("Trabajo ficticio A revisado")
                self.assertEqual(self.retention(other), original)
                self.tools(other)
                self.assertEqual(self.export(other)["workshop"]["routes"]["tenerife"]["text"],
                                 "Trabajo ficticio A revisado")

    def test_focus_keeps_work_before_deadline_and_expires_at_exact_deadline(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.set_retention_start(page, TEST_TIME_MS)
                original = self.retention(page)
                page.clock.set_fixed_time((TEST_TIME_MS + RETENTION_MS - 1) / 1000)
                page.evaluate("window.dispatchEvent(new Event('focus'))")
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                self.assertEqual(self.retention(page), original)

                page.clock.set_fixed_time((TEST_TIME_MS + RETENTION_MS) / 1000)
                page.evaluate("window.dispatchEvent(new Event('focus'))")
                expect(page.locator("#teacherDialog")).not_to_be_visible()
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                result = self.export(page)
                self.assertEqual(result["learnerName"], "")
                self.assertFalse(result["workshop"]["routes"].get("tenerife", {}).get("text"))
                self.assertNotEqual(self.retention(page)["generation"], original["generation"])

    def test_active_timer_expires_open_work_without_a_focus_event(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language, now=TEST_TIME_MS, clock=True)
                self.seed(page)
                # Keep a short amount of real retention time left, then advance
                # browser timers; no direct call to the retention API is made.
                now = page.evaluate("Date.now()")
                self.set_retention_start(page, now - RETENTION_MS + 30000)
                page.reload(wait_until="networkidle")
                expect(self.workshop(page)).to_have_value("Trabajo ficticio A")
                page.clock.fast_forward(30001)
                page.wait_for_function("() => location.hash === '#inicio'")
                expect(self.workshop(page)).to_have_value("")
                self.tools(page)
                self.assertEqual(self.export(page)["learnerName"], "")

    def test_active_timer_expires_work_when_storage_reads_become_denied(self):
        for language in ("es", "en"):
            for boundary in ("getItem", "localStorage"):
                with self.subTest(language=language, boundary=boundary), self.browser.new_context() as context:
                    page = self.open(context, language, now=TEST_TIME_MS, clock=True)
                    self.seed(page)
                    deadline = page.evaluate("Date.now()") + 30000
                    self.set_retention_start(page, deadline - RETENTION_MS)
                    page.reload(wait_until="networkidle")
                    expect(self.workshop(page)).to_have_value("Trabajo ficticio A")
                    self.deny_storage_reads(page, boundary)
                    page.clock.fast_forward(30001)
                    self.assert_expired_read_denied_work_is_empty(page, context, language, deadline)

    def test_resume_expires_read_denied_work_without_waiting_for_its_timer(self):
        for language in ("es", "en"):
            for event in ("focus", "pageshow", "visibilitychange"):
                with self.subTest(language=language, event=event), self.browser.new_context() as context:
                    # A fixed Date advances the deadline while real timers do
                    # not run forward: only the browser resume handler fires.
                    page = self.open(context, language, now=TEST_TIME_MS)
                    self.seed(page)
                    self.set_retention_start(page, TEST_TIME_MS)
                    expect(self.workshop(page)).to_have_value("Trabajo ficticio A")
                    self.deny_storage_reads(page, "getItem")
                    deadline = TEST_TIME_MS + RETENTION_MS
                    page.clock.set_fixed_time(deadline / 1000)
                    page.evaluate("""event => {
                        (event === 'visibilitychange' ? document : window).dispatchEvent(new Event(event));
                    }""", event)
                    self.assert_expired_read_denied_work_is_empty(page, context, language, deadline)

    def test_temporary_read_denial_before_deadline_preserves_work_and_fixed_window(self):
        for language in ("es", "en"):
            for boundary in ("getItem", "localStorage"):
                with self.subTest(language=language, boundary=boundary), self.browser.new_context() as context:
                    page = self.open(context, language, now=TEST_TIME_MS)
                    self.seed(page)
                    self.set_retention_start(page, TEST_TIME_MS)
                    original = self.retention(page)
                    field = self.workshop(page)
                    expect(field).to_have_value("Trabajo ficticio A")
                    self.deny_storage_reads(page, boundary)
                    deadline = TEST_TIME_MS + RETENTION_MS
                    page.clock.set_fixed_time((deadline - 1) / 1000)
                    page.evaluate("window.dispatchEvent(new Event('focus'))")
                    expect(field).to_be_visible()
                    expect(field).to_have_value("Trabajo ficticio A")
                    expect(page.locator("#storageNotice")).to_be_visible()
                    self.assertFalse(page.evaluate("document.body.inert"))

                    page.evaluate("window.restoreTestStorageAccess()")
                    page.evaluate("window.dispatchEvent(new Event('focus'))")
                    self.assertEqual(self.retention(page), original)
                    self.tools(page)
                    expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                    self.assertEqual(self.export(page)["workshop"]["routes"]["tenerife"]["text"],
                                     "Trabajo ficticio A")

    def test_imported_session_keeps_its_new_deadline_when_reads_later_fail(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                context.add_init_script("window.confirm=()=>true")
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.set_retention_start(page, TEST_TIME_MS)
                old_deadline = TEST_TIME_MS + RETENTION_MS
                imported_at = old_deadline - 30000
                page.clock.set_fixed_time(imported_at / 1000)
                self.tools(page)
                page.locator("#importProgressFile").set_input_files({"name": "ficticio.json",
                    "mimeType": "application/json", "buffer": json.dumps(self.payload()).encode()})
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio B")
                imported = self.retention(page)
                self.assertEqual(imported["record"], {"startedAt": imported_at})
                page.locator("#closeTeacher").click()
                field = self.workshop(page)
                expect(field).to_have_value("Trabajo ficticio B")
                self.deny_storage_reads(page, "getItem")

                # A successful import replaces the former retention window.
                # Denial afterward must not revive that former deadline.
                page.clock.set_fixed_time(old_deadline / 1000)
                page.evaluate("window.dispatchEvent(new Event('focus'))")
                expect(field).to_be_visible()
                expect(field).to_have_value("Trabajo ficticio B")
                expect(page.locator("#storageNotice")).to_be_visible()
                deadline = imported_at + RETENTION_MS
                page.clock.set_fixed_time(deadline / 1000)
                page.evaluate("window.dispatchEvent(new Event('focus'))")
                self.assert_expired_read_denied_work_is_empty(page, context, language, deadline)

    def test_expired_second_tab_cannot_resave_or_export_its_old_work(self):
        for language, other_language in (("es", "en"), ("en", "es")):
            with self.subTest(language=language), self.browser.new_context() as context:
                first = self.open(context, language, now=TEST_TIME_MS)
                self.seed(first)
                self.set_retention_start(first, TEST_TIME_MS)
                second = self.open(context, other_language, now=TEST_TIME_MS)
                expect(self.workshop(second)).to_have_value("Trabajo ficticio A")
                downloads = []
                second.on("download", lambda download: downloads.append(download))
                # A suspended tab may resume with its old controls before its
                # timer or storage handler runs. The ordinary input and export
                # handlers must check the deadline themselves.
                # Keep the advanced date through the guarded page reload too.
                second.clock.set_fixed_time((TEST_TIME_MS + RETENTION_MS) / 1000)
                second.evaluate("""() => {
                    const input = document.querySelector('#activity-tenerife [data-primary-text]');
                    input.value = 'Trabajo ficticio A resucitado';
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    exportProgress();
                }""")
                expect(second).to_have_url(self.base +
                    ("index-en.html?lang=en#inicio" if other_language == "en" else "index.html?lang=es#inicio"))
                self.assertEqual(downloads, [])
                expect(self.workshop(second)).to_have_value("")
                self.tools(second)
                self.assertFalse(self.export(second)["workshop"]["routes"].get("tenerife", {}).get("text"))
                self.tools(first)
                expect(first.locator("#teacherLearnerName")).to_have_value("")
                saved = first.evaluate("JSON.stringify({...localStorage})")
                self.assertNotIn("Trabajo ficticio A", saved)
                self.assertNotIn("Equipo ficticio A", saved)

    def test_core_response_crossing_deadline_cleans_old_work_and_can_save_again(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.set_retention_start(page, TEST_TIME_MS)
                original = self.retention(page)
                deadline = TEST_TIME_MS + RETENTION_MS
                page.clock.set_fixed_time((deadline - 1) / 1000)
                crossed_deadline = []

                def delayed_core(route):
                    # Fetch the real core, but deliver it only once the fixed
                    # deadline has passed after the initial preparation.
                    response = route.fetch()
                    page.clock.set_fixed_time(deadline / 1000)
                    crossed_deadline.append(True)
                    route.fulfill(response=response)

                core = "scripts-en.js" if language == "en" else "scripts.js"
                page.route("**/" + core + "?*", delayed_core, times=1)
                page.reload(wait_until="domcontentloaded")
                page.wait_for_function("""previous =>
                    localStorage.getItem('mitomapa-canario-sesion-v1') !== previous
                """, arg=original["generation"])
                self.wait_for_app(page)
                self.assertEqual(crossed_deadline, [True])
                expect(self.workshop(page)).to_have_value("")
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                result = self.export(page)
                self.assertEqual(result["learnerName"], "")
                self.assertFalse(result["workshop"]["routes"].get("tenerife", {}).get("text"))
                saved = page.evaluate("JSON.stringify({...localStorage})")
                self.assertNotIn("Trabajo ficticio A", saved)
                self.assertNotIn("Equipo ficticio A", saved)

                page.locator("#teacherLearnerName").fill("Equipo ficticio nuevo")
                page.locator("#teacherLearnerName").press("Tab")
                page.locator("#closeTeacher").click()
                self.workshop(page).fill("Trabajo ficticio posterior a la caducidad")
                page.reload(wait_until="domcontentloaded")
                expect(self.workshop(page)).to_have_value("Trabajo ficticio posterior a la caducidad")
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio nuevo")

    def test_successful_import_and_reset_start_new_windows_without_export_schema_changes(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                context.add_init_script("window.confirm=()=>true")
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.tools(page)
                original = self.retention(page)
                export_fields = set(self.export(page))
                imported_at = TEST_TIME_MS + 24 * 60 * 60 * 1000
                page.clock.set_fixed_time(imported_at / 1000)
                page.locator("#importProgressFile").set_input_files({"name": "ficticio.json",
                    "mimeType": "application/json", "buffer": json.dumps(self.payload()).encode()})
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio B")
                imported = self.retention(page)
                self.assertNotEqual(imported["generation"], original["generation"])
                self.assertEqual(imported["record"], {"startedAt": imported_at})
                exported = self.export(page)
                self.assertEqual(set(exported), export_fields)
                self.assertEqual(exported["schemaVersion"], 1)
                self.assertEqual(exported["workshop"]["routes"]["tenerife"]["text"], "Trabajo ficticio B")

                reset_at = imported_at + 24 * 60 * 60 * 1000
                page.clock.set_fixed_time(reset_at / 1000)
                page.locator("#resetProgress").click()
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                reset = self.retention(page)
                self.assertNotEqual(reset["generation"], imported["generation"])
                self.assertEqual(reset["record"], {"startedAt": reset_at})

    def test_rejected_and_cancelled_imports_keep_existing_deadline(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                context.add_init_script("window.confirm=()=>true")
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.tools(page)
                original = self.retention(page)
                page.clock.set_fixed_time((TEST_TIME_MS + 24 * 60 * 60 * 1000) / 1000)
                page.locator("#importProgressFile").set_input_files({"name": "invalido.json",
                    "mimeType": "application/json", "buffer": b'{"app":"different-resource"}'})
                expect(page.locator("#teacherImportStatus")).not_to_have_text("")
                expect(page.locator("#teacherLearnerName")).to_have_value("Equipo ficticio A")
                self.assertEqual(self.retention(page), original)

                page.evaluate("window.confirm=()=>false")
                page.locator("#importProgressFile").set_input_files({"name": "ficticio.json",
                    "mimeType": "application/json", "buffer": json.dumps(self.payload()).encode()})
                expect(page.locator("#teacherImportStatus")).to_contain_text("cancel")
                self.assertEqual(self.retention(page), original)
                self.assertEqual(self.export(page)["learnerName"], "Equipo ficticio A")

    def test_expired_startup_with_storage_mutations_denied_does_not_reveal_old_work(self):
        for language in ("es", "en"):
            with self.subTest(language=language), self.browser.new_context() as context:
                page = self.open(context, language, now=TEST_TIME_MS)
                self.seed(page)
                self.set_retention_start(page, TEST_TIME_MS - RETENTION_MS)
                page.add_init_script("""(() => {
                    Storage.prototype.setItem = function() {
                        throw new DOMException('Denied', 'SecurityError');
                    };
                    Storage.prototype.removeItem = function() {
                        throw new DOMException('Denied', 'SecurityError');
                    };
                    document.addEventListener('DOMContentLoaded', () => {
                        window.bootLearnerFields = [...document.querySelectorAll('input, textarea')]
                            .map(node => node.value).join('|');
                    });
                })();""")
                page.reload(wait_until="networkidle")
                self.wait_for_app(page)
                expect(page.locator("#storageNotice")).to_be_visible()
                # Denial really prevented physical deletion; only the empty
                # in-memory learner may be shown or exported in this tab.
                remaining = page.evaluate("JSON.stringify({...localStorage})")
                self.assertIn("Equipo ficticio A", remaining)
                self.assertIn("Trabajo ficticio A", remaining)
                self.assertNotIn("Equipo ficticio A", page.evaluate("window.bootLearnerFields"))
                self.assertNotIn("Trabajo ficticio A", page.evaluate("window.bootLearnerFields"))
                expect(self.workshop(page)).to_have_value("")
                initialized_fields = page.evaluate("""[...document.querySelectorAll('input, textarea')]
                    .map(node => node.value).join('|')""")
                self.assertNotIn("Equipo ficticio A", initialized_fields)
                self.assertNotIn("Trabajo ficticio A", initialized_fields)
                self.tools(page)
                expect(page.locator("#teacherLearnerName")).to_have_value("")
                result = self.export(page)
                self.assertEqual(result["learnerName"], "")
                self.assertFalse(result["workshop"]["routes"].get("tenerife", {}).get("text"))


if __name__ == "__main__":
    unittest.main()
