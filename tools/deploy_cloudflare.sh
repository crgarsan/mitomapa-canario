#!/usr/bin/env bash
set -euo pipefail

# Do not let Wrangler fall back to interactive login or a different account
# when the protected production environment has not been configured.
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" || -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
  echo 'Missing Cloudflare production environment secrets; deployment refused.' >&2
  exit 1
fi

exec ./node_modules/.bin/wrangler deploy --config wrangler.jsonc
