#!/usr/bin/env bash
# subagent-connection-gate.sh — three-connection gate smoke (A6 + A10)
# Fail-closed: no stub PASS. Saul CTO review 4751481118.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)

# Negative regression must pass before enforcement (validators reject placeholders)
"$ROOT/scripts/verify-agent-telegram.sh" --self-test

# Fail closed per agent until real evidence or BLOCKED remediation
exec "$ROOT/scripts/verify-agent-telegram.sh" --scope contract
