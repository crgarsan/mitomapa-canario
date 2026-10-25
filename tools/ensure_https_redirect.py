#!/usr/bin/env python3
"""Optionally enforce apex HTTPS through one verified Cloudflare redirect rule."""

import json
import os
import re
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


API = "https://api.cloudflare.com/client/v4"
HOSTNAME = "mitomapacanario.org"
PHASE = "http_request_dynamic_redirect"
RULE = {
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


class RedirectBlocked(Exception):
    """A sanitized reason why automatic configuration could not be verified."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{32}", value) is not None


def ruleset_rules(ruleset):
    if (not isinstance(ruleset, dict) or ruleset.get("kind") != "zone"
            or ruleset.get("phase") != PHASE or not identifier(ruleset.get("id"))
            or not isinstance(ruleset.get("rules"), list)):
        raise RedirectBlocked("The redirect ruleset has an unexpected scope or format.")
    seen = set()
    for rule in ruleset["rules"]:
        if (not isinstance(rule, dict) or not identifier(rule.get("id"))
                or rule["id"] in seen or type(rule.get("enabled")) is not bool
                or any(not isinstance(rule.get(key), str) or not rule[key]
                       for key in ("ref", "action", "expression"))
                or ("action_parameters" in rule and not isinstance(rule["action_parameters"], dict))):
            raise RedirectBlocked("The existing redirect rules are malformed.")
        seen.add(rule["id"])
    return ruleset["rules"]


def owned_rule_matches(rule):
    configuration = {key: value for key, value in rule.items()
                     if key not in ("id", "version", "last_updated")}
    return json.dumps(configuration, sort_keys=True) == json.dumps(RULE, sort_keys=True)


def configure(token, account, opener=None):
    if (not isinstance(token, str) or not token or "\r" in token or "\n" in token
            or not identifier(account)):
        raise RedirectBlocked("The existing Cloudflare credentials are missing or invalid.")
    # Retain urllib's configured proxy and normal TLS/CA verification.
    opener = opener if opener is not None else build_opener(NoRedirect())

    def request(method, path, body=None, missing_ok=False):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(API + path, data=data, method=method, headers={
            "Authorization": "Bearer " + token, "Content-Type": "application/json"})
        try:
            with opener.open(req, timeout=30) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise RedirectBlocked("The Cloudflare response exceeded the safety limit.")
            payload = json.loads(raw)
        except HTTPError as error:
            if error.code == 404 and missing_ok:
                return None
            code = error.code if type(error.code) is int else "unknown"
            raise RedirectBlocked(f"Cloudflare API request failed (HTTP {code}).") from None
        except (OSError, ValueError, UnicodeError, HTTPException):
            raise RedirectBlocked("The Cloudflare API response could not be read or verified.") from None
        if not isinstance(payload, dict) or payload.get("success") is not True or "result" not in payload:
            raise RedirectBlocked("Cloudflare did not return a successful, complete API response.")
        return payload

    zones_reply = request("GET", "/zones?" + urlencode({
        "name": HOSTNAME, "account.id": account, "match": "all", "status": "active"}))
    zones, info = zones_reply["result"], zones_reply.get("result_info")
    if (not isinstance(zones, list) or len(zones) != 1 or not isinstance(info, dict)
            or type(info.get("total_count")) is not int or info["total_count"] != 1):
        raise RedirectBlocked("Exactly one matching active Cloudflare zone is required.")
    zone = zones[0]
    if (not isinstance(zone, dict) or zone.get("name") != HOSTNAME or zone.get("status") != "active"
            or not identifier(zone.get("id")) or not isinstance(zone.get("account"), dict)
            or zone["account"].get("id") != account):
        raise RedirectBlocked("The returned zone does not match the requested hostname and account.")

    base = "/zones/" + zone["id"] + "/rulesets"
    entrypoint = request("GET", base + "/phases/" + PHASE + "/entrypoint", missing_ok=True)
    expected_id, expected_owned_id, remaining, status = None, None, [], "configured"
    if entrypoint is None:
        updated = request("POST", base, {"name": "MitoMapa HTTPS redirect", "kind": "zone",
                                        "phase": PHASE, "rules": [RULE]})["result"]
    else:
        ruleset = entrypoint["result"]
        rules = ruleset_rules(ruleset)
        expected_id = ruleset["id"]
        owned = [rule for rule in rules if rule["ref"] == RULE["ref"]]
        if len(owned) > 1 or (owned and not owned_rule_matches(owned[0])):
            raise RedirectBlocked("The reserved HTTPS rule reference has conflicting configuration.")
        if owned and rules[0] == owned[0]:
            return "already configured"
        remaining = [rule for rule in rules if not owned or rule["id"] != owned[0]["id"]]
        rule_path = base + "/" + expected_id + "/rules"
        if owned:
            expected_owned_id = owned[0]["id"]
            updated = request("PATCH", rule_path + "/" + owned[0]["id"],
                              {"position": {"index": 1}})["result"]
            status = "configured (moved first)"
        else:
            updated = request("POST", rule_path, {**RULE, "position": {"index": 1}})["result"]

    verified = ruleset_rules(updated)
    if (expected_id is not None and updated["id"] != expected_id) or (
            not verified or not owned_rule_matches(verified[0]) or verified[1:] != remaining
            or (expected_owned_id is not None and verified[0]["id"] != expected_owned_id)):
        raise RedirectBlocked("The API response did not verify the first HTTPS rule and preserved existing rules.")
    return status


def main():
    try:
        status = configure(os.environ.get("CLOUDFLARE_API_TOKEN", ""),
                           os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""))
    except RedirectBlocked as error:
        print("::warning title=Cloudflare HTTPS redirect::HTTPS redirect status: blocked; "
              + str(error) + " Review Single Redirect access, quota and configuration manually; publication continues.")
    else:
        print(f"HTTPS redirect status: {status}; API state verified for {HOSTNAME}. Public HTTP behavior remains unchecked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
