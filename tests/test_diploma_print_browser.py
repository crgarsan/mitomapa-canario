"""The generic diploma requires eight current-stage pieces and fits one A4 PDF.

Uses real progress imports and Chrome PDFs; requires Playwright and Poppler.
The progress fixture contains fictitious data earned through the interface.
"""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/diploma-earned-progress.json'
GENERIC_RECOGNITION = ('Se concede este diploma a la persona que ha explorado el MitoMapa canario, '
                       'reuniendo las ocho piezas y relacionando los mitos y las leyendas de las Islas Canarias.')


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class DiplomaPrintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for tool in ('pdfinfo', 'pdftotext', 'pdfimages'):
            if not shutil.which(tool):
                raise RuntimeError(f'Required PDF inspection tool missing: {tool}')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel='chrome', args=['--no-sandbox', '--disable-dev-shm-usage'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    @contextmanager
    def imported_page(self, payload, width=1280):
        context = self.browser.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
        errors = []
        try:
            context.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname in ('127.0.0.1', None) else route.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('dialog', lambda dialog: dialog.accept())
            page.set_default_timeout(10000)
            page.goto(self.base, wait_until='networkidle')
            page.locator('#openTeacher').click()
            page.locator('#teacherToolsTab').click()
            page.locator('#importProgressFile').set_input_files({
                'name': 'seguimiento-ficticio.json', 'mimeType': 'application/json',
                'buffer': json.dumps(payload).encode(),
            })
            page.wait_for_function('document.querySelector("#teacherImportStatus").textContent.includes("correctamente")')
            page.locator('#closeTeacher').click()
            # Avoid the interactive OS print dialog; page.pdf still renders a real PDF.
            page.evaluate('window.print = () => {}')
            yield page
            self.assertEqual(errors, [])
        finally:
            context.close()

    def fixture(self):
        return json.loads(FIXTURE.read_text())

    def test_eighth_piece_automatically_shows_diploma_without_reopening_on_reload(self):
        # Real quiz completion also covers a historical piece meeting the current stage's requirements.
        for stage, historical, width in (('middle', False, 1280), ('middle', True, 1280), ('early', False, 390)):
            with self.subTest(stage=stage, historical=historical):
                payload = self.fixture()
                payload['learningLevel'] = stage
                payload['final']['passed'] = False
                if not historical:
                    payload['progress']['earned'].remove('tenerife')
                if stage == 'early':
                    payload['progress']['sourcePassed'].remove('tenerife')
                    payload['progress']['truthPassed'] = []
                else:
                    payload['progress']['truthPassed'].remove('tenerife')
                with self.imported_page(payload, width) as page:
                    self.assertEqual(page.locator('#passportCount').inner_text(), '7/8')
                    page.goto(self.base + '#isla/tenerife/retos', wait_until='networkidle')
                    quiz = page.locator('#source-tenerife' if stage == 'early' else '#quiz-tenerife')
                    if stage != 'early':
                        page.locator('#route-tenerife [data-route-flow-quiz-target="verdad"]').click()
                    answers = ('1', '2', '1') if stage == 'early' else ('false', 'true', 'true')
                    for index, value in enumerate(answers):
                        quiz.locator('.question').nth(index).locator(f'input[value="{value}"]').check()
                        if index < len(answers) - 1:
                            quiz.locator('.question-next').click()
                    quiz.locator('.check-source' if stage == 'early' else '.check-quiz').click()
                    self.assertEqual(page.locator('#passportCount').inner_text(), '8/8')
                    self.assertTrue(page.locator('#diplomaDialog').is_visible())
                    self.assertFalse(page.locator('#badgeDialog').evaluate('(el) => el.open'))
                    self.assertIn(GENERIC_RECOGNITION, ' '.join(page.locator('#diplomaPreview').inner_text().split()))
                    self.assertNotIn(payload['learnerName'], page.locator('#diplomaPreview').text_content())
                    self.assertEqual(page.locator('#diplomaPreview .diploma-badges img').count(), 8)
                    self.assertEqual(page.locator('#diplomaPreview .diploma-signature img').get_attribute('src'), 'assets/images/pintadera_triangulo.webp')
                    self.assertEqual(page.locator('#diplomaPreview [id]').count(), 0)
                    self.assertFalse(page.locator('body').evaluate('(el) => el.classList.contains("print-diploma")'))
                    output_dir = os.environ.get('DIPLOMA_PDF_OUTPUT')
                    if output_dir:
                        page.screenshot(path=str(Path(output_dir) / f'auto-{stage}-{historical}.png'))
                    if historical:
                        page.locator('#printDiplomaPreview').click()
                        page.wait_for_function('document.body.classList.contains("print-diploma")')
                        self.assertFalse(page.locator('#diplomaDialog').evaluate('(el) => el.open'))
                        page.evaluate('window.dispatchEvent(new Event("afterprint"))')
                    else:
                        page.locator('#closeDiploma').click()
                        quiz.locator('.check-source' if stage == 'early' else '.check-quiz').click()
                        self.assertFalse(page.locator('#diplomaDialog').is_visible())
                    page.reload(wait_until='networkidle')
                    self.assertFalse(page.locator('#diplomaDialog').is_visible())
                    page.evaluate('window.print = () => {}')
                    page.locator('#openPassport').click()
                    self.assertTrue(page.locator('#printDiploma').is_enabled())
                    page.locator('#printDiploma').click()
                    page.wait_for_function('document.body.classList.contains("print-diploma")')
                    page.evaluate('window.dispatchEvent(new Event("afterprint"))')

    def test_eight_current_pieces_unlock_diploma_independently_of_final_challenge(self):
        # Catches retaining final.passed as a requirement for the visible button or print guard.
        for passed in (False, True):
            with self.subTest(final_passed=passed):
                payload = self.fixture()
                payload['final']['passed'] = passed
                with self.imported_page(payload) as page:
                    self.assertEqual(page.locator('#passportCount').inner_text(), '8/8')
                    page.locator('#openPassport').click()
                    self.assertEqual(page.locator('#passportDialog #printDiploma').count(), 1)
                    self.assertEqual(page.locator('#finalMission #printDiploma').count(), 0)
                    self.assertTrue(page.locator('#printDiploma').is_visible())
                    self.assertTrue(page.locator('#printDiploma').is_enabled())
                    page.locator('#printDiploma').click()
                    page.wait_for_function('document.body.classList.contains("print-diploma")')
                    self.assertFalse(page.locator('#passportDialog').evaluate('(el) => el.open'))
                    page.evaluate('window.dispatchEvent(new Event("afterprint"))')
                    if not passed:
                        # The optional challenge remains usable after receiving the diploma.
                        page.goto(self.base + '#gran-reto', wait_until='networkidle')
                        answers = ('tenerife', 'gran-canaria', 'la-palma', 'la-gomera',
                                   'el-hierro', 'fuerteventura', 'lanzarote', 'la-graciosa')
                        for index, answer in enumerate(answers):
                            page.locator('#finalMatchGrid select').nth(index).select_option(answer)
                        page.locator('#checkFinalChallenge').click()
                        self.assertIn('¡Gran reto superado!', page.locator('#finalChallengeStatus').text_content())
                        self.assertTrue(page.locator('#printDiploma').is_enabled())

    def test_incomplete_passport_cannot_print_even_with_saved_final_challenge(self):
        # Catches bypassing the passport check when the final challenge was completed earlier.
        for count in (0, 7):
            for passed in (False, True):
                with self.subTest(pieces=count, final_passed=passed):
                    payload = self.fixture()
                    for key in ('earned', 'sourcePassed', 'truthPassed'):
                        payload['progress'][key] = payload['progress'][key][:count]
                    payload['final']['passed'] = passed
                    with self.imported_page(payload) as page:
                        self.assertEqual(page.locator('#passportCount').inner_text(), f'{count}/8')
                        page.locator('#openPassport').click()
                        self.assertEqual(page.locator('#passportDialog #printDiploma').count(), 1)
                        self.assertTrue(page.locator('#printDiploma').is_visible())
                        self.assertFalse(page.locator('#printDiploma').is_enabled())
                        page.evaluate('printDiploma()')
                        self.assertFalse(page.locator('body').evaluate('(el) => el.classList.contains("print-diploma")'))
                        self.assertTrue(page.locator('#passportDialog').evaluate('(el) => el.open'))

    def test_changing_stage_rechecks_historical_pieces(self):
        # Catches counting historical earned pieces that lack the new stage's true/false task.
        payload = self.fixture()
        payload['learningLevel'] = 'early'
        payload['progress']['truthPassed'] = []
        with self.imported_page(payload) as page:
            self.assertEqual(page.locator('#passportCount').inner_text(), '8/8')
            page.locator('#openTeacher').click()
            page.locator('#teacherGuideTab').click()
            for disclosure in page.locator('#teacherGuidePanel details').all():
                if disclosure.locator('[data-learning-level="middle"]').count() and disclosure.get_attribute('open') is None:
                    disclosure.locator(':scope > summary').click()
            page.locator('#teacherGuidePanel [data-learning-level="middle"]').click()
            page.locator('#closeTeacher').click()
            self.assertEqual(page.locator('#passportCount').inner_text(), '0/8')
            page.locator('#openPassport').click()
            self.assertTrue(page.locator('#printDiploma').is_visible())
            self.assertFalse(page.locator('#printDiploma').is_enabled())
            page.evaluate('printDiploma()')
            self.assertFalse(page.locator('body').evaluate('(el) => el.classList.contains("print-diploma")'))

    def test_diploma_requests_no_name_and_teacher_tracking_keeps_its_optional_name(self):
        # Catches exposing personal-name controls in the diploma or breaking teacher-name persistence.
        payload = self.fixture()
        with self.imported_page(payload) as page:
            self.assertEqual(page.locator('#passportDialog input[type="text"]').count(), 0)
            self.assertNotIn(payload['learnerName'], page.locator('#passportDialog').text_content())
            page.locator('#openTeacher').click()
            page.locator('#teacherToolsTab').click()
            self.assertEqual(page.locator('#teacherLearnerName').input_value(), payload['learnerName'])
            page.locator('#teacherLearnerName').fill('Otro equipo FICTICIO')
            page.locator('#teacherLearnerName').dispatch_event('change')
            page.locator('#closeTeacher').click()
            page.reload(wait_until='networkidle')
            page.locator('#openPassport').click()
            page.locator('#printDiploma').click()
            page.wait_for_function('document.body.classList.contains("print-diploma")')
            self.assertEqual(page.locator('#diplomaRecognition').text_content(), GENERIC_RECOGNITION)
            self.assertNotIn('Otro equipo FICTICIO', page.locator('#diplomaPrint').text_content())
            page.evaluate('window.dispatchEvent(new Event("afterprint"))')
            page.locator('#openTeacher').click()
            page.locator('#teacherToolsTab').click()
            self.assertEqual(page.locator('#teacherLearnerName').input_value(), 'Otro equipo FICTICIO')

    def test_generic_diploma_fits_one_landscape_page_without_disclosing_saved_names(self):
        # Catches name leaks, missing pieces/team seal/date, pagination or cleanup regressions.
        cases = [('without-name', ''), ('imported-name', 'Equipo FICTICIO prueba técnica 02-11-2026'),
                 ('maximum-name', 'W' * 80)]
        for width in (390, 1280):
            for label, name in cases:
                with self.subTest(viewport=width, name=label), tempfile.TemporaryDirectory() as tmp:
                    payload = self.fixture()
                    payload['learnerName'] = name
                    with self.imported_page(payload, width) as page:
                        page.locator('#openPassport').click()
                        output_dir = os.environ.get('DIPLOMA_PDF_OUTPUT')
                        if output_dir and label == 'without-name':
                            page.screenshot(path=str(Path(output_dir) / f'passport-{width}.png'))
                        page.locator('#printDiploma').click()
                        page.wait_for_function('document.body.classList.contains("print-diploma") && [...document.querySelectorAll("#diplomaPrintBadges img")].length === 8 && [...document.querySelectorAll("#diplomaPrint img")].every(i => i.complete && i.naturalWidth)')
                        self.assertFalse(page.locator('#passportDialog').evaluate('(el) => el.open'))
                        date = page.locator('#diplomaPrintDate').text_content()
                        self.assertTrue(date)
                        pdf = Path(tmp) / 'diploma.pdf'
                        page.pdf(path=str(pdf), format='A4', landscape=True, print_background=True, prefer_css_page_size=True)
                        if output_dir:
                            shutil.copyfile(pdf, Path(output_dir) / f'{label}-{width}.pdf')
                        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
                        self.assertRegex(info, r'Pages:\s+1\b', info)
                        self.assertRegex(info, r'Page size:\s+841\.\d+ x 59[45]\.\d+ pts \(A4\)', info)
                        content = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
                        normalized = ' '.join(content.split())
                        self.assertIn('MitoMapa canario', normalized)
                        self.assertIn(GENERIC_RECOGNITION, normalized)
                        if name:
                            self.assertNotIn(name.replace(' ', ''), normalized.replace(' ', ''))
                        self.assertIn(date, normalized)
                        self.assertIn('ocho piezas', normalized)
                        self.assertIn('Por el equipo de MitoMapa canario', normalized)
                        for personal_credit in ('Autoría:', 'Jesica Fortes', 'Gloria Elsa González', 'Cristian García Santana'):
                            self.assertNotIn(personal_credit, normalized)
                        images = subprocess.check_output(['pdfimages', '-list', str(pdf)], text=True)
                        self.assertGreaterEqual(len(re.findall(r'^\s*1\s+\d+\s+image\s', images, re.M)), 9, images)
                        page.evaluate('window.dispatchEvent(new Event("afterprint"))')
                        self.assertFalse(page.locator('body').evaluate('(el) => el.classList.contains("print-diploma")'))
