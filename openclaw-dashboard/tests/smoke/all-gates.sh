#!/usr/bin/env bash
# all-gates.sh — Alfred organization onboarding smoke orchestrator
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT/.."
FAIL=0
run() {
  echo "== $1 =="
  if "$@"; then echo "PASS $1"; else echo "FAIL $1"; FAIL=1; fi
}
run scripts/verify-semantic-hierarchy
run scripts/verify-agent-setup
run openclaw-dashboard/tests/smoke/design-tokens.sh
run openclaw-dashboard/tests/smoke/design-compliance.sh
run openclaw-dashboard/scripts/verify-ingest-latency.sh || true
run openclaw-dashboard/tests/smoke/telegram-mcq.sh || true
run openclaw-dashboard/tests/smoke/subagent-connection-gate.sh || true
run openclaw-dashboard/tests/smoke/run-all.sh || true
exit $FAIL
