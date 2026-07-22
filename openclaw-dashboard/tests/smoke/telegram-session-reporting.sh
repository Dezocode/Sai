#!/usr/bin/env bash
# telegram-session-reporting.sh — contract sender Telegram reporting gate
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
REPO=$(cd "$ROOT/.." && pwd)
CONTRACT="$REPO/.ai/contracts/20260722-openclaw-dashboard-dezocode/contract.json"

python3 - <<'PY' "$CONTRACT" "$ROOT" "$REPO"
import json, os, sys
contract_path, root, repo = sys.argv[1], sys.argv[2], sys.argv[3]
c = json.load(open(contract_path))
cs = c.get("contract_sender", {})
if cs.get("slack_id") != "U0BHYH0NMCY":
    raise SystemExit("FAIL contract_sender.slack_id must be U0BHYH0NMCY (dezocode)")
if cs.get("telegram_reporting") != "mandatory_per_session_run":
    raise SystemExit("FAIL contract_sender.telegram_reporting must be mandatory_per_session_run")

behaviors = repo + "/.ai/agents/alfred/runtimes/openclaw/telegram/BEHAVIORS.md"
if not os.path.isfile(behaviors):
    raise SystemExit("FAIL Alfred BEHAVIORS.md missing")
text = open(behaviors).read()
for needle in ("INTAKE", "HANDOFF", "contract sender", "session_state.json"):
    if needle.lower() not in text.lower():
        raise SystemExit(f"FAIL BEHAVIORS.md missing {needle}")

proto = root + "/docs/telegram-session-protocol.md"
if not os.path.isfile(proto):
    raise SystemExit("FAIL telegram-session-protocol.md missing")

# Fulfillment: require sample run artifact
proof_glob = repo + "/.ai/runs/*fleet-coherence-proof*/telegram-session.jsonl"
import glob
proofs = glob.glob(proof_glob)
if proofs:
    print(f"PASS found proof artifact: {proofs[0]}")
else:
    print("STUB telegram-session-reporting: no proof run yet — mandatory before fulfillment")
    print("  Required: .ai/runs/<task-id>/telegram-session.jsonl with INTAKE+HANDOFF events")
    sys.exit(2)
print("telegram-session-reporting.sh: PASS")
PY
