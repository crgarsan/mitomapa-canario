"""Preparation remains a manual, read-only operation on the reviewed main SHA."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def workflow(self):
        return (ROOT / '.github/workflows/prepare-release.yml').read_text()

    def pre_checkout_guard(self):
        steps = re.findall(r'(?ms)^      - (.*?)(?=^      - |\Z)', self.workflow())
        checkout = next(i for i, step in enumerate(steps) if 'uses: actions/checkout@' in step)
        embedded = next((re.search(r"(?ms)^          python3 - <<'PY'\n(.*?)^          PY\n", step)
                         for step in steps[:checkout] if "python3 - <<'PY'" in step), None)
        self.assertIsNotNone(embedded, 'The input must be checked before checkout')
        return textwrap.dedent(embedded.group(1))

    def run_pre_checkout_guard(self, requested, event_sha):
        with tempfile.TemporaryDirectory() as directory:
            return subprocess.run(
                [sys.executable, '-c', self.pre_checkout_guard()], cwd=directory,
                env={'RELEASE_SOURCE_COMMIT': requested, 'GITHUB_SHA': event_sha},
                capture_output=True, text=True, check=False,
            )

    def test_preparation_has_no_publication_or_credential_permissions(self):
        text = self.workflow()
        trigger = text.split('jobs:', 1)[0]
        self.assertIn('workflow_dispatch:', trigger)
        self.assertNotRegex(trigger, r'(?m)^  (?:push|pull_request|schedule):')
        self.assertIn('contents: read', text)
        self.assertNotRegex(text, r'\b(?:contents|pages|id-token|actions):\s*write')
        for forbidden in ('gh release', 'wrangler', 'deploy-pages', 'secrets.', 'enable_auto_merge'):
            self.assertNotIn(forbidden, text)

    def test_actions_are_immutable_and_checkout_does_not_persist_credentials(self):
        text = self.workflow()
        actions = re.findall(r'uses:\s*(\S+)', text)
        self.assertGreaterEqual(len(actions), 3)
        for action in actions:
            self.assertRegex(action, r'^[\w-]+/[\w-]+@[0-9a-f]{40}$')
        self.assertIn('persist-credentials: false', text)

    def test_current_main_and_the_input_commit_are_both_checked(self):
        text = self.workflow()
        self.assertIn("github.ref == 'refs/heads/main'", text)
        self.assertIn("github.repository == 'crgarsan/mitomapa-canario'", text)
        self.assertIn("re.fullmatch(r'[0-9a-f]{40}'", text)
        self.assertIn('refs/heads/main:refs/remotes/release/main', text)
        self.assertIn('git rev-parse HEAD', text)
        self.assertIn('git rev-parse refs/remotes/release/main', text)
        # The user input is passed as data, never interpolated into a shell run.
        self.assertEqual(text.count('${{ inputs.source_commit }}'), 1)
        self.assertIn('RELEASE_SOURCE_COMMIT: ${{ inputs.source_commit }}', text)
        self.assertIn('ref: ${{ github.sha }}', text)

    def test_pre_checkout_guard_accepts_the_dispatch_main_commit(self):
        result = self.run_pre_checkout_guard('a' * 40, 'a' * 40)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pre_checkout_guard_rejects_a_different_valid_commit(self):
        result = self.run_pre_checkout_guard('b' * 40, 'a' * 40)
        self.assertNotEqual(result.returncode, 0)

    def test_pre_checkout_guard_rejects_malformed_input(self):
        for requested in ('', 'a' * 39, 'a' * 41, 'A' * 40, 'v4.10.0',
                          'a' * 40 + '\n', '$(printf x)'):
            with self.subTest(requested=requested):
                result = self.run_pre_checkout_guard(requested, 'a' * 40)
                self.assertNotEqual(result.returncode, 0)

    def test_the_bundle_is_verified_before_it_is_uploaded(self):
        text = self.workflow()
        self.assertIn('tools/historical_releases.py --check', text)
        self.assertLess(text.index('--verify-output'), text.index('actions/upload-artifact@'))
        self.assertIn('if-no-files-found: error', text)
        self.assertIn('include-hidden-files: false', text)


if __name__ == '__main__':
    unittest.main()
