#!/usr/bin/env bash
# T1: restart/resume — a killed runtime's ledgers survive respawn intact and
# no double-drain occurs (idempotent .sent parking). Fixture-based, no live bots.
set -euo pipefail
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
S="$(cd "$(dirname "$0")/.." && pwd)"

# fixture: state dir with inbox ledger + audit journal + a parked mention
mkdir -p "$T/state/inbox"
echo '{"task_id":"t1","seq":1}' > "$T/state/inbox/m1.md.sent"
echo '{"task_id":"t1","seq":2}' > "$T/state/inbox/m2.md"
echo '{"decision":"owner-steer","verdict":"allow"}' > "$T/state/audit.jsonl"
echo "42" > "$T/state/ticks"

# simulate crash: heartbeat stale (no process). Resume = migrate state forward.
"$S/state/migrate.sh" --src "$T/state" --dest "$T/resumed" --commit | grep -q "commit complete"
# ledger integrity: all files present, .sent marker preserved, unparked still unparked
[ -f "$T/resumed/inbox/m1.md.sent" ] && [ -f "$T/resumed/inbox/m2.md" ] || { echo "FAIL: ledger lost in resume"; exit 1; }
[ "$(cat "$T/resumed/ticks")" = "42" ] || { echo "FAIL: tick counter lost"; exit 1; }
grep -q "owner-steer" "$T/resumed/audit.jsonl" || { echo "FAIL: audit journal lost"; exit 1; }
# no double-drain: re-running commit is idempotent (copies same content, .sent stays .sent)
"$S/state/migrate.sh" --src "$T/state" --dest "$T/resumed" --commit >/dev/null
[ "$(ls "$T/resumed/inbox" | wc -l)" = "2" ] || { echo "FAIL: duplicate drain artifacts"; exit 1; }
echo "T1 PASS: ledgers survive restart/resume; no duplicates; audit journal intact"
