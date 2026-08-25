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
# Fleet-shared credentials (never committed): /root/.sai-fleet/tokens.env, chmod 600.
[ -f /root/.sai-fleet/tokens.env ] && { set -a; . /root/.sai-fleet/tokens.env; set +a; }
[ -f "$PLUGIN_DIR/.gitignore" ] || fail "run from plugin checkout"

cmd_name() {  # resolve this runtime's agent name: owner-marked > env > generated fingerprint.
  if [ -s "$STATE/agent-name" ]; then cat "$STATE/agent-name"; return; fi
  local n="${SAI_AGENT_NAME:-}"
  # gh login is an ACCOUNT, not an agent identity — never consulted for naming.
  case "$n" in *[!A-Za-z0-9_-]*|"") n="sai-grunt-$(printf '%s|%s|%s' "$(hostname)" "$PWD" "$$" | sha256sum | cut -c1-6)" ;; esac  # bot-id charset: any clean alias wins (H8 contract); only hostile/empty values regenerate
  # bot-id charset rule (bench/openbot agent-computer/src/bot-id.ts): plain id only —
  # letters, digits, hyphen, underscore; no dots. Normalize rather than emit an unusable id.
  n=$(printf '%s' "$n" | tr '.' '-')
  printf '%s\n' "$n" > "$STATE/agent-name"; printf '%s\n' "$n"
}

AGENT=$(cat "$STATE/agent-name" 2>/dev/null || true)
[ -n "$AGENT" ] || AGENT=$(cmd_name)
GATEWAY="$HARNESS_DIR/hooks/audit-gateway.sh"   # single gateway path; cwd-independent (derived from $0)
export AGENT PR_NUMBER REPO_SLUG STATE INTERVAL HARNESS_DIR PLUGIN_DIR GATEWAY

cmd_flightboard() {  # local attribution: name : org-role : pr-assignment (API relays to repo side).
  # The write is gated: re-enter through the gateway as decision `flightboard-attrib`
  # (decide -> record -> act). SAI_FLIGHTBOARD_GATED marks the inner, already-gated run.
  if [ "${SAI_FLIGHTBOARD_GATED:-}" != "1" ]; then
    [ -x "$GATEWAY" ] || fail "audit-gateway missing at $GATEWAY — flightboard-attrib refuses to run ungated"
    env SAI_FLIGHTBOARD_GATED=1 "$GATEWAY" flightboard-attrib "$0" flightboard
    return $?
  fi
  python3 -c '
import json,sys,os,datetime
st=os.environ["STATE"]
fb={"agent":os.environ["AGENT"],"org_role":"prototype-lane automation (Sai Harness)",
    "pr_assignment":"Dezocode/Sai#"+sys.argv[1],"side":"local","tier":"prototype",
    "updated_at":datetime.datetime.now(datetime.UTC).isoformat()}
json.dump(fb,open(os.path.join(st,"flightboard.json"),"w"),indent=1)
print(json.dumps(fb))' "$PR_NUMBER" || true
}

wake_proof() {  # consistency goal: proof-of-wake to PR comments every wake, THROUGH the gateway.
  # No silent bypass: if the gateway is missing or non-executable, name it and skip.
  [ -x "$GATEWAY" ] || { printf '[grokbot] wake-proof skipped: gateway missing at %s\n' "$GATEWAY" >&2; return 1; }
  ci=$(gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" 2>/dev/null | grep -cE '(pass|fail|passing|failing)')
  "$GATEWAY" wake-proof gh pr comment "$PR_NUMBER" --repo "$REPO_SLUG" \
    --body "wake-proof [$AGENT] $(date -u +%Y-%m-%dT%H:%M:%SZ) · tick=$1 · ci=${ci}checks-observed · next-wake=${INTERVAL}s" \
    >/dev/null 2>&1 || printf '[grokbot] wake-proof refused or failed (see audit log)\n' >&2
}

continuation_prompt() {  # pick what this wake should launch
  command -v gh >/dev/null 2>&1 || { printf 'verify-sai'; return; }
  if gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" 2>/dev/null | grep -qE '\|\s*(fail|failing)'; then printf 'tdd'; else printf 'crosscomm'; fi
}

cmd_inbox() {  # OpenBot composer semantics: parked messages drain as ONE follow-up turn.
  shopt -s nullglob
  local combined="" n=0
  for m in "$STATE"/inbox/*.md; do
    [ "${SAI_INBOX_GATED:-}" = "1" ] || printf '[grokbot] parking parked request: %s\n' "$(basename "$m")"
    combined="${combined}${combined:+ ; }$(cat "$m")"; n=$((n+1))
  done
  [ "$n" -gt 0 ] || return 0
  # The drain is gated like every other side effect: one pass through the gateway
  # as decision `inbox-drain` before anything launches. Files are parked to .sent
  # only once the gateway allows the turn.
  if [ "${SAI_INBOX_GATED:-}" != "1" ]; then
    [ -x "$GATEWAY" ] || fail "audit-gateway missing at $GATEWAY — inbox-drain refuses to run ungated"
    env SAI_INBOX_GATED=1 SAI_INBOX_COMBINED="$combined" "$GATEWAY" inbox-drain "$0" inbox
    return $?
  fi
  # Park only once we can actually launch: parking before this check silently
  # ate messages while claiming they "stay parked".
  command -v atomic >/dev/null 2>&1 || { printf 'atomic CLI missing; %d request(s) stay parked\n' "$n" >&2; return 1; }
  for m in "$STATE"/inbox/*.md; do mv "$m" "$m.sent" 2>/dev/null || rm -f "$m"; done
  local donef="$STATE/launch.$$"
  ( cd "$PLUGIN_DIR/../../.." && atomic "$combined" >"$donef.log" 2>&1; printf '%s' $? > "$donef" ) &
  printf '%s' $! > "$STATE/launches/$$"   # record: file=launcher pid, content=worker pid
  printf '[grokbot] drained %d parked mention(s) as one tracked follow-up turn (pid %s)\n' "$n" "$!"
}

LAUNCH_TIMEOUT="${SAI_GROKBOT_LAUNCH_TIMEOUT:-900}"
self_heal() {  # stuck/errored atomic runtimes: kill stale, requeue with backoff, dead-letter at 3.
  local lf pid donef rc age sent att
  shopt -s nullglob
  for lf in "$STATE"/launches/*; do
    pid=$(cat "$lf"); donef="$STATE/launch.${lf##*/}"   # done file is keyed by the LAUNCHER pid
    sent=$(ls -t "$STATE"/inbox/*.sent 2>/dev/null | head -1)
    if kill -0 "$pid" 2>/dev/null; then
      age=$(( $(date +%s) - $(stat -c %Y "$lf" 2>/dev/null || echo $(date +%s)) ))
      if [ "$age" -gt "$LAUNCH_TIMEOUT" ]; then
        kill -9 "$pid" 2>/dev/null; printf 'self-heal: launch %s stuck %ss — killed, requeued\n' "$pid" "$age" >&2
        [ -n "$sent" ] && mv "$sent" "${sent%.sent}" 2>/dev/null
        rm -f "$lf"
      fi
      continue
    fi
    rc=$(cat "$donef" 2>/dev/null || printf '1')
    mkdir -p "$STATE/att"; attf="$STATE/att/${sent##*/}"; att=$(( $(cat "$attf" 2>/dev/null || echo 0) + 1 )); printf '%s' "$att" > "$attf"
    if [ "$rc" = "0" ]; then
      printf 'self-heal: launch %s completed ok\n' "$pid" >&2; rm -f "$attf"
    elif [ "$att" -ge 3 ]; then
      mkdir -p "$STATE/dead-letter"; [ -n "$sent" ] && mv "$sent" "$STATE/dead-letter/${sent##*/}"
      printf 'self-heal: launch %s failed rc=%s attempt=%s — DEAD-LETTERED\n' "$pid" "$rc" "$att" >&2
    else
      [ -n "$sent" ] && mv "$sent" "${sent%.sent}" 2>/dev/null
      backoff=$(( 2 ** (att-1) )); [ "$backoff" -gt 300 ] && backoff=300
      printf 'self-heal: launch %s failed rc=%s attempt=%s — requeued, backoff %ss\n' "$pid" "$rc" "$att" "$backoff" >&2
    fi
    rm -f "$lf" "$donef" "$donef.log"
  done
}

cmd_tick() {
  # Serialize concurrent ticks (hook stop + daemon can overlap): flock guards the
  # counter read-modify-write and keeps two wakes from double-posting wake-proof.
  if command -v flock >/dev/null 2>&1; then exec 9>"$STATE/ticks.lock"; flock 9; fi
  n=$(cat "$STATE/ticks" 2>/dev/null || echo 0); n=$((n+1)); printf '%s' "$n" > "$STATE/ticks"
  date +%s > "$STATE/daemon.heartbeat"
  self_heal
  cmd_name >/dev/null; cmd_inbox; cmd_flightboard >/dev/null
  wake_proof "$n"
  printf '[grokbot] wake %s @ %s — continuation skill: %s\n' "$n" "$(date -u +%H:%M:%SZ)" "$(continuation_prompt)"
  if command -v flock >/dev/null 2>&1; then flock -u 9; exec 9>&-; fi
  # Explicit success: a bare `[ -f STOP ] && exit 0` would leave exit status 1 on an
  # ordinary wake (no stop file), which hook runners read as a failed hook.
  if [ ! -f "$STATE/GROKBOT_STOP" ] && ! pgrep -f "grokbot.sh daemon" >/dev/null 2>&1; then
    hb=$(cat "$STATE/daemon.heartbeat" 2>/dev/null || echo 0)
    if [ $(( $(date +%s) - hb )) -gt $(( INTERVAL * 2 )) ]; then
      printf '[grokbot] SELF-HEAL: daemon dead + stale heartbeat — relaunching detached\n' >&2
      ( set -m; nohup bash "$0" daemon >> "$STATE/daemon.log" 2>&1 & )
    fi
  fi
  [ ! -f "$STATE/GROKBOT_STOP" ] || printf '[grokbot] stop-file seen; waking no more\n'
  exit 0
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
