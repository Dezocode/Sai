#!/usr/bin/env bash
# audit-gateway.sh — OpenBot-derived gateway: decide -> record -> act, every time.
# A wake decision is written to the audit log BEFORE the action runs, and the
# outcome is appended after. Refusals are named, never silent.
set -eu
STATE="$(cd "$(dirname "$0")/../state" && pwd)"; mkdir -p "$STATE"
decision="$1"; shift

decide() {  # policy: prototype tier refuses nothing silently; each rule names itself
  case "$decision" in
    wake-proof|inbox-drain|flightboard-attrib|debugger-launch|channel-probe) printf 'allow' ;;  # debugger-launch: §10(2); channel-probe: tmux liveness reporting (spec 2026-08-25)
    *) printf 'refuse:unknown-decision' ;;
  esac
}
verdict=$(decide)
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '{"ts":"%s","decision":"%s","verdict":"%s"}\n' "$ts" "$decision" "$verdict" >> "$STATE/audit.jsonl"
[ "$verdict" = "allow" ] || { printf 'gateway refused %s (%s)\n' "$decision" "$verdict" >&2; exit 1; }
# set -e aborts on the action's failure before the outcome is ever recorded,
# leaving decide+act in the log with no outcome line. Capture the rc instead.
rc=0
"$@" || rc=$?
printf '{"ts":"%s","decision":"%s","outcome":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$decision" "$([ "$rc" -eq 0 ] && echo ok || echo error)" >> "$STATE/audit.jsonl"
exit "$rc"
