"""Exercise publication with a local Wrangler substitute and fictitious credentials."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
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
                if os.environ.get('SIMULATE_TIMEOUT'):
                    import subprocess, time
                    child = subprocess.Popen([sys.executable, '-c',
                        "import time; from pathlib import Path; time.sleep(1.8); "
                        "Path('late-activation').write_text('must not activate')"])
                    Path('child.pid').write_text(str(child.pid))
                    print(os.environ['CLOUDFLARE_API_TOKEN'], flush=True)
                    print(os.environ['CLOUDFLARE_ACCOUNT_ID'], file=sys.stderr, flush=True)
                    time.sleep(8)
                if os.environ.get('DEPLOY_ELAPSED'):
                    with Path('elapsed.jsonl').open('a') as stream:
                        stream.write(os.environ['DEPLOY_ELAPSED'] + '\\n')
                responses = json.loads(os.environ.get('DEPLOY_RESPONSES', '[]'))
                if responses:
                    calls = [json.loads(line) for line in Path('calls.jsonl').read_text().splitlines()]
                    index = sum(call['args'][:2] == ['versions', 'deploy'] for call in calls) - 1
                    if index >= len(responses):
                        sys.exit(99)
                    response = responses[index]
                    if 'elapsed' in response:
                        with Path('elapsed.jsonl').open('a') as stream:
                            stream.write(str(response['elapsed']) + '\\n')
                    if response.get('activated'):
                        with Path('activated.jsonl').open('a') as stream:
                            stream.write(json.dumps(args[2]) + '\\n')
                    print(response.get('stdout', ''), end='')
                    print(response.get('stderr', ''), file=sys.stderr, end='')
                    sys.exit(response.get('exit', 0))
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
        # Keep real subprocess/file behaviour and replace only the test clock.
        bootstrap = """
import json, os, runpy, subprocess, time
from pathlib import Path
elapsed = [0.0]
clock_calls = [0]
clock = time.monotonic
def sleep(seconds):
    with Path('waits.jsonl').open('a') as stream:
        stream.write(json.dumps(seconds) + '\\n')
    elapsed[0] += seconds
def monotonic():
    clock_calls[0] += 1
    recorded = Path('elapsed.jsonl')
    spent = sum(float(v) for v in recorded.read_text().splitlines()) if recorded.exists() else 0
    # Give the real launcher/child tree a short deadline, without mocking the
    # process timeout or termination that the regression must exercise.
    timeout_offset = 179 if os.environ.get('SIMULATE_TIMEOUT') and clock_calls[0] > 1 else 0
    # Budget cases use only virtual time, independent of runner load.
    # The process-tree timeout case retains the real monotonic clock.
    current = clock() if os.environ.get('SIMULATE_TIMEOUT') else 1000.0
    return current + elapsed[0] + spent + timeout_offset
time.sleep = sleep
time.monotonic = monotonic
runpy.run_path(os.environ['DEPLOY_SCRIPT'], run_name='__main__')
"""
        command = [sys.executable, '-c', bootstrap]
        return subprocess.run(command, cwd=self.root,
                              env={**self.env, "DEPLOY_SCRIPT": str(ROOT / "tools/deploy_cloudflare.py"), **(credentials or {}), **extra},
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


    def missing_version(self, *, account=ACCOUNT, worker="mitomapa-canario", version=VERSION, code=100146):
        return {"exit": 1, "stderr": (
            "\x1b[31m✘ [ERROR]\x1b[0m A request to the Cloudflare API "
            f"(/accounts/{account}/workers/scripts/{worker}/versions/{version}) failed.\n"
            f"The requested Worker version could not be found. [code: {code}]\n")}

    def run_responses(self, responses, **extra):
        return self.run_deploy({"CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT},
                               DEPLOY_RESPONSES=json.dumps(responses), **extra)

    def waits(self):
        path = self.root / 'waits.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def activations(self):
        path = self.root / 'activated.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_missing_exact_version_retries_then_activates_once_without_another_upload(self):
        result = self.run_responses([self.missing_version(), self.missing_version(),
                                     {"exit": 0, "activated": True}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 3)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2, 4])
        self.assertEqual(self.activations(), [VERSION + '@100%'])

    def test_version_visible_after_ninety_seconds_activates_once_on_seventh_attempt(self):
        # The recurrence exhausted the old five-attempt cap. Cover later
        # readability beyond even its former nominal 60-second ceiling.
        # These are virtual sleeps; only the fictitious local CLI is executed.
        result = self.run_responses([self.missing_version()] * 6
                                    + [{"exit": 0, "activated": True}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 7)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2, 4, 8, 16, 30, 30])
        self.assertEqual(sum(self.waits()), 90)
        self.assertEqual(self.activations(), [VERSION + '@100%'])
        self.assertIn('180', result.stdout + result.stderr)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_persistent_missing_version_stops_after_nine_attempts_without_tenth_or_activation(self):
        result = self.run_responses([self.missing_version()] * 9
                                    + [{"exit": 0, "activated": True}])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 9)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2, 4, 8, 16, 30, 30, 30, 30])
        self.assertEqual(self.activations(), [])
        self.assertRegex(result.stderr, r'\b(?:9|nine) attempts\b')
        self.assertIn('180', result.stdout + result.stderr)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_ninth_and_final_allowed_attempt_can_activate_the_same_version(self):
        result = self.run_responses([self.missing_version()] * 8
                                    + [{"exit": 0, "activated": True}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 9)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2, 4, 8, 16, 30, 30, 30, 30])
        self.assertEqual(self.activations(), [VERSION + '@100%'])

    def test_other_version_account_worker_auth_and_ambiguous_errors_never_retry(self):
        wrong = 'fe328dd1-51d7-4627-9fa3-4045beef4da9'
        errors = [self.missing_version(version=wrong), self.missing_version(account='other-account'),
                  self.missing_version(worker='other-worker'), self.missing_version(code=10000),
                  {"exit": 1, "stderr": "[ERROR] API request failed [code: 100146]"},
                  {"exit": 1, "stderr": self.missing_version()['stderr'] + "[ERROR] Auth failed [code: 10000]"},
                  {"exit": 1, "stderr": self.missing_version()['stderr'] + self.missing_version()['stderr']},
                  {"exit": 1, "stderr": self.missing_version()['stderr'].replace('/versions/' + VERSION, '/deployments')},
                  {"exit": 42, "stderr": self.missing_version()['stderr']}]
        for failure in errors:
            with self.subTest(failure=failure):
                for name in ('calls.jsonl', 'waits.jsonl', 'activated.jsonl', 'mitomapa-upload-123-1.jsonl'):
                    (self.root / name).unlink(missing_ok=True)
                result = self.run_responses([failure, {"exit": 0, "activated": True}])
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(len(self.calls()), 2)
                self.assertEqual(self.waits(), [])
                self.assertEqual(self.activations(), [])

    def test_timeout_aborts_without_retry_or_printing_captured_credentials(self):
        result = self.run_responses([self.missing_version()], SIMULATE_TIMEOUT='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.calls()), 2)  # upload and a real launcher with a child
        self.assertTrue((self.root / 'child.pid').is_file())
        time.sleep(2)
        self.assertFalse((self.root / 'late-activation').exists())
        self.assertEqual(self.waits(), [])
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_elapsed_cli_time_leaves_no_budget_for_the_first_retry_delay(self):
        # 179 seconds spent inside the CLI leaves less than the required 2s.
        result = self.run_responses([self.missing_version()] * 10, DEPLOY_ELAPSED='179')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(self.waits(), [])
        self.assertEqual(self.activations(), [])
        self.assertIn('180', result.stdout + result.stderr)
        self.assertIn('insufficient activation budget', result.stderr.lower())
        self.assertIn('retry 2/9 requires a 2s pause with 1.0s remaining', result.stderr)
        self.assertNotIn('exceeded', result.stderr.lower())
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_cli_elapsed_time_and_retry_sleep_share_one_deadline(self):
        # 160s first CLI + 2s sleep + 15s second CLI leaves <4s: no next sleep/call.
        first = {**self.missing_version(), 'elapsed': 160}
        second = {**self.missing_version(), 'elapsed': 15}
        result = self.run_responses([first, second, {"exit": 0, "activated": True}])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 2)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2])
        self.assertEqual(self.activations(), [])
        self.assertIn('180', result.stdout + result.stderr)
        self.assertIn('insufficient activation budget', result.stderr.lower())
        self.assertIn('retry 3/9 requires a 4s pause with 3.0s remaining', result.stderr)
        self.assertNotIn('exceeded', result.stderr.lower())
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_captured_cli_output_never_leaks_credentials(self):
        failure = self.missing_version()
        failure['stdout'] = TOKEN
        failure['stderr'] += ACCOUNT + TOKEN
        result = self.run_responses([failure, {"exit": 0, "activated": True,
                                              "stdout": TOKEN + ACCOUNT}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)


    def test_stdout_annotations_cannot_supply_a_missing_error_header_or_code(self):
        missing = self.missing_version()['stderr']
        failures = [
            {"exit": 1, "stdout": missing.replace('[ERROR]', ''),
             "stderr": '[ERROR] Unrelated activation failure'},
            {"exit": 1, "stdout": '[code: 100146]',
             "stderr": missing.replace('[code: 100146]', '')},
            {"exit": 1, "stderr": 'ordinary annotation: ' + missing.replace('\x1b[31m', '').replace('\x1b[0m', '')},
        ]
        for failure in failures:
            with self.subTest(failure=failure):
                for name in ('calls.jsonl', 'waits.jsonl', 'activated.jsonl', 'mitomapa-upload-123-1.jsonl'):
                    (self.root / name).unlink(missing_ok=True)
                result = self.run_responses([failure, {"exit": 0, "activated": True}])
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(len(self.calls()), 2)
                self.assertEqual(self.waits(), [])
                self.assertEqual(self.activations(), [])


    def test_late_ambiguous_post_error_never_retries_after_the_extended_lookup_window(self):
        failure = self.missing_version()
        failure['stderr'] = failure['stderr'].replace('/versions/' + VERSION, '/deployments')
        failure['activated'] = True
        result = self.run_responses([self.missing_version()] * 6
                                    + [failure, {"exit": 0, "activated": True}])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call['args'][:2] for call in self.calls()],
                         [['versions', 'upload']] + [['versions', 'deploy']] * 7)
        self.assertTrue(all(call['args'][2] == VERSION + '@100%' for call in self.calls()[1:]))
        self.assertEqual(self.waits(), [2, 4, 8, 16, 30, 30])
        self.assertEqual(self.activations(), [VERSION + '@100%'])
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertNotIn(ACCOUNT, result.stdout + result.stderr)

    def test_post_error_100146_does_not_repeat_a_possibly_completed_activation(self):
        failure = self.missing_version()
        failure['stderr'] = failure['stderr'].replace('/versions/' + VERSION, '/deployments')
        failure['activated'] = True
        result = self.run_responses([failure, {"exit": 0, "activated": True}])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(self.waits(), [])
        self.assertEqual(self.activations(), [VERSION + '@100%'])


if __name__ == "__main__":
    unittest.main()
