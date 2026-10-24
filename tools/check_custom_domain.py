#!/usr/bin/env python3
"""Preview domain changes before Wrangler can replace existing DNS or bindings."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HOSTNAME = "mitomapacanario.org"
SERVICE = "mitomapa-canario"


class PreflightError(Exception):
    """The domain change cannot safely proceed unattended."""


def check_changeset(changeset):
    keys = ("added", "removed", "updated", "conflicting")
    if not isinstance(changeset, dict) or any(
        not isinstance(changeset.get(key), list) for key in keys
    ):
        raise PreflightError("Cloudflare did not return a complete domain preview.")
    if changeset["removed"]:
        raise PreflightError("The deployment would remove an existing custom domain; review it first.")
    if changeset["conflicting"]:
        raise PreflightError("The domain has conflicting DNS records; review them before linking it.")
    for key in ("added", "updated"):
        for domain in changeset[key]:
            if not isinstance(domain, dict) or domain.get("hostname") != HOSTNAME:
                raise PreflightError("The preview contains an unexpected domain.")
            if key == "updated" and domain.get("modified") is not False:
                raise PreflightError("An existing domain binding would change; review it first.")


def main():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not token or not account:
        raise PreflightError("Cloudflare deployment credentials are missing.")
    endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/"
        f"{SERVICE}/domains/changeset?replace_state=true"
    )
    request = Request(endpoint, method="POST", data=json.dumps([
        {"hostname": HOSTNAME}
    ]).encode(), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        try:
            details = json.loads(error.read()).get("errors", [])
            message = "; ".join(str(item.get("message", "")) for item in details if isinstance(item, dict))
        except (ValueError, TypeError, AttributeError):
            message = ""
        message = message.replace(token, "[redacted]").replace(account, "[account]")[:500]
        raise PreflightError(f"Cloudflare domain preview failed (HTTP {error.code}). {message}") from None
    except (URLError, ValueError):
        raise PreflightError("Cloudflare domain preview could not be read; deployment stopped.") from None
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise PreflightError("Cloudflare did not accept the domain preview; deployment stopped.")
    check_changeset(payload.get("result"))
    print(f"Domain preview approved for {HOSTNAME}; no existing DNS or domains will be replaced.")


if __name__ == "__main__":
    try:
        main()
    except PreflightError as error:
        print(f"Domain preflight: {error}", file=sys.stderr)
        sys.exit(1)
