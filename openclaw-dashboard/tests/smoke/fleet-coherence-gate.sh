#!/usr/bin/env bash
# fleet-coherence-gate.sh — prove fleet follows ICM + Telegram + Slack protocols
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
REPO=$(cd "$ROOT/.." && pwd)
FAIL=0

check() { if "$@"; then echo "PASS $1"; else echo "FAIL $1"; FAIL=1; fi }

# Alfred template must exist
[ -f "$REPO/.ai/agents/alfred/runtimes/openclaw/telegram/BEHAVIORS.md" ] || { echo "FAIL missing Alfred BEHAVIORS.md"; FAIL=1; }
[ -f "$REPO/.ai/agents/alfred/runtimes/openclaw/telegram/session-memory.md" ] || { echo "FAIL missing session-memory.md"; FAIL=1; }
[ -f "$ROOT/docs/telegram-session-protocol.md" ] || { echo "FAIL missing telegram-session-protocol.md"; FAIL=1; }
[ -f "$REPO/.ai/agents/alfred/runtimes/openclaw/telegram/BLOCKED-MCQ-CONTINUATION.md" ] || { echo "FAIL missing BLOCKED-MCQ-CONTINUATION.md"; FAIL=1; }
[ -f "$ROOT/integrations/telegram/mcq-actions.md" ] || { echo "FAIL missing mcq-actions.md"; FAIL=1; }
[ -f "$ROOT/docs/fleet-coherence-gate.md" ] || { echo "FAIL missing fleet-coherence-gate.md"; FAIL=1; }

CONTRACT="$REPO/.ai/contracts/20260722-openclaw-dashboard-dezocode/contract.json"
python3 - <<'PY' "$CONTRACT"
import json, sys
c = json.load(open(sys.argv[1]))
if "contract_sender" not in c:
    raise SystemExit("FAIL contract.json missing contract_sender")
if not c.get("contract_sender", {}).get("telegram_reporting"):
    raise SystemExit("FAIL contract_sender.telegram_reporting not mandatory")
if "telegram_session" not in c:
    raise SystemExit("FAIL contract.json missing telegram_session")
p = c.get("blocked_mcq_policy", {})
if not p.get("mandatory") or not p.get("continuation_checkpoint_required"):
    raise SystemExit("FAIL contract.json blocked_mcq_policy incomplete")
print("PASS contract telegram_session + blocked_mcq_policy fields")
PY

# Fleet roster: Alfred + every .openclaw/agents/*.md subagent (dashboard-created)
REG="$ROOT/docs/agent-telegram-registry.md"
FLEET=(ctr-code-alfred1)
if [ -d "$ROOT/.openclaw/agents" ]; then
  for f in "$ROOT/.openclaw/agents"/*.md; do
    [ -f "$f" ] || continue
    aid=$(basename "$f" .md)
    FLEET+=("$aid")
  done
fi

for aid in "${FLEET[@]}"; do
  if ! grep -q "| $aid |" "$REG" 2>/dev/null && ! grep -q "|$aid|" "$REG" 2>/dev/null; then
    if ! grep -q "$aid" "$REG"; then
      echo "FAIL fleet agent $aid missing from agent-telegram-registry.md"
      FAIL=1
    fi
  fi
done

# Alfred hooks must reference fleet gate
HOOKS="$REPO/.ai/agents/alfred/hooks.json"
python3 - <<'PY' "$HOOKS"
import json, sys
h = json.load(open(sys.argv[1]))
gates = h.get("smoke_gates", {})
for k in ("fleet_coherence", "telegram_session_reporting"):
    if k not in gates:
        raise SystemExit(f"FAIL hooks.json smoke_gates missing {k}")
print("PASS hooks.json fleet smoke gates registered")
PY

# Fulfillment evidence file optional at scaffold — stub documents requirement
EVIDENCE="$ROOT/docs/fulfillment-evidence.md"
grep -q 'fleet-coherence' "$EVIDENCE" || { echo "FAIL fulfillment-evidence.md missing fleet-coherence"; FAIL=1; }

if [ "$FAIL" -ne 0 ]; then
  echo "fleet-coherence-gate.sh: FAIL — see docs/fleet-coherence-gate.md"
  exit 1
fi
echo "fleet-coherence-gate.sh: OK (scaffold — live proof run required for fulfillment)"
exit 0
