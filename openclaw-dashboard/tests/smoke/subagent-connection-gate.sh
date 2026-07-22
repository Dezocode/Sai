#!/usr/bin/env bash
# subagent-connection-gate.sh — TG inbox + Slack intro + Habbo presence
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
REG="$ROOT/docs/agent-telegram-registry.md"
PROTO="$ROOT/docs/subagent-onboarding-protocol.md"
FAIL=0
[ -f "$PROTO" ] || { echo "FAIL missing subagent-onboarding-protocol.md"; exit 1; }
[ -f "$REG" ] || { echo "FAIL missing agent-telegram-registry.md"; exit 1; }
# Stub: when registry populated, verify each agent_id has telegram_dm_link + slack_intro + habbo_presence
echo "subagent-connection-gate.sh: STUB"
echo "  Required per docs/subagent-onboarding-protocol.md:"
echo "    1. Telegram inbox verified"
echo "    2. Slack intro with DM link posted"
echo "    3. Habbo avatar OR blocked with ticket"
grep -q 'telegram_dm_link' "$REG" || { echo "FAIL registry missing telegram_dm_link column"; FAIL=1; }
exit $FAIL
