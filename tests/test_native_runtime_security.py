"""Preserve the reviewed native transformation boundary and reject drift."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from native_runtime_security import LICENSE_MEMBER, MEMBERS, apply_runtime_security, hardened_members
from release_support import read_zip
from sync_current_elpx import build_current, verify_preservation


class NativeRuntimeSecurityBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current,cls.version=build_current()
        cls.baseline=read_zip((ROOT/cls.version['elpx_source']['path']).read_bytes())

    def test_transform_is_repeatable_and_does_not_change_unrelated_members(self):
        files=dict(self.baseline)
        apply_runtime_security(files,self.baseline)
        first=dict(files)
        apply_runtime_security(files,self.baseline)
        self.assertEqual(files,first)
        changed={name for name in set(files)|set(self.baseline) if files.get(name)!=self.baseline.get(name)}
        self.assertEqual(changed,set(MEMBERS)|{LICENSE_MEMBER})
        self.assertIn(b'Apache License',files[LICENSE_MEMBER])

    def test_an_unknown_runtime_source_is_rejected_before_any_change(self):
        for name in MEMBERS:
            with self.subTest(member=name):
                baseline={**self.baseline,name:self.baseline[name]+b'\n// unexpected source'}
                result={'sentinel':b'unchanged'}
                with self.assertRaisesRegex(ValueError,'Unrecognized native runtime'):
                    apply_runtime_security(result,baseline)
                self.assertEqual(result,{'sentinel':b'unchanged'})

    def test_preservation_rejects_tampering_even_in_the_two_allowed_runtimes(self):
        for name in [*MEMBERS,LICENSE_MEMBER]:
            with self.subTest(member=name):
                changed={**self.current,name:self.current[name]+b'\nchanged'}
                with self.assertRaisesRegex(ValueError,'reviewed transform'):
                    verify_preservation(self.baseline,changed)

    def test_preservation_still_rejects_an_unrelated_runtime_change(self):
        changed={**self.current,'libs/common.js':self.current['libs/common.js']+b'\nchanged'}
        with self.assertRaisesRegex(ValueError,'runtime dependency'):
            verify_preservation(self.baseline,changed)

    def test_preservation_rejects_an_unexpected_added_runtime(self):
        changed={**self.current,'libs/unexpected.js':b'window.unexpected=true;'}
        with self.assertRaisesRegex(ValueError,'unexpected runtime'):
            verify_preservation(self.baseline,changed)
