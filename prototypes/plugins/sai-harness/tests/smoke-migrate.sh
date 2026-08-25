#!/usr/bin/env bash
set -euo pipefail
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/src/inbox"; echo '{}' > "$T/src/channels.json"; echo 'x' > "$T/src/audit.jsonl"; echo 'w' > "$T/src/wake.log"
"$1" --src "$T/src" --dest "$T/dst" --dry-run | grep -q "no changes made"
[ ! -d "$T/dst/channels.json" ] && [ ! -f "$T/dst/channels.json" ] && echo "PASS: dry-run makes no changes"
"$1" --src "$T/src" --dest "$T/dst" --commit | grep -q "commit complete"
[ -f "$T/dst/channels.json" ] && [ -f "$T/dst/audit.jsonl" ] && [ -f "$T/dst/wake.log" ] && [ -d "$T/dst/inbox" ] && echo "PASS: commit copies state"
"$1" --src "$T/src" --dest "$T/dst" --rollback | grep -q "rollback complete"
echo "PASS: rollback restores"
