"""Contextual reading controls and real local MP3 source transitions."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import shutil
import threading
import unittest

from playwright.sync_api import sync_playwright

from test_experience_browser import AUDIT_AUDIO, NoRangeHandler, QuietHandler


ROOT = Path(__file__).resolve().parents[1]


class ReadingSupportBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = []
        for handler in (QuietHandler, NoRangeHandler):
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(handler, directory=str(ROOT)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            cls.servers.append((server, thread))
        cls.base, cls.no_range_base = [f"http://127.0.0.1:{server.server_port}/" for server, _ in cls.servers]
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=shutil.which("chromium"),
                                                    args=["--no-sandbox", "--disable-dev-shm-usage"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        for server, thread in cls.servers:
            server.shutdown()
            server.server_close()
            thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 390, "height": 844})
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.add_init_script("document.addEventListener('securitypolicyviolation',e=>{window.__cspViolations ||= [];window.__cspViolations.push(e.violatedDirective)})")

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.page.evaluate("window.__cspViolations||[]"), [])
        self.context.close()

    def open_story(self, base=None):
        self.page.goto((base or self.base) + "#isla/tenerife/cuento", wait_until="networkidle")
        return self.page.locator("#route-tenerife .narrator")

    def open_settings(self, route="tenerife"):
        settings = self.page.locator(f"#route-{route} .reading-settings")
        settings.locator("summary").click()
        return settings

    def play_recording(self):
        narrator = self.open_story()
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>recordingIsSeekable(narrationState.audio)")
        return narrator

    def test_player_and_reading_controls_precede_illustration_and_follow_story_step(self):
        narrator = self.open_story()
        self.assertTrue(self.page.locator("#route-tenerife .reading-support").is_visible())
        self.assertLess(narrator.locator(".narration-play").bounding_box()["y"], 844)
        self.assertTrue(self.page.evaluate("()=>!!(document.querySelector('#route-tenerife .reading-support').compareDocumentPosition(document.querySelector('#route-tenerife .route-figure'))&Node.DOCUMENT_POSITION_FOLLOWING)"))
        self.assertEqual(self.page.locator("#route-tenerife .narrator").count(), 1)
        self.page.locator('#route-tenerife [data-route-flow-target="retos"]').first.click()
        self.assertFalse(self.page.locator("#route-tenerife .reading-support").is_visible())
        self.page.locator('#route-tenerife [data-route-flow-target="cuento"]').first.click()
        self.assertTrue(narrator.is_visible())

    def test_reading_preferences_persist_across_stage_island_and_reload_and_reset(self):
        self.open_story()
        settings = self.open_settings()
        settings.locator(".reading-size").select_option("xlarge")
        settings.locator(".reading-spacing").select_option("spacious")
        settings.locator(".reading-width").select_option("narrow")
        before = self.page.locator("#route-tenerife .story > p").last.evaluate("node=>({size:getComputedStyle(node).fontSize,line:getComputedStyle(node).lineHeight})")
        self.assertEqual(self.page.evaluate("learningLevel"), "middle")
        self.page.evaluate("setLearningLevel('early')")
        after = self.page.locator("#route-tenerife .story > p").last.evaluate("node=>({size:getComputedStyle(node).fontSize,line:getComputedStyle(node).lineHeight})")
        self.assertEqual(after, before)
        self.page.evaluate("location.hash='#isla/la-palma/cuento'")
        self.page.wait_for_selector("#route-la-palma.active")
        self.assertEqual(self.page.locator("#route-la-palma .reading-size").input_value(), "xlarge")
        self.page.reload(wait_until="networkidle")
        settings = self.open_settings("la-palma")
        self.assertEqual(settings.locator(".reading-spacing").input_value(), "spacious")
        self.assertEqual(settings.locator(".reading-width").input_value(), "narrow")
        settings.locator(".reading-reset").click()
        self.assertEqual(settings.locator(".reading-size").input_value(), "normal")
        self.assertEqual(settings.locator(".reading-spacing").input_value(), "normal")
        self.assertEqual(settings.locator(".reading-width").input_value(), "medium")
        self.assertEqual(self.page.evaluate("learningLevel"), "early")
        self.page.reload(wait_until="networkidle")
        self.assertEqual(self.page.locator("#route-la-palma .reading-size").input_value(), "normal")

    def test_settings_work_with_invalid_or_unavailable_storage_and_no_horizontal_overflow(self):
        self.context.add_init_script("localStorage.setItem('mitomapa-canario-lectura-v1',JSON.stringify({size:'<script>',spacing:[],width:'huge'}))")
        self.open_story()
        settings = self.open_settings()
        self.assertEqual(settings.locator(".reading-size").input_value(), "normal")
        self.page.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('Blocked','SecurityError')}}")
        settings.locator(".reading-size").select_option("xlarge")
        settings.locator(".reading-spacing").select_option("spacious")
        self.page.set_viewport_size({"width": 320, "height": 720})
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 320)
        self.assertTrue(settings.locator(".reading-reset").is_visible())
        self.assertFalse(self.page.locator("#storageNotice").is_hidden())

    def test_ambient_choice_is_saved_without_loading_audio_and_preserves_voice_preference(self):
        self.context.add_init_script("if(!localStorage.getItem('mitomapa-canario-preferencias-v3'))localStorage.setItem('mitomapa-canario-preferencias-v3',JSON.stringify({selectedVoiceURI:'voz-elegida'}))")
        requests = []
        self.page.on("request", lambda request: requests.append(request.url) if "/assets/audio/" in request.url else None)
        narrator = self.open_story()
        narrator.locator(".narration-ambient").uncheck()
        self.assertEqual(requests, [])
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('mitomapa-canario-preferencias-v3')).selectedVoiceURI"), "voz-elegida")
        self.page.reload(wait_until="networkidle")
        self.assertFalse(self.page.locator("#route-tenerife .narration-ambient").is_checked())
        self.page.evaluate("location.hash='#isla/la-palma/cuento'")
        self.page.wait_for_selector("#route-la-palma.active")
        self.assertFalse(self.page.locator("#route-la-palma .narration-ambient").is_checked())
        self.assertEqual(requests, [])

    def test_switch_ambient_preserves_real_audio_position_pause_rate_and_single_player(self):
        narrator = self.play_recording()
        narrator.locator(".narration-pause").click()
        narrator.locator(".narration-seek").fill("20")
        narrator.locator(".narration-rate").select_option("0.82")
        self.page.evaluate("window.__originalAudio=narrationState.audio")
        narrator.locator(".narration-ambient").uncheck()
        self.page.wait_for_function("()=>narrationState.audio&&!narrationState.sourceLoading&&recordingIsSeekable(narrationState.audio)&&narrationState.audio.currentTime>=19.9")
        self.assertTrue(self.page.evaluate("narrationState.audio===window.__originalAudio&&narrationState.paused&&narrationState.audio.paused"))
        self.assertTrue(self.page.evaluate("narrationState.audio.src.endsWith('/tenerife.mp3')"))
        self.assertAlmostEqual(self.page.evaluate("narrationState.audio.currentTime"), 20, delta=0.1)
        self.assertEqual(self.page.evaluate("narrationState.audio.playbackRate"), 0.82)
        narrator.locator(".narration-pause").click()
        self.page.wait_for_function("()=>!narrationState.audio.paused")
        position = self.page.evaluate("narrationState.audio.currentTime")
        narrator.locator(".narration-ambient").check()
        self.page.wait_for_function("()=>narrationState.audio&&!narrationState.sourceLoading&&!narrationState.audio.paused&&narrationState.audio.src.endsWith('/tenerife-ambiente.mp3')")
        self.assertAlmostEqual(self.page.evaluate("narrationState.audio.currentTime"), position, delta=1)
        self.assertEqual(self.page.locator("#route-tenerife .is-reading").count(), 0)
        self.page.locator('#route-tenerife [data-route-flow-target="retos"]').first.click()
        self.assertTrue(self.page.evaluate("narrationState.audio===null"))

    def test_switch_ambient_releases_old_blob_and_retains_pause_on_no_range_host(self):
        self.context.add_init_script(AUDIT_AUDIO)
        narrator = self.open_story(self.no_range_base)
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>narrationState.objectUrl&&recordingIsSeekable(narrationState.audio)")
        old_url = self.page.evaluate("narrationState.objectUrl")
        narrator.locator(".narration-pause").click()
        narrator.locator(".narration-seek").fill("20")
        narrator.locator(".narration-ambient").uncheck()
        try:
            self.page.wait_for_function("()=>narrationState.objectUrl&&recordingIsSeekable(narrationState.audio)&&narrationState.audio.currentTime>=19.9")
        except Exception:
            print(self.page.evaluate("()=>({source:narrationState.audio?.src,position:narrationState.audio?.currentTime,seekable:recordingIsSeekable(narrationState.audio),loading:narrationState.sourceLoading,url:narrationState.objectUrl,ready:narrationState.audio?.readyState,network:narrationState.audio?.networkState,duration:narrationState.audio?.duration,buffered:narrationState.audio?Array.from({length:narrationState.audio.buffered.length},(_,i)=>[narrationState.audio.buffered.start(i),narrationState.audio.buffered.end(i)]):null,error:narrationState.audio?.error?.message,audit:window.__audioAudit})"))
            raise
        self.assertNotEqual(self.page.evaluate("narrationState.objectUrl"), old_url)
        self.assertTrue(self.page.evaluate("narrationState.paused&&narrationState.audio.paused"))
        self.assertIn(old_url, self.page.evaluate("window.__audioAudit.revoked"))
        narrator.locator(".narration-stop").click()
        self.assertEqual(self.page.evaluate("window.__audioAudit.revoked"), self.page.evaluate("window.__audioAudit.created"))

    def check_cancel_pending_ambient_change(self, change_route):
        narrator = self.play_recording()
        pending = []
        self.page.route("**/assets/audio/tenerife.mp3", lambda route: pending.append(route))
        with self.page.expect_request(lambda request: request.url.endswith("/tenerife.mp3")):
            narrator.locator(".narration-ambient").uncheck()
        self.page.wait_for_function("()=>narrationState.sourceLoading")
        if change_route:
            self.page.evaluate("location.hash='#isla/la-palma/cuento'")
            self.page.wait_for_selector("#route-la-palma.active")
        else:
            narrator.locator(".narration-stop").click()
        for route in pending:
            route.fulfill(status=200, content_type="audio/mpeg", body=(ROOT / "assets/audio/tenerife.mp3").read_bytes())
        self.page.wait_for_timeout(100)
        self.assertTrue(self.page.evaluate("narrationState.audio===null"))

    def test_stop_during_ambient_loading_never_resumes_old_audio(self):
        self.check_cancel_pending_ambient_change(False)

    def test_route_change_during_ambient_loading_never_resumes_old_audio(self):
        self.check_cancel_pending_ambient_change(True)

    def test_failed_seek_preparation_after_ambient_change_keeps_new_track_usable(self):
        narrator = self.open_story(self.no_range_base)
        narrator.locator(".narration-play").click()
        self.page.wait_for_function("()=>narrationState.objectUrl&&recordingIsSeekable(narrationState.audio)")
        narrator.locator(".narration-pause").click()
        narrator.locator(".narration-seek").fill("20")

        def reject_only_auxiliary_download(route):
            if route.request.resource_type == "fetch":
                route.abort()
            else:
                route.continue_()

        self.page.route("**/assets/audio/tenerife.mp3", reject_only_auxiliary_download)
        narrator.locator(".narration-ambient").uncheck()
        self.page.wait_for_function("()=>document.querySelector('#route-tenerife .narration-status').textContent.includes('No se ha podido')")
        self.assertFalse(self.page.evaluate("narrationState.sourceLoading"))
        self.assertTrue(self.page.evaluate("narrationState.paused&&narrationState.audio.paused"))
        self.assertIn("principio", narrator.locator(".narration-status").text_content())
        narrator.locator(".narration-pause").click()
        self.page.wait_for_function("()=>!narrationState.paused&&!narrationState.audio.paused")


if __name__ == "__main__":
    unittest.main()
