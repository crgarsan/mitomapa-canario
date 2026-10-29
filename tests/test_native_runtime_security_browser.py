"""Real native renderers must keep project metadata inert in a local preview.

The preview frame uses the author-preview sandbox attributes documented by
eXe v4.0.5. This tests the two bundled renderers, not a hosted editor's trust
policy or the safety of opening arbitrary executable eXe projects.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import shutil
import sys
import threading
import unittest
import zipfile
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_current_elpx import build_current

PAYLOAD = '<img src="data:,broken" onerror="window.parent.__nativeAuditExecuted += 1">'
BREAKOUT = '\"><img src="data:,broken" onerror="window.parent.__nativeAuditExecuted += 1"><span data-x="'


class NativeRuntimeSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, version = build_current()
        if os.environ.get('MITOMAPA_NATIVE_TEST_BASELINE') == '1':
            # Test-only mutation: run the same fixtures against the exact
            # original runtimes, not a rewritten approximation of the bug.
            with zipfile.ZipFile(ROOT/version['elpx_source']['path']) as original:
                for kind in ('progress-report','checklist'):
                    member=f'idevices/{kind}/{kind}.js'
                    cls.files[member]=original.read(member)
        files = cls.files

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = unquote(urlsplit(self.path).path).lstrip('/')
                if path == 'audit-host.html':
                    body = b'''<!doctype html><title>Isolated native audit</title>
<script>window.__nativeAuditExecuted=0;</script>
<iframe id="preview" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals" src="html/pasaporte-y-progreso.html"></iframe>'''
                else:
                    body = files.get(path)
                if body is None:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'text/html')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox', '--disable-dev-shm-usage'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 1000})
        self.context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname in ('127.0.0.1', None) or urlsplit(r.request.url).scheme in ('data', 'blob') else r.abort())
        self.page = self.context.new_page()
        self.page.goto(self.base + 'audit-host.html', wait_until='networkidle')
        self.frame = self.page.frame_locator('#preview')
        self.child = self.page.frames[1]
        self.child.wait_for_function('()=>window.$eXeListaCotejo?.options?.length && window.$eXeInforme?.options')

    def tearDown(self):
        self.context.close()

    def settle(self):
        self.child.evaluate('''async()=>{
          await Promise.all([...document.images].map(image=>image.decode().catch(()=>{})));
          await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
        }''')

    def assert_no_active_metadata(self):
        self.settle()
        self.assertEqual(self.page.evaluate('window.__nativeAuditExecuted'), 0)
        self.assertEqual(self.child.locator('main [onerror],main [onload],main script[data-injected],main svg,main math').count(), 0)

    def test_page_and_block_metadata_are_literal_in_both_progress_generators(self):
        for generator in ('generateHtmlFromPages', 'generateHtmlFromJsonPages'):
            with self.subTest(generator=generator):
                self.page.evaluate('window.__nativeAuditExecuted=0')
                self.child.evaluate('''({generator,payload,breakout})=>{
                  const report=$eXeInforme;
                  report.isInExe=false; report.options.showTypeGame=true;
                  report.options.activeLinks=true; report.options.evaluationID='audit';
                  report.options.msgs.msgSeeActivity=breakout;
                  const item={ideviceID:breakout,odeIdeviceId:breakout,blockName:payload,
                    odeIdeviceTypeName:payload,evaluation:true,evaluationID:'audit'};
                  const child={id:breakout,odePageId:breakout,title:payload,name:payload,
                    url:'tenerife-taller',components:[item],children:[],parentID:'root'};
                  const root={id:'root',title:'Canarias < > & " seguro',name:'Canarias < > & " seguro',
                    components:[],children:[child]};
                  const html=report[generator]([root]);report.createTableIdevices(html,0);
                }''', {'generator': generator, 'payload': PAYLOAD, 'breakout': BREAKOUT})
                self.assert_no_active_metadata()
                titles=self.child.locator('#informeData-0 .IFPP-PageTitle').all_text_contents()
                self.assertEqual(titles, ['Canarias < > & " seguro', PAYLOAD])
                self.assertEqual(self.child.locator('#informeData-0 .IFPP-ComponentTitle').inner_text(), PAYLOAD)
                self.assertEqual(self.child.locator('#informeData-0 .IFPP-ComponentItem').count(), 1)

    def test_xml_metadata_reaches_the_report_without_becoming_markup(self):
        self.child.evaluate('''({xml,payload})=>{
          const doc=new DOMParser().parseFromString(xml,'text/xml');
          doc.querySelector('pageName').textContent=payload;
          doc.querySelector('blockName').textContent=payload;
          const pages=$eXeInforme.parseOdeXmlToJson(new XMLSerializer().serializeToString(doc));
          $eXeInforme.createTableIdevices($eXeInforme.generateHtmlFromJsonPages(pages),0);
        }''',{'xml':self.files['content.xml'].decode(),'payload':PAYLOAD})
        self.assert_no_active_metadata()
        titles=self.child.locator('#informeData-0 .IFPP-PageTitle').all_text_contents()
        self.assertEqual(len(titles),34)
        self.assertIn(PAYLOAD,titles)

    def test_progress_messages_cannot_break_text_or_attribute_contexts(self):
        self.child.evaluate('''payload=>{
          for(const key of ['msgReportTitle','msgName','msgDate','mgsSections','msgAverageScore','msgReboot','msgSave'])
            $eXeInforme.options.msgs[key]=payload;
          $eXeInforme.options.userData=true;$eXeInforme.createTableIdevices('<ul></ul>',0);
        }''', PAYLOAD)
        self.assert_no_active_metadata()
        self.assertEqual(self.child.locator('#informeTitleProyect-0').inner_text().strip(), PAYLOAD)
        self.assertEqual(self.child.locator('#informeCapture-0').inner_text(), PAYLOAD)

    def test_progress_counter_and_empty_state_messages_are_literal(self):
        for generator in ('generateHtmlFromPages', 'generateHtmlFromJsonPages', 'empty'):
            with self.subTest(generator=generator):
                self.page.evaluate('window.__nativeAuditExecuted=0')
                self.child.evaluate('''({generator,payload})=>{
                  document.querySelector('#informeEvalutationNumber')?.remove();
                  const counter=document.createElement('p');
                  counter.id='informeEvalutationNumber';document.querySelector('main').append(counter);
                  $eXeInforme.options.msgs.msgNoPendientes=payload+' %s';
                  $eXeInforme.options.msgs.msgReload=payload;
                  if(generator==='empty')counter.innerHTML=$eXeInforme.createPagesHtml(null);
                  else $eXeInforme[generator]([]);
                }''', {'generator':generator,'payload':PAYLOAD})
                self.assert_no_active_metadata()
                expected=PAYLOAD if generator=='empty' else PAYLOAD+' 0'
                self.assertEqual(self.child.locator('#informeEvalutationNumber').inner_text(),expected)

    def test_checklist_plain_fields_messages_and_points_are_inert(self):
        for key in ('title', 'subtitle', 'message', 'points'):
            with self.subTest(field=key):
                self.page.evaluate('window.__nativeAuditExecuted=0')
                self.child.evaluate('''({key,payload,breakout})=>{
                  const game=$eXeListaCotejo,options=game.options[0];
                  options.title='Colección';options.subtitle='Islas';options.useScore=true;
                  options.levels=[{type:'0',nivel:'0',item:'Una pieza',points:'1'}];
                  if(key==='message')for(const name of ['msgName','msgDate','msgComplit','msgScore','msgReboot','msgSave'])options.msgs[name]=breakout;
                  else if(key==='points')options.levels[0].points='1'+payload;
                  else options[key]=payload;
                  $('#ctjMainContainer-0').remove();$('main').append(game.createInterfaceListaCotejo(0));
                }''', {'key': key, 'payload': PAYLOAD, 'breakout': BREAKOUT})
                self.assert_no_active_metadata()
                if key in ('title','subtitle'):
                    selector='#ctjTitle-0' if key=='title' else '#ctjSubTitle-0'
                    self.assertEqual(self.child.locator(selector).inner_text(),PAYLOAD)
                    self.assertEqual(self.child.evaluate('key=>$eXeListaCotejo.options[0][key]',key),PAYLOAD)

    def test_checklist_rich_fields_keep_formatting_without_active_content(self):
        payload='<strong>Garoé</strong> y <em>agua</em><br><a href="https://example.org/fuente" target="_blank">Fuente</a>'+PAYLOAD+'<svg onload="window.parent.__nativeAuditExecuted+=1"></svg><math><mi>x</mi></math><span id="location" style="position:fixed">texto</span><a href="javascript:window.parent.__nativeAuditExecuted++">inseguro</a>'
        self.child.evaluate('''payload=>{
          const game=$eXeListaCotejo,options=game.options[0];
          options.footer=payload;options.levels=['0','1','2','3'].map(type=>({type,nivel:'0',item:payload,points:'1'}));
          $('#ctjMainContainer-0').remove();$('main').append(game.createInterfaceListaCotejo(0));
        }''',payload)
        self.assert_no_active_metadata()
        expect(self.child.locator('#ctjMainContainer-0 strong')).to_have_count(5)
        expect(self.child.locator('#ctjMainContainer-0 em')).to_have_count(5)
        self.assertEqual(self.child.locator('#ctjMainContainer-0 a[href="https://example.org/fuente"]').count(),5)
        self.assertEqual(self.child.locator('#ctjMainContainer-0 a[target="_blank"][rel="noopener noreferrer"]').count(),5)
        self.assertEqual(self.child.locator('#ctjMainContainer-0 [id="location"],#ctjMainContainer-0 a[href^="javascript:"]').count(),0)
        self.assertEqual(self.child.locator('#ctjMainContainer-0 span[style="position:fixed"]').count(),0)

    def test_encoded_protocols_and_namespace_payloads_stay_inert(self):
        vectors=[
            '<a href="&#x6a;ava&#x73;cript:window.parent.__nativeAuditExecuted++">enlace</a>',
            '<a href="java&#9;script:window.parent.__nativeAuditExecuted++">enlace</a>',
            '<math><mtext><table><mglyph><style><!--</style><img title="--><img src=data:,broken onerror=window.parent.__nativeAuditExecuted++>">',
            '<svg><foreignObject><img src="data:,broken" onerror="window.parent.__nativeAuditExecuted++"></foreignObject></svg>',
            '&lt;img src=data:,broken onerror=window.parent.__nativeAuditExecuted++&gt;',
        ]
        for vector in vectors:
            with self.subTest(vector=vector):
                self.page.evaluate('window.__nativeAuditExecuted=0')
                self.child.evaluate('''value=>{
                  const game=$eXeListaCotejo;
                  game.options[0].footer=value;game.options[0].levels=[{type:'3',nivel:'0',item:value,points:''}];
                  $('#ctjMainContainer-0').remove();$('main').append(game.createInterfaceListaCotejo(0));
                }''',vector)
                self.assert_no_active_metadata()
                unsafe=self.child.locator('#ctjMainContainer-0').evaluate(r'''root=>[...root.querySelectorAll('*')].flatMap(node=>[...node.attributes].filter(a=>/^on/i.test(a.name)||a.name==='style'&&/fixed/i.test(a.value)||['href','src'].includes(a.name)&&/^\s*javascript:/i.test(a.value)))''')
                self.assertEqual(unsafe,[])

    def test_hidden_image_urls_cannot_break_the_checklist_interface(self):
        self.child.evaluate('''breakout=>{
          const game=$eXeListaCotejo,options=structuredClone(game.options[0]);
          options.hasLogo=true;options.hasCommunity=true;options.hasDecorative=true;
          const data=$('<p>').text($exeDevices.iDevice.gamification.helpers.encrypt(JSON.stringify(options)));
          game.options[0]=game.loadDataGame(data,breakout,breakout,breakout);
          $('#ctjMainContainer-0').remove();$('main').append(game.createInterfaceListaCotejo(0));
        }''',BREAKOUT)
        self.assert_no_active_metadata()
        expect(self.child.locator('#ctjMainContainer-0')).to_have_count(1)

    def test_original_native_checklist_still_saves_and_renders_emphasis(self):
        expect(self.frame.locator('.CTJP-Item strong')).to_have_count(8)
        self.page.goto(self.base+'html/tenerife-taller.html',wait_until='networkidle')
        select=self.page.locator('.CTJP-Item select').first
        if select.is_hidden():
            select.locator('xpath=ancestor::article[1]').locator('.box-toggle').click()
        select.select_option('1')
        self.page.reload(wait_until='networkidle')
        expect(self.page.locator('.CTJP-Item select').first).to_have_value('1')

    def test_a_host_sanitizer_instance_is_not_replaced(self):
        vendor=(ROOT/'tools/vendor/dompurify-3.4.17.min.js').read_text()
        self.context.add_init_script(vendor+'\nwindow.__hostSanitizer=window.DOMPurify;')
        self.page.reload(wait_until='networkidle')
        child=self.page.frames[1]
        child.wait_for_function('()=>window.$eXeListaCotejo?.options?.length')
        self.assertTrue(child.evaluate('window.DOMPurify===window.__hostSanitizer'))


if __name__=='__main__':unittest.main()
