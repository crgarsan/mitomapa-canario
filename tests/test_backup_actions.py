"""Check the backup workflow against offline, immutable Pages action metadata.

These tests inspect upstream action contracts and execute only our Python address
guard. They do not execute a GitHub action bundle, call an API, or publish a site.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / 'fixtures/pages-actions'


def scalar(text, name):
    """Read one scalar from the simple mappings used by these action contracts."""
    match = re.search(r'(?m)^[ \t]*' + re.escape(name) + r':[ \t]*([^\n]+)$', text)
    return match.group(1).split(' #', 1)[0].strip().strip("'\"") if match else None


def ports(metadata, section):
    # The complete upstream files are retained; only their flat public ports
    # are needed here. This deliberately does not implement a YAML loader.
    match = re.search(r'(?ms)^' + section + r':\n(.*?)(?=^\S|\Z)', metadata)
    return dict(re.findall(r'(?ms)^  ([\w-]+):\n(.*?)(?=^  \S|\Z)',
                           match.group(1))) if match else {}


class BackupActionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / '.github/workflows/deploy-backup.yml').read_text()
        cls.steps = re.findall(r'(?ms)^      - (.*?)(?=^      - |\Z)', cls.workflow)
        cls.snapshots = json.loads((FIXTURES / 'provenance.json').read_text())['snapshots']

    def action_step(self, action):
        found = [step for step in self.steps
                 if (scalar(step, 'uses') or '').startswith(action + '@')]
        self.assertEqual(len(found), 1, 'Expected one workflow step for ' + action)
        return found[0]

    def selected_metadata(self, step):
        selected = scalar(step, 'uses')
        action, ref = selected.rsplit('@', 1)
        self.assertRegex(ref, r'^[0-9a-f]{40}$', 'Action refs must be immutable: ' + selected)
        snapshot = next((item for item in self.snapshots
                         if item['action'] == action and item['commit'] == ref), None)
        self.assertIsNotNone(snapshot, 'Review and retain upstream metadata for ' + selected)
        self.assertEqual(snapshot['source_url'],
                         f'https://raw.githubusercontent.com/{action}/{ref}/action.yml')
        payload = (FIXTURES / snapshot['file']).read_bytes()
        self.assertEqual(sha256(payload).hexdigest(), snapshot['sha256'],
                         'The upstream metadata snapshot changed: ' + selected)
        metadata = payload.decode('utf-8')
        runtime = re.search(r'(?ms)^runs:\n(.*?)(?=^\S|\Z)', metadata)
        self.assertIsNotNone(runtime, 'Missing upstream action runtime: ' + selected)
        return {'selected': selected, 'runtime': scalar(runtime.group(1), 'using'),
                'inputs': ports(metadata, 'inputs'), 'outputs': ports(metadata, 'outputs')}

    def supplied_inputs(self, step):
        return {name: value.strip().strip("'\"")
                for name, value in re.findall(r'(?m)^          ([\w-]+):[ \t]*([^\n]+)$', step)}

    def test_workflow_selects_node24_actions(self):
        # Regression: a valid SHA can still select Node20 and cause the warning.
        # Both old snapshots remain resolvable, so this checks their runtime,
        # rather than comparing the workflow to a hard-coded replacement SHA.
        for action in ('actions/configure-pages', 'actions/deploy-pages'):
            with self.subTest(action=action):
                metadata = self.selected_metadata(self.action_step(action))
                self.assertEqual(metadata['runtime'], 'node24',
                                 metadata['selected'] + ' declares ' + metadata['runtime'])

    def test_selected_actions_support_the_workflow_consumers(self):
        # Regressions: unknown inputs, missing consumed outputs, enabling Pages,
        # or deploying an artifact name different from the validated upload.
        selected = {}
        for action in ('actions/configure-pages', 'actions/deploy-pages'):
            step = self.action_step(action)
            metadata = self.selected_metadata(step)
            supplied = self.supplied_inputs(step)
            self.assertLessEqual(set(supplied), set(metadata['inputs']))
            for name, declaration in metadata['inputs'].items():
                if scalar(declaration, 'required') == 'true' and scalar(declaration, 'default') is None:
                    self.assertIn(name, supplied, action + ' requires ' + name)
            step_id = scalar(step, 'id')
            self.assertIsNotNone(step_id)
            consumed = set(re.findall(r'\$\{\{\s*steps\.' + re.escape(step_id)
                                      + r'\.outputs\.([\w-]+)\s*\}\}', self.workflow))
            self.assertLessEqual(consumed, set(metadata['outputs']))
            selected[action] = (metadata, supplied, consumed)

        configure, supplied, consumed = selected['actions/configure-pages']
        enablement = supplied.get('enablement', scalar(configure['inputs']['enablement'], 'default'))
        self.assertEqual(enablement, 'false')
        self.assertLessEqual({'host', 'base_path'}, consumed)

        deployment, supplied, consumed = selected['actions/deploy-pages']
        artifact = supplied.get('artifact_name', scalar(deployment['inputs']['artifact_name'], 'default'))
        upload = self.supplied_inputs(self.action_step('actions/upload-pages-artifact'))
        # upload-pages-artifact's documented default name is github-pages.
        self.assertEqual(artifact, upload.get('name', 'github-pages'))
        self.assertIn('page_url', consumed)

    def test_address_guard_uses_action_outputs_and_rejects_other_sites(self):
        # Execute our real guard, including its workflow env bindings, without
        # running configure-pages or contacting GitHub.
        configure_step = self.action_step('actions/configure-pages')
        configure_id = scalar(configure_step, 'id')
        metadata = self.selected_metadata(configure_step)
        guard = next(step for step in self.steps
                     if "python3 - <<'PY'" in step and 'PAGES_HOST' in step)
        embedded = re.search(r"(?ms)^          python3 - <<'PY'\n(.*?)^          PY\n", guard)
        self.assertIsNotNone(embedded)
        script = textwrap.dedent(embedded.group(1))
        bindings = dict(re.findall(r'(?m)^          (PAGES_HOST|PAGES_PATH):[ \t]*(.+)$', guard))
        self.assertEqual(set(bindings), {'PAGES_HOST', 'PAGES_PATH'})
        output_names = {}
        for variable, expression in bindings.items():
            binding = re.fullmatch(r'\$\{\{\s*steps\.' + re.escape(configure_id)
                                   + r'\.outputs\.([\w-]+)\s*\}\}', expression)
            self.assertIsNotNone(binding, variable + ' must use configure-pages output')
            self.assertIn(binding.group(1), metadata['outputs'])
            output_names[variable] = binding.group(1)

        cases = [
            ('crgarsan.github.io', '/mitomapa-canario', True),
            ('crgarsan.github.io', '/mitomapa-canario/', True),
            ('mitomapa.example', '/mitomapa-canario', False),
            ('crgarsan.github.io', '/another-project', False),
            ('crgarsan.github.io', '', False),
            ('', '/mitomapa-canario', False),
        ]
        for host, path, accepted in cases:
            with self.subTest(host=host, path=path), tempfile.TemporaryDirectory() as directory:
                outputs = {'host': host, 'base_path': path}
                env = {variable: outputs[name] for variable, name in output_names.items()}
                result = subprocess.run([sys.executable, '-c', script], cwd=directory,
                                        env=env, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode == 0, accepted, result.stderr)


if __name__ == '__main__':
    unittest.main()
