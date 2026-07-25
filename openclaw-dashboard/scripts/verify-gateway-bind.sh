#!/usr/bin/env bash
# verify-gateway-bind.sh — Saul P1: Gateway must bind loopback by default
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../.." && pwd)
OPTS="$REPO/.ai/agents/alfred/runtimes/openclaw/gateway/config/gateway-options.json"
POLICY="$REPO/.ai/agents/alfred/runtimes/openclaw/gateway/config/gateway-exposure-policy.md"

[ -f "$OPTS" ] || { echo "FAIL missing gateway-options.json"; exit 1; }
[ -f "$POLICY" ] || { echo "FAIL missing gateway-exposure-policy.md"; exit 1; }

python3 - <<'PY' "$OPTS"
import json, sys
p = sys.argv[1]
g = json.load(open(p))
host = g.get("gateway", {}).get("host", "")
bind_policy = g.get("gateway", {}).get("bind_policy", "")
ingest_bind = g.get("dashboard_ingest", {}).get("bind", "")
forbidden = g.get("gateway", {}).get("remote_access", {}).get("forbidden_without_documentation", [])

if host in ("0.0.0.0", "::", ""):
    raise SystemExit(f"FAIL gateway.host must be loopback, got {host!r}")
if host != "127.0.0.1":
    raise SystemExit(f"FAIL gateway.host must be 127.0.0.1, got {host!r}")
if bind_policy != "loopback_default":
    raise SystemExit(f"FAIL gateway.bind_policy must be loopback_default, got {bind_policy!r}")
if ingest_bind != "127.0.0.1":
    raise SystemExit(f"FAIL dashboard_ingest.bind must be 127.0.0.1, got {ingest_bind!r}")
if "0.0.0.0" not in forbidden:
    raise SystemExit("FAIL remote_access.forbidden_without_documentation must list 0.0.0.0")
print("verify-gateway-bind.sh: OK (127.0.0.1 loopback default)")
PY

# Negative: reject scaffold that reintroduces 0.0.0.0
if grep -q '"host"[[:space:]]*:[[:space:]]*"0\.0\.0\.0"' "$OPTS"; then
  echo "FAIL gateway-options.json contains 0.0.0.0 host"
  exit 1
fi

exit 0
