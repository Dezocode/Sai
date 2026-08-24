#!/usr/bin/env bash
# grokbot.sh — Sai Harness automation fleet brain (prototype tier).
# Subcommands: name | inbox | flightboard | tick | hook | daemon
# Contract: wake every SAI_GROKBOT_INTERVAL seconds (default 600) after turn end,
# mirror of Cursor's stop+loop_limit semantics defined in production .cursor/hooks.json.
set -u
HARNESS_DIR="$(cd "$(dirname "$0")/.." && pwd)"          # .sai
PLUGIN_DIR="$(dirname "$HARNESS_DIR")"
STATE="$HARNESS_DIR/state"; mkdir -p "$STATE/inbox" "$STATE"
PR_NUMBER="${SAI_GROKBOT_PR:-146}"
REPO_SLUG="${CROSSCOM_REPO:-Dezocode/Sai}"
INTERVAL="${SAI_GROKBOT_INTERVAL:-600}"

fail() { printf 'grokbot: %s\n' "$1" >&2; exit 1; }
[ -f "$PLUGIN_DIR/.gitignore" ] || fail "run from plugin checkout"

cmd_name() {  # resolve this runtime's agent name: owner-marked > env > generated fingerprint.
  if [ -s "$STATE/agent-name" ]; then cat "$STATE/agent-name"; return; fi
  local n="${SAI_AGENT_NAME:-}"
  if [ -z "$n" ] && command -v gh >/dev/null 2>&1; then n=$(gh api user --jq .login 2>/dev/null | sed 's/^sai\.grunt-.*/&/'); fi
  # gh login is an ACCOUNT, not an agent identity: only accept it when explicitly aliased.
  case "$n" in sai.*|her) : ;; *) n="sai.grunt-$(printf '%s|%s|%s' "$(hostname)" "$PWD" "$$" | sha256sum | cut -c1-6)" ;; esac
  printf '%s\n' "$n" > "$STATE/agent-name"; printf '%s\n' "$n"
}

AGENT=$(cat "$STATE/agent-name" 2>/dev/null || true)
[ -n "$AGENT" ] || AGENT=$(cmd_name)
export AGENT PR_NUMBER REPO_SLUG STATE INTERVAL HARNESS_DIR PLUGIN_DIR

cmd_flightboard() {  # local attribution: name : org-role : pr-assignment (API relays to repo side)
  python3 -c '
import json,sys,os,datetime
st=os.environ["STATE"]
fb={"agent":os.environ["AGENT"],"org_role":"prototype-lane automation (Sai Harness)",
    "pr_assignment":"Dezocode/Sai#"+sys.argv[1],"side":"local","tier":"prototype",
    "updated_at":datetime.datetime.now(datetime.UTC).isoformat()}
json.dump(fb,open(os.path.join(st,"flightboard.json"),"w"),indent=1)
print(json.dumps(fb))' "$PR_NUMBER" 2>/dev/null || true
}

wake_proof() {  # consistency goal: ping proof-of-wake to the PR comments every wake
  command -v gh >/dev/null 2>&1 || return 0
  gh pr comment "$PR_NUMBER" --repo "$REPO_SLUG" --body "wake-proof [$AGENT] $(date -u +%Y-%m-%dT%H:%M:%SZ) · tick=$1 · ci=$(gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" 2>/dev/null | grep -cE '(pass|fail|passing|failing)' )checks-observed · next-wake=${INTERVAL}s" >/dev/null 2>&1 || true
}

continuation_prompt() {  # pick what this wake should launch
  command -v gh >/dev/null 2>&1 || { printf 'verify-sai'; return; }
  if gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" 2>/dev/null | grep -qE '\|\s*(fail|failing)'; then printf 'tdd'; else printf 'crosscomm'; fi
}

cmd_inbox() {  # scan drops; launch each mention as a user request via atomic CLI
  shopt -s nullglob
  for m in "$STATE"/inbox/*.md; do
    printf '[grokbot] launching queued request: %s\n' "$(basename "$m")"
    if command -v atomic >/dev/null 2>&1; then (cd "$PLUGIN_DIR/../../.." && nohup atomic "$(cat "$m")" >/tmp/grokbot-launch.$$ 2>&1 &) ; else printf 'atomic CLI missing; request stays queued\n' >&2; continue; fi
    mv "$m" "$m.sent" 2>/dev/null || rm -f "$m"
  done
}

cmd_tick() {
  n=$(cat "$STATE/ticks" 2>/dev/null || echo 0); n=$((n+1)); printf '%s' "$n" > "$STATE/ticks"
  cmd_name >/dev/null; cmd_inbox; cmd_flightboard >/dev/null
  wake_proof "$n"
  printf '[grokbot] wake %s @ %s — continuation skill: %s\n' "$n" "$(date -u +%H:%M:%SZ)" "$(continuation_prompt)"
  [ -f "$STATE/GROKBOT_STOP" ] && exit 0
}

cmd_hook() {  # structural parity with production .cursor wiring (19 events); no side effects
  printf '{"continue":true}\n'; exit 0
}

cmd_daemon() {
  printf '[grokbot] daemon started: interval=%ss stop-file=%s\n' "$INTERVAL" "$STATE/GROKBOT_STOP"
  while [ ! -f "$STATE/GROKBOT_STOP" ]; do cmd_tick; sleep "$INTERVAL"; done
  printf '[grokbot] stop-file seen; exiting\n'
}

case "${1:-tick}" in
  name) cmd_name ;;
  inbox) cmd_inbox ;;
  flightboard) cmd_flightboard ;;
  tick) cmd_tick ;;
  hook) cmd_hook ;;
  daemon) cmd_daemon ;;
  *) fail "usage: grokbot.sh [name|inbox|flightboard|tick|hook|daemon]" ;;
esac
