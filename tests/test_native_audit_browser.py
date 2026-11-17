"""Reproduce the audited native navigation/choice defects in a real browser."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import shutil
import sys
import threading
import unittest
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_current_elpx import build_current


class NativeAuditBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, _ = build_current()
        source = cls.files['search_index.js'].decode()
        cls.search = json.loads(source[source.index('{'):].rstrip(';\n'))
        files = cls.files

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = unquote(urlsplit(self.path).path).removeprefix('/')
                if path.startswith('rea/'):
                    path = path.removeprefix('rea/')
                if not path:
                    path = 'index.html'
                if path not in files:
                    self.send_error(404)
                    return
                payload = files[path]
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_):
                pass

        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=shutil.which('chromium'), args=['--no-sandbox', '--disable-dev-shm-usage'],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 1000})
        self.context.route('**/*', self.route)
        self.page = self.context.new_page()
        self.failed = []
        self.errors = []
        self.context.on('response', lambda response: self.failed.append(response.url) if response.status >= 400 else None)
        self.context.on('page', lambda page: page.on('pageerror', lambda error: self.errors.append(str(error))))
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def route(self, route):
        parsed = urlsplit(route.request.url)
        if parsed.hostname == '127.0.0.1' or parsed.scheme in {'blob', 'data'}:
            route.continue_()
        else:
            self.errors.append('Unexpected external request: ' + route.request.url)
            route.abort()

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])
        self.assertEqual(self.failed, [])

    def test_native_previews_resolve_assets_under_root_and_subdirectory(self):
        for prefix in ('', 'rea/'):
            for path in ('index.html', 'html/guia-didactica.html', 'html/tenerife-dacil-y-el-regreso-de-magec.html'):
                with self.subTest(prefix=prefix, page=path):
                    self.page.goto(self.base + prefix + path, wait_until='networkidle')
                    expect(self.page.locator('main')).to_be_visible()
                    expect(self.page.locator('#skipNav')).to_have_text('Saltar al contenido')

    def test_all_eight_vocabulary_games_offer_correctly_spelled_choices(self):
        for index in range(1, 9):
            with self.subTest(island=index):
                path = self.search[f'GBC20261006RETOS{index}']['fileUrl']
                self.page.goto(self.base + 'rea/' + path, wait_until='networkidle')
                game = self.page.locator('[data-idevice-type="complete"]')
                if game.is_hidden():
                    game.locator('xpath=ancestor::article[1]').locator('.box-toggle').click()
                start = game.locator('[id^="cmptStartGame-"]')
                if start.is_visible():
                    start.click()
                self.assertGreater(game.locator('select.CMPT-Select').count(), 0)
                options = set(game.locator('select.CMPT-Select option').all_text_contents())
                self.assertFalse(options & {'Cilios', 'Nueclolo', 'vivian', 'pequeno', 'encendio', 'dia', 'desaparecio'})
                self.assertIn('Selecciona', game.locator('.completa-instructions').inner_text())
                if index == 3:
                    self.assertIn('guardamos su memoria', options)
                if index == 8:
                    self.assertIn('desaparecía', options)

    def test_teacher_links_open_the_local_pauta_and_complete_protocol(self):
        self.page.goto(self.base + 'rea/html/guia-didactica.html', wait_until='networkidle')
        guide = self.page.locator('[id="20260823155837TGUID1"]')
        guide.locator('xpath=ancestor::article[1]').locator('.box-toggle').click()
        guide.locator('summary').filter(has_text='Ejemplo curricular del itinerario corto').click()
        with self.page.expect_popup() as opened:
            guide.get_by_role('link', name='Abrir la pauta cualitativa', exact=True).click()
        pauta = opened.value
        pauta.wait_for_load_state('networkidle')
        self.assertTrue(pauta.url.endswith('/rea/content/resources/Rubrica_lectura_MitoMapa_4_0.html'))
        expect(pauta.locator('h1')).to_have_text('Pauta cualitativa de lectura e impresión')
        pauta.close()
        guide.get_by_role('link', name='Abrir el protocolo de pilotaje y su hoja imprimible', exact=True).click()
        self.page.wait_for_load_state('networkidle')
        self.assertTrue(self.page.url.endswith('/rea/content/resources/PROTOCOLO_PILOTAJE.html'))
        expect(self.page.locator('h1')).to_have_text('Preparar una primera aplicación de MitoMapa')
        expect(self.page.locator('table tbody tr')).to_have_count(5)
        image = self.page.locator('img[alt="CC BY-SA 4.0"]')
        self.assertTrue(image.evaluate('element=>element.complete&&element.naturalWidth>0'))
        self.page.get_by_role('link', name='← Volver a la guía docente').click()
        self.page.wait_for_load_state('networkidle')
        expect(self.page.locator('h1.page-title')).to_have_text('Orientaciones docentes')


if __name__ == '__main__':
    unittest.main()
