#!/usr/bin/env bash
# verify-agent-telegram.sh — fail-closed three-connection gate (A10)
#
# Usage:
#   verify-agent-telegram.sh [--scope contract|registry|table]
#
# Scopes:
#   contract  — Alfred + contract subagents (default for fulfillment)
#   registry  — every agent in .ai/agents/registry.json (strict A10)
#   table     — only rows present in agent-telegram-registry.md
#
# Exit 0 only when every in-scope agent has evidenced gates or BLOCKED record.
# Exit 1 on any missing/invalid evidence (fail closed — Saul P1).
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$ROOT/.." && pwd)
REG="$ROOT/docs/agent-telegram-registry.md"
PROTO="$ROOT/docs/subagent-onboarding-protocol.md"
BLOCKED="$ROOT/docs/blocked-agents.md"
REGISTRY="$REPO/.ai/agents/registry.json"
SCOPE="${1:-contract}"
if [ "${1:-}" = "--scope" ]; then SCOPE="${2:-contract}"; fi

[ -f "$PROTO" ] || { echo "FAIL missing $PROTO"; exit 1; }
[ -f "$REG" ] || { echo "FAIL missing $REG"; exit 1; }
[ -f "$REGISTRY" ] || { echo "FAIL missing $REGISTRY"; exit 1; }

export ROOT REPO REG BLOCKED REGISTRY SCOPE
python3 <<'PY'
import json, os, re, sys

REG = os.environ["REG"]
BLOCKED = os.environ["BLOCKED"]
REGISTRY = os.environ["REGISTRY"]
SCOPE = os.environ["SCOPE"]

INVALID = {"", "—", "-", "pending", "n/a", "na", "none", "null"}

def load_blocked():
    blocked = set()
    if not os.path.isfile(BLOCKED):
        return blocked
    for line in open(BLOCKED):
        line = line.strip()
        if line.startswith("|") and "agent_id" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if cols and cols[0]:
                blocked.add(cols[0])
    return blocked

def parse_registry_table(path):
    rows = {}
    headers = []
    for line in open(path):
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if not cols:
            continue
        if "agent_id" in cols[0]:
            headers = cols
            continue
        if "---" in line or not headers:
            continue
        if len(cols) < len(headers):
            cols += [""] * (len(headers) - len(cols))
        row = dict(zip(headers, cols))
        aid = row.get("agent_id", "")
        if aid:
            rows[aid] = row
    return rows

def valid_link(val):
    v = (val or "").strip().lower()
    if v in INVALID:
        return False
    return v.startswith("http") or v.startswith("https") or v.startswith("@") or v.startswith("t.me/")

def valid_slack(val):
    v = (val or "").strip().lower()
    if v in INVALID:
        return False
    return "slack.com" in v or v.startswith("http")

def scope_agent_ids(registry_data):
    agents = registry_data.get("agents", [])
    if SCOPE == "registry":
        return [a["agent_id"] for a in agents if a.get("status") in ("active", "provisional")]
    if SCOPE == "table":
        return list(parse_registry_table(REG).keys())
    # contract scope: Alfred + OpenClaw subagents in dashboard registry table
    required = {"ctr-code-alfred1", "config-expert", "research-coordinator"}
    for a in agents:
        if a.get("agent_id") == "ctr-code-alfred1":
            required.add(a["agent_id"])
    return sorted(required)

blocked_ids = load_blocked()
table = parse_registry_table(REG)
try:
    registry_data = json.load(open(REGISTRY))
except json.JSONDecodeError as e:
    print(f"FAIL invalid registry.json: {e}")
    sys.exit(1)

agent_ids = scope_agent_ids(registry_data)
errors = []

for aid in agent_ids:
    row = table.get(aid)
    if not row:
        errors.append(f"{aid}: missing row in agent-telegram-registry.md")
        continue

    tg = row.get("telegram_dm_link", "")
    slack = row.get("slack_intro_permalink", "")
    habbo = row.get("habbo_presence", "")
    connected = row.get("connected", "no").strip().lower()

    is_blocked = aid in blocked_ids or habbo.strip().lower() == "blocked"

    if not is_blocked:
        if not valid_link(tg):
            errors.append(f"{aid}: telegram_dm_link invalid or pending ({tg!r})")
        if not valid_slack(slack):
            errors.append(f"{aid}: slack_intro_permalink missing ({slack!r})")
        if habbo.strip().lower() in INVALID:
            errors.append(f"{aid}: habbo_presence not connected/blocked ({habbo!r})")
    else:
        if aid not in blocked_ids:
            errors.append(f"{aid}: habbo_presence=blocked but no row in docs/blocked-agents.md")

    if connected == "yes":
        if not (valid_link(tg) and valid_slack(slack) and (habbo.strip().lower() == "connected" or is_blocked)):
            errors.append(f"{aid}: connected=yes without full three-connection evidence")

if errors:
    print("verify-agent-telegram.sh: FAIL (fail-closed)")
    print(f"  scope={SCOPE} agents_checked={len(agent_ids)}")
    for e in errors:
        print(f"  - {e}")
    print("  Remediation: docs/subagent-onboarding-protocol.md")
    print("  BLOCKED path: docs/blocked-agents.md")
    sys.exit(1)

print(f"verify-agent-telegram.sh: PASS scope={SCOPE} agents={len(agent_ids)}")
PY
