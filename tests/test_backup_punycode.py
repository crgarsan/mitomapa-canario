"""Exercise the Pages step's real Node preload without credentials or network.

Removing its loader, routing the wrong module, or suppressing warnings must break
these tests. No GitHub action bundle or deployment API is executed here.
"""
import base64
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    'tools/pages-punycode.mjs',
    'tools/pages-punycode-exports.js',
    'tools/vendor/punycode-2.3.1.js',
)


def workflow_node_options(workflow):
    """Read the scalar env binding on the selected publishing action only."""
    steps = re.findall(r'(?ms)^      - (.*?)(?=^      - |\Z)', workflow)
    matches = [step for step in steps
               if re.search(r'(?m)^        uses: actions/deploy-pages@', '      - ' + step)]
    if len(matches) != 1:
        raise AssertionError('Expected one deploy-pages step')
    binding = re.search(r'(?m)^          NODE_OPTIONS:[ \t]*([^\n]+)$', matches[0])
    value = binding.group(1).strip() if binding else ''
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


class BackupPunycodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which('node')
        if cls.node is None:
            raise AssertionError('Node.js is required by the Pages runtime regression tests')
        cls.options = workflow_node_options(
            (ROOT / '.github/workflows/deploy-backup.yml').read_text())

    def run_node(self, script, *, preload=True, input_type='commonjs'):
        # Deliberately do not inherit tokens, NODE_OPTIONS or warning controls.
        # A space in the checkout path catches unquoted --import paths in YAML.
        with tempfile.TemporaryDirectory(prefix='mitomapa pages ') as directory:
            workspace = Path(directory) / 'checkout with spaces'
            workspace.mkdir()
            if preload and self.options:
                for name in RUNTIME_FILES:
                    source = ROOT / name
                    # During RED a new facade may not exist yet: Node must
                    # report the real import failure, not a fixture copy error.
                    if not source.exists():
                        continue
                    target = workspace / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
            env = {'PATH': str(Path(self.node).parent)}
            if preload and self.options:
                env['NODE_OPTIONS'] = self.options.replace('${{ github.workspace }}', str(workspace))
            return subprocess.run(
                [self.node, '--throw-deprecation', '--input-type=' + input_type, '-e', script],
                cwd=workspace, env=env, capture_output=True, text=True,
                timeout=15, check=False)

    def test_workflow_preload_keeps_idn_results_without_deprecated_core_module(self):
        # Broken production change: dropping the step env/preload falls back to
        # Node core and --throw-deprecation turns DEP0040 into a failing exit.
        result = self.run_node(r'''
const assert = require('node:assert/strict');
const punycode = require('punycode');
assert.strictEqual(require('node:punycode'), punycode);
for (const [unicode, ascii] of [
  ['mañana.com', 'xn--maana-pta.com'],
  ['bücher.example', 'xn--bcher-kva.example'],
  ['例え.テスト', 'xn--r8jz45g.xn--zckzah'],
  ['example.com', 'example.com']
]) {
  assert.equal(punycode.toASCII(unicode), ascii);
  assert.equal(punycode.toUnicode(ascii), unicode);
}
assert.equal(punycode.decode('maana-pta'), 'mañana');
assert.equal(punycode.encode('mañana'), 'maana-pta');
assert.deepEqual(punycode.ucs2.decode('😀'), [0x1f600]);
Promise.all([import('punycode'), import('node:punycode')]).then(([bare, builtin]) => {
  assert.strictEqual(bare.default, punycode);
  assert.strictEqual(builtin.default, punycode);
  setImmediate(() => {
    // A selective DEP0040 mute would still load Node core 2.1.0.
    assert.equal(punycode.version, '2.3.1');
    console.log('IDN_REQUIRE_IMPORT_OK');
  });
}).catch(error => { console.error(error); process.exitCode = 1; });
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('IDN_REQUIRE_IMPORT_OK', result.stdout)
        self.assertNotIn('DEP0040', result.stderr)
        self.assertEqual(result.stderr, '')

    def test_preload_preserves_named_esm_exports_for_both_specifiers(self):
        # Routing directly to opaque CommonJS preserves default but loses the
        # named imports exposed by Node's original punycode builtin contract.
        script = r'''
import punycode, { version, ucs2, decode, encode, toASCII, toUnicode }
  from PUNYCODE_SPECIFIER;
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
assert.strictEqual(punycode, require('punycode'));
assert.strictEqual(punycode, require('node:punycode'));
assert.equal(version, '2.3.1');
for (const [name, value] of Object.entries({ ucs2, decode, encode, toASCII, toUnicode })) {
  assert.strictEqual(value, punycode[name]);
}
assert.deepEqual(ucs2.decode('😀'), [0x1f600]);
assert.equal(ucs2.encode([0x1f600]), '😀');
assert.equal(decode('bcher-kva'), 'bücher');
assert.equal(encode('mañana'), 'maana-pta');
assert.equal(toASCII('mañana.com'), 'xn--maana-pta.com');
assert.equal(toUnicode('xn--bcher-kva.example'), 'bücher.example');
console.log('ESM_NAMED_EXPORTS_OK');
'''
        for specifier in ('punycode', 'node:punycode'):
            with self.subTest(specifier=specifier):
                result = self.run_node(
                    script.replace('PUNYCODE_SPECIFIER', json.dumps(specifier)),
                    input_type='module')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('ESM_NAMED_EXPORTS_OK', result.stdout)
                self.assertEqual(result.stderr, '')

    def test_preload_leaves_other_builtin_modules_unchanged(self):
        # A resolver that intercepts every specifier would break real consumers.
        result = self.run_node(r'''
const assert = require('node:assert/strict');
assert.strictEqual(require('fs'), require('node:fs'));
assert.strictEqual(require('url'), require('node:url'));
assert.equal(require.resolve('node:fs'), 'node:fs');
assert.equal(require('node:path').posix.join('/alpha', 'beta'), '/alpha/beta');
assert.equal(new (require('node:url').URL)('https://bücher.example/').hostname,
             'xn--bcher-kva.example');
console.log('OTHER_BUILTINS_OK');
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('OTHER_BUILTINS_OK', result.stdout)
        self.assertEqual(result.stderr, '')

    def test_preload_keeps_other_warnings_visible(self):
        # Disabling process warnings would hide this independent diagnostic.
        result = self.run_node(r'''
process.emitWarning('independent warning must remain visible', {
  type: 'Warning', code: 'MITOMAPA_WARNING_SENTINEL'
});
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('MITOMAPA_WARNING_SENTINEL', result.stderr)
        self.assertIn('independent warning must remain visible', result.stderr)

    def test_preload_keeps_other_deprecations_fatal(self):
        # Catching/removing warning handlers must not override Node's policy.
        result = self.run_node(r'''
process.emitWarning('independent deprecation must remain fatal', {
  type: 'DeprecationWarning', code: 'MITOMAPA_DEPRECATION_SENTINEL'
});
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MITOMAPA_DEPRECATION_SENTINEL', result.stderr)
        self.assertIn('independent deprecation must remain fatal', result.stderr)

    def test_vendored_runtime_and_license_match_reviewed_provenance(self):
        # Missing/edited vendor bytes or licence must require a provenance review.
        provenance = json.loads((ROOT / 'tools/vendor/PUNYCODE.json').read_text())
        self.assertEqual(provenance['name'], 'punycode')
        self.assertEqual(provenance['version'], '2.3.1')
        self.assertEqual(provenance['license'], 'MIT')
        self.assertEqual(provenance['registry_url'],
                         'https://registry.npmjs.org/punycode/2.3.1')
        self.assertEqual(provenance['tarball_url'],
                         'https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz')
        algorithm, integrity = provenance['tarball_integrity'].split('-', 1)
        self.assertEqual(algorithm, 'sha512')
        self.assertEqual(len(base64.b64decode(integrity, validate=True)), 64)
        files = {item['path']: item for item in provenance['files']}
        self.assertEqual(set(files), {'tools/vendor/punycode-2.3.1.js',
                                      'tools/vendor/punycode-LICENSE.txt'})
        for name, metadata in files.items():
            with self.subTest(path=name):
                data = (ROOT / name).read_bytes()
                self.assertEqual(len(data), metadata['bytes'])
                self.assertEqual(sha256(data).hexdigest(), metadata['sha256'])

    def test_control_without_preload_reproduces_dep0040(self):
        # This control proves the selected test runtime still detects the bug.
        result = self.run_node("require('punycode');", preload=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DEP0040', result.stderr)
        self.assertIn('punycode', result.stderr)


if __name__ == '__main__':
    unittest.main()
