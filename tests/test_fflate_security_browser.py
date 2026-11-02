"""Run the actual native HTTP export loader with the pinned browser UMD."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from media_browser import launch_media_browser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from sync_current_elpx import build_current


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class NativeFflateExportBrowserTests(unittest.TestCase):
    def test_http_export_preserves_text_binary_unicode_and_store_entries(self):
        files, _ = build_current()
        fixture = {'content.xml': b'<ode>native fixture</ode>',
                   'datos/cuento-ñ.txt': 'Texto legítimo áéí'.encode(),
                   'datos/texto-grande.txt': ('Texto legítimo áéí — ' * 12000).encode(),
                   'datos/audio.mp3': bytes([0,255,17,0])}
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as playwright:
            root=Path(folder)
            for name,payload in {**fixture,
                    'libs/fflate/fflate.umd.js':files['libs/fflate/fflate.umd.js'],
                    'libs/exe_elpx_download/exe_elpx_download.js':files['libs/exe_elpx_download/exe_elpx_download.js']}.items():
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
            (root/'manifest.js').write_text('window.__ELPX_MANIFEST__='+json.dumps({'files':list(fixture),'basePath':'/','projectTitle':'Ensayo'}))
            (root/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Exportación nativa aislada</title>'
                '<script src="manifest.js"></script><script src="libs/fflate/fflate.umd.js"></script>'
                '<script src="libs/exe_elpx_download/exe_elpx_download.js"></script>')
            server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(root)))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            browser=launch_media_browser(playwright)
            try:
                context=browser.new_context(accept_downloads=True)
                context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname in ('127.0.0.1',None) else route.abort())
                page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='networkidle')
                with page.expect_download() as pending:
                    page.evaluate('()=>window.downloadElpx({filename:"ensayo-nativo"})')
                download=pending.value
                self.assertEqual(download.suggested_filename,'ensayo-nativo.elpx')
                with ZipFile(BytesIO(Path(download.path()).read_bytes())) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(set(archive.namelist()),set(fixture))
                    for name,payload in fixture.items():
                        self.assertEqual(archive.read(name),payload)
                    self.assertEqual(archive.getinfo('datos/audio.mp3').compress_type,0)
                self.assertEqual(errors,[])
                context.close()
            finally:
                browser.close();server.shutdown();server.server_close();thread.join()

    def test_native_http_api_exports_every_reconstructed_project_member(self):
        files, _ = build_current()
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as playwright:
            root = Path(folder)
            for name, payload in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            browser = launch_media_browser(playwright)
            try:
                context = browser.new_context(accept_downloads=True)
                # Playwright aborts every */favicon.ico request when interception
                # is enabled. This local project needs that real member in its ZIP.
                page = context.new_page()
                page.goto(f'http://127.0.0.1:{server.server_port}/html/creditos-y-descarga.html',
                          wait_until='networkidle')
                # The editable archive retains eXe's exe-package:elp placeholder;
                # editor/export rendering is a separate integration boundary.
                # Exercise its unchanged native loader with the real inventory.
                page.add_script_tag(url=f'http://127.0.0.1:{server.server_port}/libs/elpx-manifest.js')
                with page.expect_download(timeout=60000) as pending:
                    page.evaluate('()=>window.downloadElpx()')
                download = pending.value
                self.assertTrue(download.suggested_filename.endswith('.elpx'))
                with ZipFile(BytesIO(Path(download.path()).read_bytes())) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(set(archive.namelist()), set(files))
                    for name, payload in files.items():
                        with self.subTest(member=name):
                            self.assertEqual(archive.read(name), payload)
                context.close()
            finally:
                browser.close()
                server.shutdown()
                server.server_close()
                thread.join()
