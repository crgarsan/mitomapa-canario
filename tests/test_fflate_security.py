"""Exercise the fflate bytes selected by the native builder in bounded processes."""
import base64
from io import BytesIO
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_current_elpx import build_current
from release_support import read_zip
from native_fflate import LICENSE_MEMBER, apply_fflate_upgrade, verify_fflate_upgrade

MEMBER = 'libs/fflate/fflate.umd.js'


def malformed_zip64(extra=b''):
    # One central entry declares a ZIP64 compressed size without its required
    # extra field. The second variant has an unrelated, correctly bounded tag.
    data = bytearray(145 + len(extra))
    struct.pack_into('<I', data, 0, 0x06064B50)
    struct.pack_into('<I', data, 32, 1)
    struct.pack_into('<I', data, 48, 56)
    struct.pack_into('<I', data, 56, 0x02014B50)
    struct.pack_into('<I', data, 76, 0xFFFFFFFF)
    struct.pack_into('<HH', data, 84, 1, len(extra))
    data[102] = ord('x')
    data[103:103+len(extra)] = extra
    struct.pack_into('<I', data, 103+len(extra), 0x07064B50)
    end = 123+len(extra)
    struct.pack_into('<I', data, end, 0x06054B50)
    struct.pack_into('<H', data, end+8, 65535)
    struct.pack_into('<I', data, end+16, 0xFFFFFFFF)
    return bytes(data)


def valid_zip64():
    # Independent, tiny STORE archive with ZIP64 sizes, local offset and EOCD.
    name, payload = b'x', b'valid ZIP64 payload'
    crc = zlib.crc32(payload)
    extra_local = struct.pack('<HHQQ', 1, 16, len(payload), len(payload))
    local = struct.pack('<IHHHHHIIIHH', 0x04034B50, 45, 0, 0, 0, 0,
                        crc, 0xFFFFFFFF, 0xFFFFFFFF, len(name), len(extra_local)) + name + extra_local + payload
    extra_central = struct.pack('<HHQQQ', 1, 24, len(payload), len(payload), 0)
    central = struct.pack('<IHHHHHHIIIHHHHHII', 0x02014B50, 45, 45, 0, 0, 0, 0,
                          crc, 0xFFFFFFFF, 0xFFFFFFFF, len(name), len(extra_central), 0, 0, 0, 0, 0xFFFFFFFF) + name + extra_central
    end64 = struct.pack('<IQHHIIQQQQ', 0x06064B50, 44, 45, 45, 0, 0, 1, 1, len(central), len(local))
    locator = struct.pack('<IIQI', 0x07064B50, 0, len(local)+len(central), 1)
    end = struct.pack('<IHHHHIIH', 0x06054B50, 0, 0, 65535, 65535, 0xFFFFFFFF, 0xFFFFFFFF, 0)
    return local + central + end64 + locator + end


class NativeFflateSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.version = build_current()

    def run_library(self, program, payload=b''):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node is required for the native-library regression')
        with tempfile.TemporaryDirectory() as folder:
            library = Path(folder) / 'fflate.cjs'
            library.write_bytes(self.files[MEMBER])
            script = "const fflate=require(process.argv[1]);const data=new Uint8Array(Buffer.from(process.argv[2],'base64'));\n" + program
            try:
                result = subprocess.run([node, '-e', script, str(library), base64.b64encode(payload).decode()],
                                        capture_output=True, text=True, timeout=3)
            except subprocess.TimeoutExpired:
                self.fail('Native fflate did not terminate within 3 seconds for a bounded ZIP input')
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_malformed_zip64_is_rejected_without_a_nonterminating_parser(self):
        for extra in (b'', struct.pack('<HH', 0x9999, 0)):
            with self.subTest(extra=extra.hex()):
                result = self.run_library("try{fflate.unzipSync(data);console.log(JSON.stringify({accepted:true}));}catch(e){console.log(JSON.stringify({accepted:false,code:e.code}));}", malformed_zip64(extra))
                self.assertEqual(result, {'accepted': False, 'code': 13})

    def test_legitimate_zip64_sizes_and_offsets_remain_readable(self):
        archive = valid_zip64()
        with ZipFile(BytesIO(archive)) as z:
            self.assertEqual(z.read('x'), b'valid ZIP64 payload')
        result = self.run_library("console.log(JSON.stringify({text:fflate.strFromU8(fflate.unzipSync(data).x)}));", archive)
        self.assertEqual(result, {'text': 'valid ZIP64 payload'})

    def test_native_async_export_preserves_unicode_binary_and_store_entries(self):
        result = self.run_library("""
const input={'cuento-ñ.txt':fflate.strToU8('Texto legítimo áéí'), 'binario.bin':new Uint8Array([0,255,17,0]),'sin-comprimir.txt':[fflate.strToU8('STORE'),{level:0}]};
fflate.zip(input,(error,archive)=>{if(error)throw error;const out=fflate.unzipSync(archive);console.log(JSON.stringify({names:Object.keys(out).sort(),text:fflate.strFromU8(out['cuento-ñ.txt']),binary:Array.from(out['binario.bin']),store:fflate.strFromU8(out['sin-comprimir.txt'])}));});
""")
        self.assertEqual(result, {'names':['binario.bin','cuento-ñ.txt','sin-comprimir.txt'],
                                  'text':'Texto legítimo áéí','binary':[0,255,17,0],'store':'STORE'})


class NativeFflatePinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current, version = build_current()
        cls.baseline = read_zip((ROOT/version['elpx_source']['path']).read_bytes())

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ('package.json','package-lock.json','tools/vendor/FFLATE.json',
                     'tools/vendor/fflate-0.8.3.umd.js','tools/vendor/fflate-LICENSE.txt'):
            destination = self.root/name
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((ROOT/name).read_bytes())

    def test_upgrade_is_repeatable_and_only_touches_the_approved_members(self):
        destination = {**self.baseline, 'unrelated': b'keep'}
        apply_fflate_upgrade(destination,self.baseline,self.root)
        first = dict(destination)
        apply_fflate_upgrade(destination,self.baseline,self.root)
        self.assertEqual(destination,first)
        changed = {name for name in set(destination)|set(self.baseline)
                   if destination.get(name)!=self.baseline.get(name)}
        self.assertEqual(changed,{MEMBER,LICENSE_MEMBER,'unrelated'})
        self.assertEqual(destination['unrelated'],b'keep')

    def test_unrecognized_source_cannot_partially_change_the_destination(self):
        destination = {'sentinel':b'unchanged'}
        baseline = {**self.baseline,MEMBER:self.baseline[MEMBER]+b'changed'}
        with self.assertRaisesRegex(ValueError,'Unrecognized native fflate source'):
            apply_fflate_upgrade(destination,baseline,self.root)
        self.assertEqual(destination,{'sentinel':b'unchanged'})

    def test_modified_vendor_or_license_is_rejected_before_update(self):
        for name in ('fflate-0.8.3.umd.js','fflate-LICENSE.txt'):
            with self.subTest(member=name):
                path = self.root/'tools/vendor'/name
                original = path.read_bytes()
                path.write_bytes(original+b'changed')
                destination = {'sentinel':b'unchanged'}
                with self.assertRaisesRegex(ValueError,'pinned fflate bytes'):
                    apply_fflate_upgrade(destination,self.baseline,self.root)
                self.assertEqual(destination,{'sentinel':b'unchanged'})
                path.write_bytes(original)

    def test_changed_metadata_cannot_redirect_or_downgrade_the_pin(self):
        path = self.root/'tools/vendor/FFLATE.json'
        metadata = json.loads(path.read_text())
        for key,value in (('version','0.8.2'),('path','../outside.js'),('sha256','0'*64)):
            with self.subTest(field=key):
                path.write_text(json.dumps({**metadata,key:value}))
                with self.assertRaisesRegex(ValueError,'reviewed pin'):
                    apply_fflate_upgrade({},self.baseline,self.root)
        path.write_text(json.dumps(metadata))

    def test_dependency_lock_downgrade_is_rejected(self):
        path = self.root/'package-lock.json'
        locked = json.loads(path.read_text())
        locked['packages']['node_modules/fflate']['version']='0.8.2'
        path.write_text(json.dumps(locked))
        with self.assertRaisesRegex(ValueError,'dependency lock'):
            apply_fflate_upgrade({},self.baseline,self.root)

    def test_output_downgrade_and_missing_license_are_rejected(self):
        for name,value in ((MEMBER,self.baseline[MEMBER]),(LICENSE_MEMBER,b'')):
            with self.subTest(member=name),self.assertRaisesRegex(ValueError,'reviewed pin'):
                verify_fflate_upgrade({**self.current,name:value},self.baseline,self.root)
