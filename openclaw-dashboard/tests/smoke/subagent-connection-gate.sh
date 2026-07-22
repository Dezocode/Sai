#!/usr/bin/env bash
# subagent-connection-gate.sh — three-connection gate smoke (A6 + A10)
# Delegates to verify-agent-telegram.sh — fail closed per Saul CTO P1.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
exec "$ROOT/scripts/verify-agent-telegram.sh" --scope contract
