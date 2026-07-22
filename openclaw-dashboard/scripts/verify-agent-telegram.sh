#!/usr/bin/env bash
# verify-agent-telegram.sh — fail-closed three-connection gate (A10)
#
# Usage:
#   verify-agent-telegram.sh [--scope contract|registry|table]
#   verify-agent-telegram.sh --self-test   # negative regression (Saul P1)
#
# Exit 0 only when every in-scope agent has evidenced gates or BLOCKED record.
# Exit 1 on any missing/invalid evidence (fail closed).
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$ROOT/.." && pwd)
REG="$ROOT/docs/agent-telegram-registry.md"
PROTO="$ROOT/docs/subagent-onboarding-protocol.md"
BLOCKED="$ROOT/docs/blocked-agents.md"
REGISTRY="$REPO/.ai/agents/registry.json"
SCOPE="contract"
MODE="verify"

while [ $# -gt 0 ]; do
  case "$1" in
    --scope) SCOPE="${2:-contract}"; shift 2;;
    --self-test) MODE="self-test"; shift;;
    -h|--help)
      echo "Usage: verify-agent-telegram.sh [--scope contract|registry|table] | --self-test"
      exit 0;;
    *) echo "verify-agent-telegram.sh: unknown option $1" >&2; exit 2;;
  esac
done

export ROOT REPO REG BLOCKED REGISTRY SCOPE MODE PROTO
python3 <<'PY'
import json, os, re, sys

REG = os.environ["REG"]
BLOCKED = os.environ["BLOCKED"]
REGISTRY = os.environ["REGISTRY"]
SCOPE = os.environ["SCOPE"]
MODE = os.environ["MODE"]
PROTO = os.environ["PROTO"]

INVALID = {"", "—", "-", "pending", "n/a", "na", "none", "null", "tbd", "todo"}

# Strict formats — bare @ and fake http strings MUST fail (Saul review 4751481118)
TELEGRAM_DM_RE = re.compile(
    r"^https://(t\.me|telegram\.me)/[A-Za-z0-9_+-]+(\?start=[A-Za-z0-9_+-]+)?/?$",
    re.I,
)
SLACK_INTRO_RE = re.compile(
    r"^https://[a-z0-9-]+\.slack\.com/archives/[A-Z0-9]+/p[0-9]+(?:\?thread_ts=[0-9.]+)?(?:&cid=[A-Z0-9]+)?$",
    re.I,
)

NEGATIVE_TELEGRAM = ["@", "pending", "http-not-a-url", "https://example.com/foo", "t.me/bot"]
NEGATIVE_SLACK = ["—", "http-not-a-url", "https://example.com", "https://slack.com/foo"]
NEGATIVE_PASS_POSITIVE = [
    ("https://t.me/alfred_bot?start=ctr-code-alfred1", True),
    ("https://telegram.me/alfred_bot", True),
    (
        "https://sai-qbz5908.slack.com/archives/C0BH15HDN2Z/p1721612345678909",
        True,
    ),
]


def run_self_test():
    errors = []
    for bad in NEGATIVE_TELEGRAM:
        if valid_telegram_dm(bad):
            errors.append(f"self-test: telegram must reject {bad!r}")
    for bad in NEGATIVE_SLACK:
        if valid_slack_intro(bad):
            errors.append(f"self-test: slack must reject {bad!r}")
    for good, expect in NEGATIVE_PASS_POSITIVE:
        fn = valid_telegram_dm if "t.me" in good or "telegram.me" in good else valid_slack_intro
        if fn(good) != expect:
            errors.append(f"self-test: expected {good!r} -> {expect}, got {fn(good)}")
    if valid_habbo_presence("pending"):
        errors.append("self-test: habbo must reject pending")
    if not valid_habbo_presence("connected"):
        errors.append("self-test: habbo must accept connected")
    if errors:
        print("verify-agent-telegram.sh --self-test: FAIL")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("verify-agent-telegram.sh --self-test: PASS (negative regression)")
    sys.exit(0)


def valid_telegram_dm(val):
    v = (val or "").strip()
    if v.lower() in INVALID:
        return False
    return bool(TELEGRAM_DM_RE.match(v))


def valid_slack_intro(val):
    v = (val or "").strip()
    if v.lower() in INVALID:
        return False
    return bool(SLACK_INTRO_RE.match(v))


def valid_habbo_presence(val):
    return (val or "").strip().lower() == "connected"


def load_blocked():
    blocked = set()
    if not os.path.isfile(BLOCKED):
        return blocked
    for line in open(BLOCKED):
        line = line.strip()
        if line.startswith("|") and "agent_id" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if cols and cols[0] and cols[0] != "_example_":
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


def scope_agent_ids(registry_data):
    agents = registry_data.get("agents", [])
    if SCOPE == "registry":
        return [a["agent_id"] for a in agents if a.get("status") in ("active", "provisional")]
    if SCOPE == "table":
        return list(parse_registry_table(REG).keys())
    return sorted({"ctr-code-alfred1", "config-expert", "research-coordinator"})


if MODE == "self-test":
    run_self_test()

if not os.path.isfile(PROTO):
    print(f"FAIL missing {PROTO}")
    sys.exit(1)
if not os.path.isfile(REG):
    print(f"FAIL missing {REG}")
    sys.exit(1)
if not os.path.isfile(REGISTRY):
    print(f"FAIL missing {REGISTRY}")
    sys.exit(1)

blocked_ids = load_blocked()
table = parse_registry_table(REG)
registry_data = json.load(open(REGISTRY))
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
        if not valid_telegram_dm(tg):
            errors.append(
                f"{aid}: telegram_dm_link invalid — require https://t.me/... or https://telegram.me/... ({tg!r})"
            )
        if not valid_slack_intro(slack):
            errors.append(
                f"{aid}: slack_intro_permalink invalid — require https://*.slack.com/archives/.../p... ({slack!r})"
            )
        if not valid_habbo_presence(habbo):
            errors.append(
                f"{aid}: habbo_presence must be 'connected' or documented BLOCKED ({habbo!r})"
            )
    else:
        if aid not in blocked_ids:
            errors.append(f"{aid}: habbo_presence=blocked but no row in docs/blocked-agents.md")

    if connected == "yes":
        if not (
            valid_telegram_dm(tg)
            and valid_slack_intro(slack)
            and (valid_habbo_presence(habbo) or is_blocked)
        ):
            errors.append(f"{aid}: connected=yes without valid three-connection evidence")

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
