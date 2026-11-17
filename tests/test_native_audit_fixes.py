"""Exercise the native defects reproduced during the complete resource audit."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import urljoin, urlsplit

from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from native_preservation import game_payloads, verify_component
from editorial_elpx import clean_markup, encode_native_payload
from release_support import read_zip
from sync_current_elpx import build_current, field, native_structure

NS = {'o': 'http://www.intef.es/xsd/ode'}
VOCABULARY = (
    '20260823155837COM1YD', '20260823155837COM2J3',
    '20260823155837COM3VY', '20260823155837COM4HJ',
    '20260823155837COM571', '20260823155837COM6WT',
    '20260823155837COM7Z9', '20260823155837COM843',
)


class NativeAuditFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.version = build_current()
        cls.components = native_structure(cls.files)['components']
        cls.originals = native_structure(read_zip((ROOT / cls.version['elpx_source']['path']).read_bytes()))['components']

    def changed_payload(self, component, mutate):
        changed = deepcopy(component)
        view = field(component, 'htmlView')
        data = deepcopy(game_payloads(view)[0][0])
        mutate(data)
        document = html.fragment_fromstring(view, create_parent=True)
        encoded = document.xpath('.//div[contains(@class,"completa-DataGame")]')[0].text_content()
        changed.find('o:htmlView', NS).text = view.replace(
            encoded, encode_native_payload(json.dumps(data, ensure_ascii=False)), 1,
        )
        return changed

    def test_vocabulary_choices_have_no_biology_or_misspelling_alternatives(self):
        for iid in VOCABULARY:
            data = game_payloads(field(self.components[iid], 'htmlView'))[0][0]
            with self.subTest(idevice=iid):
                self.assertEqual(data['wordsErrors'], '')
                self.assertEqual(data['type'], 2)
                self.assertIn('Selecciona', data['instructions'])
                text = re.sub(r'%u([0-9a-f]{4})|%([0-9a-f]{2})',
                              lambda m: chr(int(m[1] or m[2], 16)), data['textText'], flags=re.I)
                alternatives = [word.strip() for group in re.findall(r'@@(.*?)@@', text)
                                for word in group.split('|')]
                self.assertFalse(set(alternatives) & {'vivian', 'pequeno', 'encendio', 'desaparecio', 'dia'})
                document = html.fragment_fromstring(field(self.components[iid], 'htmlView'), create_parent=True)
                source = document.xpath('.//div[contains(@class,"completa-text-game")]')[0]
                self.assertEqual(html.tostring(source[0], encoding='unicode'), html.tostring(html.fragment_fromstring(text, create_parent=True)[0], encoding='unicode'))
                self.assertEqual(' '.join(source.text_content().split()),
                                 ' '.join(html.fragment_fromstring(text, create_parent=True).text_content().split()))
        palma = game_payloads(field(self.components[VOCABULARY[2]], 'htmlView'))[0][0]
        self.assertIn('guardamos', palma['textText'])
        graciosa = game_payloads(field(self.components[VOCABULARY[7]], 'htmlView'))[0][0]
        decoded = re.sub(r'%u([0-9a-f]{4})|%([0-9a-f]{2})',
                         lambda m: chr(int(m[1] or m[2], 16)), graciosa['textText'], flags=re.I)
        self.assertIn('desaparecía', decoded)

    def test_vocabulary_preservation_rejects_every_unreviewed_setting_or_answer(self):
        changes = {
            'mode': lambda value: value.update(type=1),
            'score': lambda value: value.update(weighted=5),
            'attempts': lambda value: value.update(attempsNumber=99),
            'tracking': lambda value: value.update(evaluationID='OTHER'),
            'unreviewed instructions': lambda value: value.update(instructions='<p>Otra actividad.</p>'),
            'unreviewed answers': lambda value: value.update(textText='@@otra respuesta@@'),
            'new distractor': lambda value: value.update(wordsErrors='Otro distractor'),
            'unreviewed message': lambda value: value['msgs'].update(msgCheck='Otro texto'),
        }
        for iid in VOCABULARY:
            verify_component(self.originals[iid], self.components[iid], self.files)
            for label, change in changes.items():
                with self.subTest(idevice=iid, field=label):
                    candidate = self.changed_payload(self.components[iid], change)
                    with self.assertRaisesRegex(ValueError, 'vocabulary'):
                        verify_component(self.originals[iid], candidate, self.files)

    def test_teacher_material_links_open_the_announced_local_documents(self):
        guide = json.loads(field(self.components['20260823155837TGUID1'], 'jsonProperties'))['textTextarea']
        doc = html.fragment_fromstring(guide, create_parent=True)
        expected = {
            'Abrir la pauta cualitativa': '{{context_path}}/content/resources/Rubrica_lectura_MitoMapa_4_0.html',
            'Abrir el protocolo de pilotaje y su hoja imprimible': '{{context_path}}/content/resources/PROTOCOLO_PILOTAJE.html',
        }
        for label, target in expected.items():
            with self.subTest(label=label):
                link = doc.xpath('.//a[normalize-space(.)=$label]', label=label)
                self.assertEqual(len(link), 1)
                self.assertEqual(link[0].get('href'), target)
                self.assertIn(target.removeprefix('{{context_path}}/'), self.files)
        protocol = html.fromstring(self.files['content/resources/PROTOCOLO_PILOTAJE.html'])
        self.assertEqual(protocol.xpath('string(//h1)'), 'Preparar una primera aplicación de MitoMapa')
        self.assertEqual(len(protocol.xpath('//table/tbody/tr')), 5)
        self.assertIn('Registro sin identificadores', protocol.text_content())
        self.assertTrue(protocol.xpath('//style'))
        self.assertFalse(protocol.xpath('//link[@rel="stylesheet"]'))

    def test_preview_assets_resolve_once_under_a_host_subdirectory(self):
        source = self.files['search_index.js'].decode()
        pages = json.loads(source[source.index('{'):].rstrip(';\n'))
        for page in pages.values():
            name = page['fileUrl']
            doc = html.fromstring(self.files[name])
            targets = []
            for element in doc.xpath('//head/script[@src] | //head/link[@href]'):
                ref = element.get('src') or element.get('href')
                if 'idevices/' not in ref:
                    continue
                resolved = urlsplit(urljoin('https://example.invalid/rea/' + name, ref)).path
                with self.subTest(page=name, reference=ref):
                    self.assertTrue(resolved.startswith('/rea/'))
                    self.assertIn(resolved.removeprefix('/rea/'), self.files)
                    self.assertNotIn(resolved, targets)
                targets.append(resolved)
            self.assertEqual(doc.xpath('string(//*[@id="skipNav"])'), 'Saltar al contenido')

    def test_native_owned_prose_uses_aborigen_and_the_new_domain(self):
        for iid, component in self.components.items():
            if field(component, 'odeIdeviceTypeName') != 'text':
                continue
            text = json.loads(field(component, 'jsonProperties'))['textTextarea']
            with self.subTest(idevice=iid):
                self.assertNotRegex(html.fragment_fromstring(text, create_parent=True).text_content(), r'\bindígenas?\b')
        extra = json.loads(field(self.components['20261006TEXPLORER440'], 'jsonProperties'))['textTextarea']
        self.assertIn('href="https://mitomapacanario.org/"', extra)

    def test_aborigen_edit_preserves_official_linked_titles_and_reference_urls(self):
        sample = '<p>La población indígena. <a href="https://example.invalid/indigena">Arqueología indígena de Canarias</a>: fuente sobre los indígenas. <cite>El mundo indígena</cite>.</p>'
        doc = html.fragment_fromstring(clean_markup(sample), create_parent=True)
        self.assertIn('La población aborigen.', doc.text_content())
        self.assertIn('fuente sobre los aborígenes.', doc.text_content())
        self.assertEqual(doc.xpath('string(.//a)'), 'Arqueología indígena de Canarias')
        self.assertEqual(doc.xpath('string(.//cite)'), 'El mundo indígena')
        self.assertEqual(doc.xpath('string(.//a/@href)'), 'https://example.invalid/indigena')


if __name__ == '__main__':
    unittest.main()
