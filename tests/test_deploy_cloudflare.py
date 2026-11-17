"""Exercise publication with a local Wrangler substitute and fictitious credentials."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOKEN = "fictitious-production-token"
ACCOUNT = "fictitious-production-account"
VERSION = "147e050b-52e5-4abb-b0a4-8760c96d59f6"


class DeployCloudflareTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.marker = self.root / "calls.jsonl"
        (self.root / "wrangler.jsonc").write_bytes((ROOT / "wrangler.jsonc").read_bytes())
        cli = self.root / "node_modules" / ".bin" / "wrangler"
        cli.parent.mkdir(parents=True)
        cli.write_text("#!" + sys.executable + "\n" + textwrap.dedent('''\
            import json, os, sys
            from pathlib import Path
            args = sys.argv[1:]
            with Path('calls.jsonl').open('a') as stream:
                stream.write(json.dumps({
                    'args': args,
                    'token': os.environ.get('CLOUDFLARE_API_TOKEN'),
                    'account': os.environ.get('CLOUDFLARE_ACCOUNT_ID'),
                }) + '\\n')
            if args[:2] == ['versions', 'upload']:
                if os.environ.get('UPLOAD_EXIT_CODE'):
                    sys.exit(int(os.environ['UPLOAD_EXIT_CODE']))
                Path(os.environ['WRANGLER_OUTPUT_FILE_PATH']).write_text(os.environ['UPLOAD_REPORT'])
            else:
                sys.exit(int(os.environ.get('DEPLOY_EXIT_CODE', '0')))
            '''))
        cli.chmod(0o755)
        self.env = {
            "PATH": os.environ["PATH"],
            "RUNNER_TEMP": str(self.root),
            "GITHUB_SHA": "a" * 40,
            "GITHUB_RUN_ID": "123",
            "GITHUB_RUN_ATTEMPT": "1",
            "UPLOAD_REPORT": json.dumps({
                "type": "version-upload", "version": 1,
                "worker_name": "mitomapa-canario", "version_id": VERSION,
            }),
        }

    def run_deploy(self, credentials=None, **extra):
        command = [sys.executable, str(ROOT / "tools/deploy_cloudflare.py")]
        return subprocess.run(command, cwd=self.root,
                              env={**self.env, **(credentials or {}), **extra},
                              capture_output=True, text=True, timeout=10)

    def calls(self):
        if not self.marker.exists():
            return []
        return [json.loads(line) for line in self.marker.read_text().splitlines()]

    def test_missing_or_blank_credentials_stop_before_any_publication_side_effect(self):
        combinations = [
            {},
            {"CLOUDFLARE_API_TOKEN": TOKEN},
            {"CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
            {"CLOUDFLARE_API_TOKEN": "", "CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
            {"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ""},
            {"CLOUDFLARE_API_TOKEN": " \t\n", "CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
            {"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": "\t "},
            {"CF_API_TOKEN": TOKEN, "CF_ACCOUNT_ID": ACCOUNT},
            {"CLOUDFLARE_API_KEY": TOKEN, "CLOUDFLARE_EMAIL": "test@example.invalid"},
        ]
        for credentials in combinations:
            with self.subTest(credentials=credentials):
                for name in ("calls.jsonl", "mitomapa-story-video.json", "mitomapa-upload-123-1.jsonl"):
                    (self.root / name).unlink(missing_ok=True)
                result = self.run_deploy(credentials)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])
                self.assertFalse((self.root / "mitomapa-story-video.json").exists())
                self.assertFalse((self.root / "mitomapa-upload-123-1.jsonl").exists())
                self.assertNotIn(TOKEN, result.stdout + result.stderr)
                self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_valid_credentials_upload_and_activate_the_reported_version(self):
        result = self.run_deploy({"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT})
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual([call["args"][:2] for call in calls],
                         [["versions", "upload"], ["versions", "deploy"]])
        self.assertEqual(calls[1]["args"][2], VERSION + "@100%")
        self.assertTrue(all(call["token"] == TOKEN and call["account"] == ACCOUNT for call in calls))
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_upload_failure_does_not_activate_a_version(self):
        result = self.run_deploy({"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
                                 UPLOAD_EXIT_CODE="42")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call["args"][:2] for call in self.calls()], [["versions", "upload"]])

    def test_activation_failure_fails_the_publication(self):
        result = self.run_deploy({"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
                                 DEPLOY_EXIT_CODE="37")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.calls()), 2)


if __name__ == "__main__":
    unittest.main()
