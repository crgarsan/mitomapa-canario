"""Regression checks for learner changes, feedback and recorded narration.

Runs the actual local resource in Chromium. No public site is modified or used.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import threading
import unittest

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CSP = next(line.split(":", 1)[1].strip() for line in (ROOT / "_headers").read_text().splitlines() if line.strip().startswith("Content-Security-Policy:"))


class QuietHandler(SimpleHTTPRequestHandler):
    supports_ranges = True

    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()

    def do_GET(self):
        # Exercise both servers with Range and ordinary HTTP 200 static hosts.
        path = Path(self.translate_path(self.path))
        if not self.supports_ranges or path.suffix != ".mp3" or not path.is_file():
            return super().do_GET()
        size = path.stat().st_size
        match = re.fullmatch(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        start = int(match[1]) if match else 0
        end = min(int(match[2]), size - 1) if match and match[2] else size - 1
        if start >= size or end < start:
            self.send_error(416)
            return
        self.send_response(206 if match else 200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if match:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with path.open("rb") as stream:
            stream.seek(start)
            try:
                self.wfile.write(stream.read(end - start + 1))
            except (BrokenPipeError, ConnectionResetError):
                pass


class NoRangeHandler(QuietHandler):
    supports_ranges = False


AUDIT_AUDIO = """
(()=>{
if(window.__audioAudit)return;
window.__audioAudit={created:[],revoked:[],fetches:[],signals:[],settled:0};
const nativeCreate=URL.createObjectURL.bind(URL),nativeRevoke=URL.revokeObjectURL.bind(URL);
URL.createObjectURL=blob=>{const url=nativeCreate(blob);window.__audioAudit.created.push(url);return url;};
URL.revokeObjectURL=url=>{window.__audioAudit.revoked.push(url);nativeRevoke(url);};
const nativeFetch=window.fetch.bind(window);
window.fetch=(source,options={})=>{
 window.__audioAudit.fetches.push(String(source));window.__audioAudit.signals.push(options.signal);
 return nativeFetch(source,options).then(
  response=>{window.__audioAudit.settled++;return response;},
  error=>{window.__audioAudit.settled++;throw error;}
 );
};
})();
"""


class ExperienceBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.no_range_server = ThreadingHTTPServer(("127.0.0.1", 0), partial(NoRangeHandler, directory=str(ROOT)))
        cls.no_range_thread = threading.Thread(target=cls.no_range_server.serve_forever, daemon=True)
        cls.no_range_thread.start()
        cls.no_range_base = f"http://127.0.0.1:{cls.no_range_server.server_port}/"
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
        cls.no_range_server.shutdown()
        cls.no_range_server.server_close()
        cls.no_range_thread.join()

    def setUp(self):
        self.context = self.browser.new_context(accept_downloads=True)
        self.context.add_init_script("window.confirm=()=>true")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.base + "#isla/tenerife/retos", wait_until="networkidle")

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def answer_quiz(self, kind, values):
        box = self.page.locator(f"#{kind}-tenerife")
        if kind == "quiz":
            self.page.locator("#route-tenerife [data-route-flow-quiz-target=verdad]").click()
        for index, value in enumerate(values):
            box.locator(f'.question').nth(index).locator(f'input[value="{value}"]').check()
            if index < len(values) - 1:
                box.locator(".question-next").click()
        box.locator(".check-source,.check-quiz").click()

    def test_reset_clears_answers_pagers_rewards_and_teacher_table(self):
        self.answer_quiz("source", [1, 2, 1])
        self.answer_quiz("quiz", ["false", "true", "true"])
        self.page.locator("#dismissBadge").click()
        self.assertEqual(self.page.locator("#passportCount").text_content(), "1/8")
        self.page.locator("#openTeacher").click()
        self.page.evaluate("document.getElementById('resetProgress').click()")
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.assertEqual(self.page.locator(".route input[type=radio]:checked").count(), 0)
        self.assertEqual(self.page.locator(".route .feedback.ok,.route .feedback.ko,.reward.show,.route-step.complete").count(), 0)
        self.assertEqual(self.page.locator("#source-tenerife .question-counter").text_content(), "Pregunta 1 de 3")
        self.assertEqual(self.page.locator("#quiz-tenerife .question-counter").text_content(), "Pregunta 1 de 3")
        self.assertEqual(self.page.locator("#source-tenerife .source-status").text_content(), "")
        self.assertEqual(self.page.locator("#quiz-tenerife .quiz-status").text_content(), "")
        cells = self.page.locator("#teacherProgressBody tr").first.locator("td").all_text_contents()
        self.assertEqual(cells[:2], ["Pendiente", "Pendiente"])
        self.assertEqual(cells[3], "Pendiente")
        self.assertEqual(self.page.locator("#teacherProgressBody [data-review-route]:checked").count(), 0)
        self.page.reload(wait_until="networkidle")
        self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
        self.assertEqual(self.page.locator(".route input[type=radio]:checked").count(), 0)

    def test_importing_legacy_progress_replaces_other_learners_answers(self):
        self.answer_quiz("source", [1, 2, 1])
        self.page.evaluate("""()=>{
          document.querySelector('#finalMatchGrid select').value='tenerife';
          document.querySelector('#finalMatchGrid .final-match-feedback').textContent='Correcto.';
          document.querySelector('[data-feedback-open=liked]').value='Opinión anterior';
        }""")
        payload = {
            "app": "mitomapa-canario", "version": "4.4.2", "learnerName": "Otra persona",
            "learningLevel": "middle", "progress": {"sourcePassed": [], "truthPassed": [], "earned": []},
        }
        self.page.locator("#importProgressFile").set_input_files(
            {"name": "anterior.json", "mimeType": "application/json", "buffer": json.dumps(payload).encode()}
        )
        self.page.wait_for_function("()=>document.getElementById('teacherImportStatus').textContent.includes('correctamente')")
        self.assertEqual(self.page.locator("#source-tenerife input:checked").count(), 0)
        self.assertEqual(self.page.locator("#source-tenerife .source-status").text_content(), "")
        self.assertEqual(self.page.locator("#source-tenerife .question-counter").text_content(), "Pregunta 1 de 3")
        self.assertEqual(self.page.locator("#teacherLearnerName").input_value(), "Otra persona")
        self.assertEqual(self.page.locator("#finalMatchGrid select").first.input_value(), "")
        self.assertEqual(self.page.locator("#finalMatchGrid .final-match-feedback").first.text_content(), "")
        self.assertEqual(self.page.locator("[data-feedback-open=liked]").input_value(), "")

    def test_wrong_answers_reveal_and_focus_the_first_problem(self):
        for kind, values in [("source", [0, 2, 1]), ("quiz", ["true", "true", "true"])]:
            self.answer_quiz(kind, values)
            box = self.page.locator(f"#{kind}-tenerife")
            self.assertEqual(box.locator(".question-counter").text_content(), "Pregunta 1 de 3")
            self.assertTrue(box.locator(".question").first.locator("legend").evaluate("node=>node===document.activeElement"))
            self.assertNotEqual(box.locator(".feedback.ko").first.text_content(), "")
            self.assertEqual(box.locator(".feedback.ok").count(), 2)

    def test_feedback_accepts_comment_only_and_rejects_blank_space(self):
        self.page.goto(self.base + "#recursos", wait_until="networkidle")
        # Open the feedback details if the current navigation folds it.
        self.page.locator("#studentFeedback").evaluate("node=>{const details=node.closest('details');if(details)details.open=true}")
        self.page.locator("[data-feedback-open=liked]").fill("   \n   ")
        self.page.locator("#downloadFeedback").click()
        self.assertIn("escribe un comentario", self.page.locator("#feedbackStatus").text_content())
        self.page.locator("[data-feedback-open=liked]").fill("  Me ayudó escuchar el cuento.  ")
        with self.page.expect_download() as download_info:
            self.page.locator("#downloadFeedback").click()
        response = json.loads(Path(download_info.value.path()).read_text())
        self.assertEqual(response["liked"], "Me ayudó escuchar el cuento.")
        self.assertTrue(all(item["response"] is None for item in response["ratings"]))
        self.assertEqual(response["schemaVersion"], 1)
        self.assertEqual(response["version"], json.loads((ROOT / "VERSION.json").read_text())["web_version"])

    def test_recording_seek_pause_stop_and_island_change(self):
        requests = []
        self.page.on("request", lambda request: requests.append(request.url) if "/assets/audio/" in request.url else None)
        self.page.goto(self.base + "#isla/tenerife/cuento", wait_until="networkidle")
        narrator = self.page.locator("#route-tenerife .narrator")
        self.assertEqual(requests, [])
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())
        self.assertTrue(narrator.locator(".narration-back").is_disabled())
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>!document.querySelector('#route-tenerife .narration-seek').disabled")
        self.assertIsNone(self.page.evaluate("narrationState.objectUrl"))
        narrator.locator(".narration-pause").click()
        self.assertIn("Continuar", narrator.locator(".narration-pause").text_content())
        narrator.locator(".narration-seek").fill("20")
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:20")
        narrator.locator(".narration-seek").press("ArrowRight")
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:21")
        narrator.locator(".narration-seek").fill("20")
        narrator.locator(".narration-back").click()
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:10")
        narrator.locator(".narration-forward").click()
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:20")
        self.assertIn("0:20 de", narrator.locator(".narration-seek").get_attribute("aria-valuetext"))
        self.assertNotEqual(narrator.locator(".narration-duration").text_content(), "--:--")
        narrator.locator(".narration-rate").select_option("0.82")
        self.assertEqual(self.page.evaluate("narrationState.audio.playbackRate"), 0.82)
        narrator.locator(".narration-stop").click()
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:00")
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>!document.querySelector('#route-tenerife .narration-seek').disabled")
        self.page.evaluate("location.hash='#isla/la-palma/cuento'")
        self.page.wait_for_function("()=>document.querySelector('#route-la-palma.active')!==null")
        self.assertTrue(self.page.evaluate("narrationState.audio===null"))
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())
        self.assertIn("cambiar", narrator.locator(".narration-status").text_content())

    def test_failed_recording_leaves_position_controls_disabled(self):
        self.page.route("**/assets/audio/**", lambda route: route.abort())
        self.page.goto(self.base + "#isla/tenerife/cuento", wait_until="networkidle")
        narrator = self.page.locator("#route-tenerife .narrator")
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>document.querySelector('#route-tenerife .narration-status').textContent.includes('No se pudo')")
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())
        self.assertTrue(narrator.locator(".narration-back").is_disabled())
        self.assertTrue(narrator.locator(".narration-forward").is_disabled())
        self.assertTrue(narrator.locator(".narration-play").is_enabled())
        self.assertTrue(self.page.evaluate("narrationState.audio===null"))

    def open_no_range_recording(self, hold_fetch=False):
        self.context.add_init_script(AUDIT_AUDIO)
        pending = []
        if hold_fetch:
            def hold_audio_fetch(route):
                if route.request.resource_type != "fetch":
                    route.continue_()
                    return
                pending.append(route)
                self.page.evaluate("()=>{window.__audioRouteHeld=true;}")
            self.page.route("**/assets/audio/**", hold_audio_fetch)
        self.no_range_navigation = getattr(self, "no_range_navigation", 0) + 1
        response = self.page.goto(self.no_range_base + f"?audio-test={self.no_range_navigation}#isla/tenerife/cuento", wait_until="networkidle")
        self.assertIn("connect-src 'self'", response.headers["content-security-policy"])
        self.assertIn("blob:", response.headers["content-security-policy"])
        self.assertEqual(self.page.evaluate("window.__audioAudit.fetches.length"), 0)
        narrator = self.page.locator("#route-tenerife .narrator")
        narrator.locator(".narration-rate").select_option("0.82")
        narrator.locator(".narration-play").click()
        if hold_fetch:
            self.page.wait_for_function("()=>window.__audioRouteHeld===true")
            self.assertEqual(self.page.evaluate("window.__audioAudit.fetches.length"), 1)
            self.assertEqual(len(pending), 1)
            self.assertFalse(self.page.evaluate("recordingIsSeekable(narrationState.audio)"))
        return narrator, pending

    def test_server_without_ranges_prepares_seekable_audio_and_releases_blob(self):
        narrator, _ = self.open_no_range_recording()
        self.page.wait_for_function("()=>narrationState.objectUrl&&recordingIsSeekable(narrationState.audio)")
        self.assertEqual(self.page.evaluate("window.__audioAudit.fetches"), ["assets/audio/tenerife-ambiente.mp3"])
        self.assertEqual(self.page.evaluate("narrationState.audio.playbackRate"), 0.82)
        narrator.locator(".narration-pause").click()
        narrator.locator(".narration-seek").fill("20")
        narrator.locator(".narration-forward").click()
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:30")
        narrator.locator(".narration-back").click()
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:20")
        narrator.locator(".narration-stop").click()
        self.assertEqual(self.page.evaluate("window.__audioAudit.revoked"), self.page.evaluate("window.__audioAudit.created"))
        self.assertEqual(self.page.evaluate("window.__audioAudit.created.length"), 1)
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())

    def test_no_range_fallback_preserves_pause_resume_position_and_rate(self):
        narrator, pending = self.open_no_range_recording(hold_fetch=True)
        narrator.locator(".narration-pause").click()
        self.assertTrue(self.page.evaluate("narrationState.paused&&narrationState.audio.paused"))
        narrator.locator(".narration-pause").click()
        self.page.wait_for_function("()=>!narrationState.paused&&!narrationState.audio.paused")
        narrator.locator(".narration-pause").click()
        position = self.page.evaluate("narrationState.audio.currentTime")
        narrator.locator(".narration-rate").select_option("1.08")
        pending[0].fulfill(status=200, content_type="audio/mpeg", body=(ROOT / "assets/audio/tenerife-ambiente.mp3").read_bytes())
        self.page.wait_for_function("()=>narrationState.objectUrl&&recordingIsSeekable(narrationState.audio)")
        self.assertTrue(self.page.evaluate("narrationState.paused&&narrationState.audio.paused"))
        self.assertAlmostEqual(self.page.evaluate("narrationState.audio.currentTime"), position, delta=0.1)
        self.assertEqual(self.page.evaluate("narrationState.audio.playbackRate"), 1.08)
        narrator.locator(".narration-seek").fill("25")
        self.assertEqual(narrator.locator(".narration-current").text_content(), "0:25")

    def test_stopping_or_changing_island_aborts_pending_seek_preparation(self):
        for change_island in [False, True]:
            narrator, pending = self.open_no_range_recording(hold_fetch=True)
            if change_island:
                self.page.evaluate("location.hash='#isla/la-palma/cuento'")
                self.page.wait_for_function("()=>document.querySelector('#route-la-palma.active')!==null")
            else:
                narrator.locator(".narration-stop").click()
            self.assertTrue(self.page.evaluate("narrationState.audio===null"))
            self.assertTrue(self.page.evaluate("window.__audioAudit.signals[0].aborted"))
            pending[0].fulfill(status=200, content_type="audio/mpeg", body=(ROOT / "assets/audio/tenerife-ambiente.mp3").read_bytes())
            self.page.wait_for_function("()=>window.__audioAudit.settled===1")
            self.assertEqual(self.page.evaluate("window.__audioAudit.created"), [])
            self.assertTrue(self.page.evaluate("narrationState.audio===null"))
            self.page.unroute("**/assets/audio/**")

    def test_blob_autoplay_rejection_reuses_prepared_audio_on_direct_click(self):
        self.context.add_init_script("""
        const nativePlay=HTMLMediaElement.prototype.play;
        HTMLMediaElement.prototype.play=function(...args){
         if(this.src.startsWith('blob:')&&!window.__blobRejected){
          window.__blobRejected=true;
          return Promise.reject(new DOMException('Use a new gesture','NotAllowedError'));
         }
         return nativePlay.apply(this,args);
        };
        """)
        narrator, _ = self.open_no_range_recording()
        self.page.wait_for_function("()=>narrationState.awaitingGesture===true")
        self.assertIn("Pulsa Reproducir o Continuar", narrator.locator(".narration-status").text_content())
        self.page.evaluate("window.__preparedAudio=narrationState.audio")
        original = self.page.evaluate("narrationState.objectUrl")
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>!narrationState.paused&&!narrationState.awaitingGesture&&!narrationState.audio.paused")
        self.assertTrue(self.page.evaluate("window.__preparedAudio===narrationState.audio"))
        self.assertEqual(self.page.evaluate("narrationState.objectUrl"), original)
        self.assertEqual(self.page.evaluate("window.__audioAudit.fetches.length"), 1)
        self.assertEqual(self.page.evaluate("window.__audioAudit.created.length"), 1)
        narrator.locator(".narration-stop").click()
        self.assertEqual(self.page.evaluate("window.__audioAudit.revoked"), [original])

    def test_failed_seek_download_keeps_original_narration_available(self):
        narrator, pending = self.open_no_range_recording(hold_fetch=True)
        pending[0].abort()
        self.page.wait_for_function("()=>document.querySelector('#route-tenerife .narration-status').textContent.includes('Puedes seguir escuchando')")
        self.assertTrue(self.page.evaluate("narrationState.audio!==null&&!narrationState.audio.paused"))
        self.assertIsNone(self.page.evaluate("narrationState.objectUrl"))
        self.assertTrue(narrator.locator(".narration-seek").is_disabled())
        narrator.locator(".narration-pause").click()
        self.assertTrue(self.page.evaluate("narrationState.audio.paused"))

    def test_progress_and_draft_export_use_distribution_version(self):
        expected = json.loads((ROOT / "VERSION.json").read_text())["web_version"]
        with self.page.expect_download() as download_info:
            self.page.evaluate("document.getElementById('exportProgress').click()")
        payload = json.loads(Path(download_info.value.path()).read_text())
        self.assertEqual(payload["version"], expected)
        self.assertEqual(payload["schemaVersion"], 1)
        with self.page.expect_download() as download_info:
            self.page.evaluate("downloadWorkshopDraft('tenerife')")
        text = Path(download_info.value.path()).read_text()
        self.assertIn(f"MitoMapa {expected}", text)
        self.assertIn("Versión del esquema de exportación: 1", text)


if __name__ == "__main__":
    unittest.main()
