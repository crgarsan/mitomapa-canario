"""Learner orientation, free routes and recovery under the published CSP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSP = next(line.split(':', 1)[1].strip() for line in (ROOT / '_headers').read_text().splitlines() if line.strip().startswith('Content-Security-Policy:'))


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header('Content-Security-Policy', CSP)
        super().end_headers()


class ExpeditionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox', '--disable-dev-shm-usage'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
        self.context.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname in ('127.0.0.1', None) else route.abort())
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.goto(self.base, wait_until='networkidle')

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def test_mobile_home_visual_opens_island_choice(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        visual = self.page.locator('#homeMapLink')
        expect(visual).to_be_visible(timeout=1500)
        visual.click()
        expect(self.page.locator('#exploreMap')).to_be_visible()
        self.assertEqual(urlsplit(self.page.url).fragment, 'islas')

    def test_new_visit_continues_the_saved_workshop(self):
        self.page.goto(self.base + '#isla/tenerife/taller', wait_until='networkidle')
        other = self.context.new_page()
        other.goto(self.base, wait_until='networkidle')
        expect(other.locator('#resumeRoute')).to_contain_text('Tenerife', timeout=1500)
        expect(other.locator('#resumeRoute')).to_contain_text('Taller', timeout=1500)
        other.locator('#resumeRoute').click()
        expect(other).to_have_url(self.base + '#isla/tenerife/taller')

    def test_same_visit_home_continues_the_latest_island_and_step(self):
        for island in ('tenerife','lanzarote'):
            self.page.evaluate('id=>window.MitoMapaNavigation.go(`isla/${id}/taller`)',island)
            self.page.locator('.main-navigation [data-nav="inicio"]').click()
            button=self.page.locator('#resumeRoute')
            expect(button).to_be_visible(timeout=1500)
            expect(button).to_contain_text('Tenerife' if island=='tenerife' else 'Lanzarote')
            expect(button).to_contain_text('Taller')
            button.click()
            expect(self.page).to_have_url(self.base+f'#isla/{island}/taller')

    def test_invalid_resume_data_cannot_choose_a_route_or_execute_markup(self):
        self.page.evaluate("localStorage.setItem('mitomapa-canario-ultimo-apartado-v1', JSON.stringify({routeId:'<img src=x onerror=alert(1)>',step:'constructor',level:'middle'}))")
        other = self.context.new_page()
        other.goto(self.base, wait_until='networkidle')
        self.assertEqual(other.locator('#resumeRoute img').count(), 0)
        self.assertEqual(other.locator('#resumeRoute').is_enabled(), False)
        expect(other.locator('#main .hero')).to_be_visible()

    def test_direct_url_and_back_forward_keep_the_requested_step(self):
        self.page.goto(self.base + '#isla/lanzarote/retos', wait_until='networkidle')
        self.page.locator('#route-lanzarote .route-flow-nav [data-route-flow-target="taller"]').click()
        self.page.locator('.main-navigation [data-nav="juegos"]').click()
        self.page.go_back()
        expect(self.page.locator('#route-lanzarote')).to_have_attribute('data-route-flow-step', 'taller')
        self.page.go_back()
        expect(self.page.locator('#route-lanzarote')).to_have_attribute('data-route-flow-step', 'retos')
        self.page.go_forward()
        expect(self.page.locator('#route-lanzarote')).to_have_attribute('data-route-flow-step', 'taller')

    def test_short_agreed_route_replaces_the_header_collection_goal(self):
        self.page.locator('#openTeacher').click()
        self.page.locator('#teacherToolsTab').click()
        self.page.locator('#agreedRouteSettings').evaluate('node=>node.open=true')
        self.page.locator('[data-agreed-route="tenerife"]').check()
        self.page.locator('[data-agreed-route="la-gomera"]').check()
        self.page.locator('[data-review-route="tenerife"]').check()
        expect(self.page.locator('#progressText')).to_contain_text('1/2', timeout=1500)
        expect(self.page.locator('#passportCount')).to_have_text('0/8')
        self.page.locator('[data-task-route="tenerife"]').fill('Explicar un detalle del cuento y crear una escena')
        self.page.locator('[data-task-route="tenerife"]').press('Tab')
        self.page.locator('#closeTeacher').click()
        self.page.goto(self.base + '#isla/tenerife/cuento', wait_until='networkidle')
        expect(self.page.locator('#route-tenerife .route-session-brief')).to_contain_text('crear una escena')
        self.page.locator('#route-tenerife .route-flow-nav [data-route-flow-target="retos"]').click()
        expect(self.page.locator('#route-tenerife .route-session-brief')).to_be_visible()

    def test_every_island_can_open_creative_closure_without_pieces(self):
        self.page.goto(self.base + '#isla/la-graciosa/taller', wait_until='networkidle')
        self.page.locator('#route-la-graciosa a[href="#crear"]').click(timeout=1500)
        expect(self.page.locator('#creativeClosure')).to_be_visible()
        expect(self.page.locator('#passportCount')).to_have_text('0/8')
        expect(self.page.locator('#finalContent')).not_to_be_visible()

    def test_games_keep_the_eight_piece_extension_last(self):
        self.page.locator('.main-navigation [data-nav="juegos"]').click()
        hrefs = self.page.locator('[data-screen="juegos"] .activity-choice').evaluate_all('nodes=>nodes.map(node=>node.getAttribute("href"))')
        self.assertEqual(hrefs[-1], '#gran-reto')
        self.assertIn('#crear', hrefs)
        expect(self.page.locator('[data-screen="juegos"] a[href="#gran-reto"]')).to_contain_text('opcional')

    def test_settings_label_exists_and_route_cannot_widen_at_enlarged_text(self):
        missing = self.page.locator('[aria-labelledby]').evaluate_all('nodes=>nodes.flatMap(node=>node.getAttribute("aria-labelledby").split(/\\s+/).filter(id=>!document.getElementById(id)))')
        self.assertEqual(missing, [])
        self.page.set_viewport_size({'width': 320, 'height': 800})
        self.page.evaluate("document.documentElement.style.fontSize='200%'")
        for screen in ('inicio', 'juegos', 'crear', 'isla/tenerife/cuento', 'isla/tenerife/retos', 'isla/tenerife/taller'):
            self.page.evaluate('screen=>window.MitoMapaNavigation.go(screen)', screen)
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 321, screen)

    def test_research_feedback_survives_summary_refresh_and_keeps_human_review(self):
        self.page.goto(self.base + '#isla/tenerife/taller', wait_until='networkidle')
        self.page.evaluate("setLearningLevel('advanced')")
        self.page.locator('#activity-tenerife [data-activity-tab="research"]').click()
        self.page.locator('#activity-tenerife .activity-research-question').evaluate_all("nodes=>nodes.forEach(node=>{node.querySelector(`input[value=\"${node.dataset.answer}\"]`).checked=true})")
        self.page.evaluate("checkWorkshopResearch('tenerife')")
        status=self.page.locator('#activity-tenerife [data-activity-panel="research"] .activity-panel-status')
        expect(status).to_contain_text('Preguntas de apoyo comprobadas')
        expect(status).to_contain_text('docente')
        self.assertNotIn('investigación superada', status.inner_text().lower())
        self.page.evaluate("updateWorkshopSummary('tenerife')")
        expect(status).to_contain_text('qué queda sin confirmar')
        self.page.evaluate("Storage.prototype.setItem=()=>{throw new Error('quota')};checkWorkshopResearch('tenerife')")
        expect(status).to_contain_text('Descarguen el seguimiento')

    def test_reset_preserves_source_supports_and_discards_open_answers(self):
        self.page.goto(self.base + '#isla/tenerife/taller', wait_until='networkidle')
        self.page.evaluate("setLearningLevel('advanced')")
        self.page.locator('#activity-tenerife [data-activity-tab="research"]').click()
        self.page.locator('#activity-tenerife [data-research-evidence]').fill('Nota de la visita anterior')
        self.context.add_init_script('window.confirm=()=>true')
        self.page.evaluate('window.confirm=()=>true;resetProgress()')
        expect(self.page.locator('#learning-source-guide-tenerife')).to_have_count(1)
        evidence=self.page.locator('#activity-tenerife [data-research-evidence]')
        self.assertEqual(evidence.input_value(), '')
        self.assertIn('learning-source-reminder-tenerife',evidence.get_attribute('aria-describedby'))


if __name__ == '__main__':
    unittest.main()
