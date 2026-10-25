"""Exercise the optional HTTPS policy without contacting Cloudflare."""

import copy
from email.message import Message
import importlib.util
from http.client import IncompleteRead
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl
from contextlib import redirect_stdout


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "ensure_https_redirect.py"
ACCOUNT = "a" * 32
ZONE = "b" * 32
RULESET = "c" * 32
TOKEN = "private-test-token"
OWNED = {
    "ref": "mitomapa_https_only",
    "description": "Redirect only the MitoMapa custom hostname from HTTP to HTTPS",
    "expression": '(http.host eq "mitomapacanario.org" and not ssl)',
    "action": "redirect",
    "enabled": True,
    "action_parameters": {"from_value": {
        "target_url": {"expression": 'concat("https://mitomapacanario.org", http.request.uri.path)'},
        "status_code": 301,
        "preserve_query_string": True,
    }},
}


def existing_rule(identifier="d", **changes):
    return {"id": identifier * 32, "ref": "other-" + identifier,
            "expression": '(http.host eq "other.example")', "enabled": True,
            "action": "redirect", "action_parameters": {"from_value": {
                "target_url": {"value": "https://other.example/welcome"},
                "status_code": 302, "preserve_query_string": False}}, **changes}


def owned_rule(identifier="e", **changes):
    return {**copy.deepcopy(OWNED), "id": identifier * 32, "version": "1", **changes}


class Cloudflare:
    """Stateful HTTP boundary: the real configure logic reads and changes rules."""

    def __init__(self, rules=None):
        self.ruleset = None if rules is None else {
            "id": RULESET, "kind": "zone", "phase": "http_request_dynamic_redirect",
            "name": "Existing redirects", "rules": copy.deepcopy(rules), "version": "1"}
        self.zones = [{"id": ZONE, "name": "mitomapacanario.org", "status": "active",
                       "account": {"id": ACCOUNT}}]
        self.total_count = 1
        self.requests = []
        self.mutations = []
        self.failure = None
        self.corrupt_reply = None

    def open(self, request, timeout):
        parsed = urlsplit(request.full_url)
        if (parsed.scheme, parsed.netloc) != ("https", "api.cloudflare.com"):
            raise AssertionError("Credentials must stay on the fixed HTTPS API origin")
        if request.get_header("Authorization") != "Bearer " + TOKEN:
            raise AssertionError("The configured token must authenticate the API request")
        self.requests.append((request.method, parsed.path, parse_qs(parsed.query)))
        if self.failure is not None:
            raise HTTPError(request.full_url, self.failure, "sensitive " + TOKEN + ACCOUNT,
                            {}, io.BytesIO((TOKEN + ACCOUNT).encode()))
        body = json.loads(request.data) if request.data is not None else None
        zone_path = "/client/v4/zones/" + ZONE + "/rulesets"
        if request.method == "GET" and parsed.path == "/client/v4/zones":
            if parse_qs(parsed.query) != {"name": ["mitomapacanario.org"],
                                        "account.id": [ACCOUNT], "match": ["all"],
                                        "status": ["active"]}:
                raise AssertionError("Zone discovery must include the exact scope filters")
            payload = {"success": True, "result": self.zones,
                       "result_info": {"total_count": self.total_count}}
        elif request.method == "GET" and parsed.path == zone_path + "/phases/http_request_dynamic_redirect/entrypoint":
            if self.ruleset is None:
                raise HTTPError(request.full_url, 404, "Not Found", {}, io.BytesIO())
            payload = {"success": True, "result": copy.deepcopy(self.ruleset)}
        elif request.method == "POST" and parsed.path == zone_path:
            if self.ruleset is not None or body != {
                "name": "MitoMapa HTTPS redirect", "kind": "zone",
                "phase": "http_request_dynamic_redirect", "rules": [OWNED]}:
                raise AssertionError("Only a new zone phase with the exact owned rule may be created")
            self.mutations.append((request.method, parsed.path, body))
            self.ruleset = {**body, "id": RULESET, "rules": [owned_rule()]}
            payload = {"success": True, "result": copy.deepcopy(self.ruleset)}
        elif request.method == "POST" and parsed.path == zone_path + "/" + RULESET + "/rules":
            if body != {**OWNED, "position": {"index": 1}}:
                raise AssertionError("Insert the exact owned rule first without replacing the ruleset")
            self.mutations.append((request.method, parsed.path, body))
            self.ruleset["rules"].insert(0, owned_rule())
            payload = {"success": True, "result": copy.deepcopy(self.ruleset)}
        elif request.method == "PATCH" and parsed.path == zone_path + "/" + RULESET + "/rules/" + "e" * 32:
            if body != {"position": {"index": 1}}:
                raise AssertionError("An owned rule move must not rewrite its configuration")
            self.mutations.append((request.method, parsed.path, body))
            owned = next(rule for rule in self.ruleset["rules"] if rule["id"] == "e" * 32)
            self.ruleset["rules"].remove(owned)
            self.ruleset["rules"].insert(0, owned)
            payload = {"success": True, "result": copy.deepcopy(self.ruleset)}
        else:
            raise AssertionError("Unexpected API request: " + request.method + " " + parsed.path)
        if self.corrupt_reply is not None:
            payload = self.corrupt_reply(payload, request.method)
        return io.BytesIO(json.dumps(payload).encode())


class HttpsRedirectTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "The optional HTTPS configuration is missing")
        spec = importlib.util.spec_from_file_location("ensure_https_redirect", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def configure(self, cloudflare):
        return self.module.configure(TOKEN, ACCOUNT, opener=cloudflare)

    def test_creates_only_missing_zone_phase_with_verified_exact_rule(self):
        cloudflare = Cloudflare()
        self.assertEqual(self.configure(cloudflare), "configured")
        self.assertEqual(cloudflare.ruleset["rules"], [owned_rule()])
        self.assertEqual(len(cloudflare.mutations), 1)

    def test_inserts_first_and_preserves_other_rule_configuration_ids_and_order(self):
        previous = [existing_rule(), existing_rule("f", enabled=False)]
        cloudflare = Cloudflare(previous)
        self.assertEqual(self.configure(cloudflare), "configured")
        self.assertEqual(cloudflare.ruleset["rules"], [owned_rule()] + previous)

    def test_second_run_is_a_verified_noop(self):
        cloudflare = Cloudflare([existing_rule()])
        self.configure(cloudflare)
        self.assertEqual(self.configure(cloudflare), "already configured")
        self.assertEqual(len(cloudflare.mutations), 1)

    def test_identical_owned_rule_later_is_moved_without_rewriting(self):
        previous = [existing_rule(), owned_rule(), existing_rule("f")]
        cloudflare = Cloudflare(previous)
        self.assertEqual(self.configure(cloudflare), "configured (moved first)")
        self.assertEqual(cloudflare.ruleset["rules"], [previous[1], previous[0], previous[2]])
        self.assertEqual(cloudflare.mutations[0][0], "PATCH")

    def test_ref_collisions_and_differently_configured_owned_rules_never_mutate(self):
        for rules in [[owned_rule(enabled=False)], [owned_rule(expression="true")],
                      [owned_rule(), owned_rule("f")], [owned_rule(extra_setting=True)]]:
            with self.subTest(rules=rules):
                cloudflare = Cloudflare(rules)
                with self.assertRaises(self.module.RedirectBlocked):
                    self.configure(cloudflare)
                self.assertEqual(cloudflare.mutations, [])
                self.assertEqual(cloudflare.ruleset["rules"], rules)

    def test_wrong_multiple_or_malformed_zone_results_never_mutate(self):
        valid = Cloudflare().zones[0]
        for zones, total in [([], 0), ([valid, valid], 2), ([valid], 2),
                             ([{**valid, "name": "other.example"}], 1),
                             ([{**valid, "status": "pending"}], 1),
                             ([{**valid, "account": {"id": "f" * 32}}], 1),
                             ([{**valid, "id": "../elsewhere"}], 1), (None, 1)]:
            with self.subTest(zones=zones, total=total):
                cloudflare = Cloudflare([])
                cloudflare.zones, cloudflare.total_count = zones, total
                with self.assertRaises(self.module.RedirectBlocked):
                    self.configure(cloudflare)
                self.assertEqual(len(cloudflare.requests), 1)
                self.assertEqual(cloudflare.mutations, [])

    def test_malformed_or_wrong_scope_rulesets_never_mutate(self):
        for changes in [{"kind": "account"}, {"phase": "http_request_firewall_custom"},
                        {"id": "invalid"}, {"rules": None}, {"rules": [{}]},
                        {"rules": [existing_rule(), existing_rule()]}]:
            with self.subTest(changes=changes):
                cloudflare = Cloudflare([])
                cloudflare.ruleset.update(changes)
                with self.assertRaises(self.module.RedirectBlocked):
                    self.configure(cloudflare)
                self.assertEqual(cloudflare.mutations, [])

    def test_write_is_not_reported_configured_if_response_alters_unrelated_rules(self):
        cloudflare = Cloudflare([existing_rule()])
        def corrupt(payload, method):
            if method == "POST":
                payload["result"]["rules"][1]["enabled"] = False
            return payload
        cloudflare.corrupt_reply = corrupt
        with self.assertRaises(self.module.RedirectBlocked):
            self.configure(cloudflare)
        self.assertEqual(len(cloudflare.mutations), 1)

    def test_move_response_must_preserve_the_owned_rule_id(self):
        cloudflare = Cloudflare([existing_rule(), owned_rule()])
        def corrupt(payload, method):
            if method == "PATCH":
                payload["result"]["rules"][0]["id"] = "9" * 32
            return payload
        cloudflare.corrupt_reply = corrupt
        with self.assertRaises(self.module.RedirectBlocked):
            self.configure(cloudflare)

    def test_malformed_success_envelope_is_blocked(self):
        for payload in [None, {"success": False}, {"success": True, "result": {}},
                        {"success": "true", "result": []}]:
            with self.subTest(payload=payload):
                cloudflare = Cloudflare([])
                cloudflare.corrupt_reply = lambda *args: payload
                with self.assertRaises(self.module.RedirectBlocked):
                    self.configure(cloudflare)
                self.assertEqual(cloudflare.mutations, [])

    def test_http_errors_are_nonblocking_sanitized_github_warnings(self):
        for code in [403, 429, 500]:
            with self.subTest(code=code):
                cloudflare = Cloudflare([])
                cloudflare.failure = code
                output = io.StringIO()
                with patch.dict(self.module.os.environ, {
                    "CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT}, clear=True), \
                        patch.object(self.module, "build_opener", return_value=cloudflare), \
                        redirect_stdout(output):
                    self.assertEqual(self.module.main(), 0)
                self.assertIn("::warning", output.getvalue())
                self.assertIn("status: blocked", output.getvalue())
                self.assertIn("HTTP " + str(code), output.getvalue())
                self.assertNotIn(TOKEN, output.getvalue())
                self.assertNotIn(ACCOUNT, output.getvalue())
                self.assertEqual(cloudflare.mutations, [])

    def test_missing_credentials_are_nonblocking_and_do_not_make_requests(self):
        output = io.StringIO()
        with patch.dict(self.module.os.environ, {}, clear=True), \
                patch.object(self.module, "build_opener", side_effect=AssertionError("No request allowed")), \
                redirect_stdout(output):
            self.assertEqual(self.module.main(), 0)
        self.assertIn("::warning", output.getvalue())
        self.assertIn("status: blocked", output.getvalue())

    def test_interrupted_http_response_is_a_sanitized_nonblocking_warning(self):
        class InterruptedResponse(io.BytesIO):
            def read(self, *args):
                raise IncompleteRead((TOKEN + ACCOUNT).encode())
        cloudflare = Cloudflare([])
        cloudflare.open = lambda request, timeout: InterruptedResponse()
        output = io.StringIO()
        with patch.dict(self.module.os.environ, {
            "CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT}, clear=True), \
                patch.object(self.module, "build_opener", return_value=cloudflare), \
                redirect_stdout(output):
            try:
                returncode = self.module.main()
            except Exception as error:
                self.fail("Transport failure escaped instead of warning: " + type(error).__name__)
        self.assertEqual(returncode, 0)
        self.assertIn("::warning", output.getvalue())
        self.assertIn("status: blocked", output.getvalue())
        self.assertNotIn(TOKEN, output.getvalue())
        self.assertNotIn(ACCOUNT, output.getvalue())

    def test_failed_phase_creation_never_retries_or_replaces_an_entrypoint(self):
        cloudflare = Cloudflare()
        original_open = cloudflare.open
        denied = []
        def deny_create(request, timeout):
            if request.method == "POST":
                denied.append(request)
                raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO())
            return original_open(request, timeout)
        cloudflare.open = deny_create
        with self.assertRaises(self.module.RedirectBlocked):
            self.configure(cloudflare)
        self.assertEqual(len(denied), 1)
        self.assertEqual(len(cloudflare.requests), 2)
        self.assertIsNone(cloudflare.ruleset)

    def test_main_reports_only_verified_configured_and_noop_states(self):
        cloudflare = Cloudflare([])
        with patch.dict(self.module.os.environ, {
            "CLOUDFLARE_API_TOKEN": TOKEN, "CLOUDFLARE_ACCOUNT_ID": ACCOUNT}, clear=True), \
                patch.object(self.module, "build_opener", return_value=cloudflare):
            for state in ["configured", "already configured"]:
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(self.module.main(), 0)
                self.assertIn("status: " + state, output.getvalue())
                self.assertIn("API state verified", output.getvalue())
        self.assertEqual(len(cloudflare.mutations), 1)

    def test_http_redirects_never_forward_the_authenticated_request(self):
        for code in [301, 302, 303, 307, 308]:
            for destination in ["https://attacker.example/steal", "http://api.cloudflare.com/steal",
                                "https://api.cloudflare.com/client/v4/elsewhere"]:
                with self.subTest(code=code, destination=destination):
                    seen = []
                    class RedirectTransport(BaseHandler):
                        handler_order = 1

                        def https_open(self, request):
                            seen.append(request)
                            headers = Message()
                            headers["Location"] = destination
                            response = addinfourl(io.BytesIO(b"{}"), headers, request.full_url, code)
                            response.msg = "Redirect"
                            return response
                        http_open = https_open
                    def local_opener(*handlers):
                        return build_opener(*handlers, RedirectTransport())
                    with patch.object(self.module, "build_opener", side_effect=local_opener):
                        with self.assertRaises(self.module.RedirectBlocked):
                            self.module.configure(TOKEN, ACCOUNT)
                    self.assertEqual(len(seen), 1, "A redirect must never forward API authorization")


if __name__ == "__main__":
    unittest.main()
