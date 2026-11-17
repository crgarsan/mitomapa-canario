"""Preparation remains a manual, read-only operation on the reviewed main SHA."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def workflow(self):
        return (ROOT / '.github/workflows/prepare-release.yml').read_text()

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
        self.assertEqual(text.count('${{ inputs.source_commit }}'), 2)
        self.assertIn('RELEASE_SOURCE_COMMIT: ${{ inputs.source_commit }}', text)
        self.assertIn('ref: ${{ inputs.source_commit }}', text)

    def test_the_bundle_is_verified_before_it_is_uploaded(self):
        text = self.workflow()
        self.assertIn('tools/historical_releases.py --check', text)
        self.assertLess(text.index('--verify-output'), text.index('actions/upload-artifact@'))
        self.assertIn('if-no-files-found: error', text)
        self.assertIn('include-hidden-files: false', text)


if __name__ == '__main__':
    unittest.main()
