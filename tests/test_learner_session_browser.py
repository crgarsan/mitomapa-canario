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

    def open(self, context, language):
        page = context.new_page()
        page.set_default_timeout(7000)
        page.goto(self.base + ("index-en.html?lang=en" if language == "en" else "index.html?lang=es"),
                  wait_until="networkidle")
        return page

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

    def tools(self, page):
        page.locator("#openTeacher").click()
        page.locator("#teacherToolsTab").click()

    def export(self, page):
        with page.expect_download() as downloaded:
            page.locator("#exportProgress").click()
        return json.loads(Path(downloaded.value.path()).read_text())

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


if __name__ == "__main__":
    unittest.main()
