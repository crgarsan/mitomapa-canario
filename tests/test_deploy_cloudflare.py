"""Run the credential boundary with a stub Wrangler and no Cloudflare access."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "deploy_cloudflare.sh"


class DeployCloudflareTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.marker = self.root / "invocation.json"
        wrangler = self.root / "node_modules" / ".bin" / "wrangler"
        wrangler.parent.mkdir(parents=True)
        wrangler.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path('invocation.json').write_text(json.dumps({\n"
            "    'args': sys.argv[1:],\n"
            "    'token': os.environ.get('CLOUDFLARE_API_TOKEN'),\n"
            "    'account': os.environ.get('CLOUDFLARE_ACCOUNT_ID'),\n"
            "}))\n"
            "sys.exit(int(os.environ.get('WRANGLER_EXIT_CODE', '0')))\n",
            encoding="utf-8",
        )
        wrangler.chmod(0o755)
        self.env = {
            "PATH": os.environ["PATH"],
            "HOME": str(self.root),
        }

    def run_deploy(self, **credentials):
        return subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=self.root,
            env={**self.env, **credentials},
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_missing_credentials_never_starts_wrangler(self):
        cases = [
            {},
            {"CLOUDFLARE_API_TOKEN": "test-token"},
            {"CLOUDFLARE_ACCOUNT_ID": "test-account"},
            {"CLOUDFLARE_API_TOKEN": "", "CLOUDFLARE_ACCOUNT_ID": "test-account"},
            {"CLOUDFLARE_API_TOKEN": "test-token", "CLOUDFLARE_ACCOUNT_ID": ""},
        ]
        for credentials in cases:
            with self.subTest(credentials=credentials):
                result = self.run_deploy(**credentials)
                self.assertEqual(result.returncode, 1)
                self.assertIn("deployment refused", result.stderr)
                self.assertFalse(self.marker.exists())
                self.assertNotIn("test-token", result.stdout + result.stderr)
                self.assertNotIn("test-account", result.stdout + result.stderr)

    def test_complete_credentials_deploy_only_the_configured_worker(self):
        result = self.run_deploy(
            CLOUDFLARE_API_TOKEN="test-token",
            CLOUDFLARE_ACCOUNT_ID="test-account",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        invocation = json.loads(self.marker.read_text(encoding="utf-8"))
        self.assertEqual(invocation["args"], ["deploy", "--config", "wrangler.jsonc"])
        self.assertEqual(invocation["token"], "test-token")
        self.assertEqual(invocation["account"], "test-account")
        self.assertEqual(result.stdout + result.stderr, "")

    def test_wrangler_failure_is_propagated(self):
        result = self.run_deploy(
            CLOUDFLARE_API_TOKEN="test-token",
            CLOUDFLARE_ACCOUNT_ID="test-account",
            WRANGLER_EXIT_CODE="42",
        )
        self.assertTrue(self.marker.exists())
        self.assertEqual(result.returncode, 42)


if __name__ == "__main__":
    unittest.main()
