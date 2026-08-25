#!/usr/bin/env bash
# grokbot.sh — Sai Harness automation fleet brain (prototype tier).
# Subcommands: name | inbox | flightboard | tick | hook | daemon | spawn
# Contract: wake every SAI_GROKBOT_INTERVAL seconds (default 600) after turn end,
# mirror of Cursor's stop+loop_limit semantics defined in production .cursor/hooks.json.
set -u
HARNESS_DIR="$(cd "$(dirname "$0")/.." && pwd)"          # .sai
PLUGIN_DIR="$(dirname "$HARNESS_DIR")"
STATE="$HARNESS_DIR/state"
PAYLOADS="$STATE/payloads"; REQUEUE="$STATE/requeue"
LAUNCHES="$STATE/launches"; DEAD_LETTER="$STATE/dead-letter"
HEARTBEAT="$STATE/daemon.heartbeat"
mkdir -p "$STATE/inbox" "$PAYLOADS" "$REQUEUE" "$LAUNCHES" "$DEAD_LETTER"
PR_NUMBER="${SAI_GROKBOT_PR:-146}"
REPO_SLUG="${CROSSCOM_REPO:-Dezocode/Sai}"
INTERVAL="${SAI_GROKBOT_INTERVAL:-600}"
# Self-heal knobs (lane lineage ef235dd parity): stuck launches are killed past
# LAUNCH_TIMEOUT, errored requests are requeued with exponential backoff and
# dead-lettered at MAX_ATTEMPTS, and a dead daemon is respawned from its stale
# heartbeat — nobody types "continue" to resurrect the loop.
LAUNCH_TIMEOUT="${SAI_GROKBOT_LAUNCH_TIMEOUT:-900}"
MAX_ATTEMPTS="${SAI_GROKBOT_MAX_ATTEMPTS:-3}"
# Owner-provisioned credentials (0600, dir 0700): sourced once at startup so
# SESSIONS_VERIFIER_TOKEN / SESSIONS_API_URL / CROSSCOM_REPO reach the whole hook
# chain (lane-connector write path, reconcile probes). Values stay in process env —
# never echoed, never logged, never embedded in PR comments or state files.
TOKENS_ENV="${SAI_TOKENS_ENV:-/root/.sai-fleet/tokens.env}"
if [ -r "$TOKENS_ENV" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$TOKENS_ENV"
  set +a
fi
 [ -r "$HARNESS_DIR/hooks/sai-channel.sh" ] && . "$HARNESS_DIR/hooks/sai-channel.sh"   # channel-per-agent doors (spec 2026-08-25)

fail() { printf 'grokbot: %s\n' "$1" >&2; exit 1; }
[ -f "$PLUGIN_DIR/.gitignore" ] || fail "run from plugin checkout"

cmd_name() {  # resolve this runtime's agent name: owner-marked > env > generated fingerprint.
  if [ -s "$STATE/agent-name" ]; then cat "$STATE/agent-name"; return; fi
  local n="${SAI_AGENT_NAME:-}"
  if [ -z "$n" ] && command -v gh >/dev/null 2>&1; then n=$(gh api user --jq .login 2>/dev/null || true); fi
  # gh login is an ACCOUNT, not an agent identity: only accept it when explicitly aliased.
  case "$n" in sai-*|her) : ;; *) n="sai-grunt-$(printf '%s|%s|%s' "$(hostname)" "$PWD" "$$" | sha256sum | cut -c1-6)" ;; esac
  # bot-id charset rule (bench/openbot agent-computer/src/bot-id.ts): plain id only —
  # letters, digits, hyphen, underscore; no dots. Normalize rather than emit an unusable id.
  n=$(printf '%s' "$n" | tr '.' '-')
  printf '%s\n' "$n" > "$STATE/agent-name"; printf '%s\n' "$n"
}

AGENT=$(cat "$STATE/agent-name" 2>/dev/null || true)
[ -n "$AGENT" ] || AGENT=$(cmd_name)
GATEWAY="$HARNESS_DIR/hooks/audit-gateway.sh"   # single gateway path; cwd-independent (derived from $0)
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"   # absolute self path for respawn/spawn re-entry
export AGENT PR_NUMBER REPO_SLUG STATE INTERVAL HARNESS_DIR PLUGIN_DIR GATEWAY SELF \
  PAYLOADS REQUEUE LAUNCHES DEAD_LETTER HEARTBEAT LAUNCH_TIMEOUT MAX_ATTEMPTS

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

# ---- Self-heal (lane lineage ef235dd parity) --------------------------------
track_launch() {  # track_launch <pid> <kind> <attempts> <payload-path>
  printf 'L_PID=%s\nL_KIND=%s\nL_ATTEMPTS=%s\nL_STARTED=%s\nL_PAYLOAD=%s\n' \
    "$1" "$2" "$3" "$(date +%s)" "$4" > "$LAUNCHES/launch.$1"
}

spawn_tracked() {  # spawn_tracked <kind> <attempts> <prompt-text>: persist payload,
  # launch an atomic runtime tracked for self-heal (stuck-kill / requeue / dead-letter).
  command -v atomic >/dev/null 2>&1 || { printf 'grokbot: atomic CLI missing; request kept\n' >&2; return 1; }
  local kind="$1" att="$2" pf log pid
  pf="$PAYLOADS/$kind.$(date +%s%N).a$att.md"
  printf '%s' "$3" > "$pf"
  log="/tmp/grokbot-$kind.$$.log"
  nohup bash -c 'cd "$1" && atomic "$(cat "$2")"; echo $? >"$2.exit"' \
    _ "$PLUGIN_DIR/../../.." "$pf" >"$log" 2>&1 &
  pid=$!
  track_launch "$pid" "$kind" "$att" "$pf"
  printf '[grokbot] tracked launch pid=%s kind=%s attempt=%s payload=%s\n' "$pid" "$kind" "$att" "$pf"
}

requeue_or_deadletter() {  # $1 kind, $2 attempts, $3 payload path:
  # backoff-gated requeue; dead-letter once attempts are exhausted.
  local att=$(( ${2:-0} + 1 )) dst
  if [ "$att" -ge "$MAX_ATTEMPTS" ]; then
    dst="$DEAD_LETTER/$(basename "$3")"
    mv "$3" "$dst" 2>/dev/null
    printf '[grokbot] dead-letter after %s attempt(s): %s\n' "$att" "$dst"
  else
    dst="$REQUEUE/$(basename "$3").r$att"
    mv "$3" "$dst" 2>/dev/null
    printf '[grokbot] requeued attempt=%s (backoff-gated): %s\n' "$att" "$dst"
  fi
}

self_heal() {  # sweep tracked launches: kill stuck (>LAUNCH_TIMEOUT), requeue errored, clear ok.
  local f rc now
  now=$(date +%s)
  for f in "$LAUNCHES"/launch.*; do
    [ -f "$f" ] || continue
    L_PID=; L_KIND=; L_ATTEMPTS=0; L_STARTED=0; L_PAYLOAD=
    # shellcheck disable=SC1090
    . "$f"
    rc=""
    [ -f "$L_PAYLOAD.exit" ] && rc="$(cat "$L_PAYLOAD.exit")"
    if kill -0 "$L_PID" 2>/dev/null; then
      [ $((now - L_STARTED)) -le "$LAUNCH_TIMEOUT" ] && continue   # still within budget
      printf '[grokbot] stuck launch pid=%s (%ss > %ss): killing\n' "$L_PID" "$((now-L_STARTED))" "$LAUNCH_TIMEOUT"
      kill -TERM "$L_PID" 2>/dev/null; sleep 3; kill -KILL "$L_PID" 2>/dev/null
      requeue_or_deadletter "$L_KIND" "$L_ATTEMPTS" "$L_PAYLOAD"
    elif [ "$rc" = "0" ]; then
      printf '[grokbot] launch pid=%s finished ok\n' "$L_PID"
    else
      printf '[grokbot] launch pid=%s errored (rc=%s): requeueing\n' "$L_PID" "${rc:-none}"
      requeue_or_deadletter "$L_KIND" "$L_ATTEMPTS" "$L_PAYLOAD"
    fi
    rm -f "$f" "$L_PAYLOAD.exit"
  done
}

drain_requeue() {  # respawn requeued requests only after 2^(n-1) intervals of quiet.
  local f base att age wait_s
  for f in "$REQUEUE"/*.md; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"; att="${base##*.r}"; att="${att%.md}"
    case "$att" in ''|*[!0-9]*) att=1 ;; esac
    age=$(( $(date +%s) - "$(stat -c %Y "$f" 2>/dev/null || date +%s)" ))
    wait_s=$(( INTERVAL * (1 << ((att-1)>2 ? 2 : (att-1))) ))
    [ "$age" -ge "$wait_s" ] || continue
    local txt
    txt="$(cat "$f" 2>/dev/null)"   # read BEFORE unlink: a failed respawn must not eat the request
    rm -f "$f"
    if spawn_tracked requeue "$att" "$txt"; then :
    else printf '%s' "$txt" > "$REQUEUE/$base" 2>/dev/null; fi
  done
}

maybe_restart_daemon() {  # stale heartbeat + no live daemon -> relaunch detached (§10 self-heal).
  local dpid age=999999999 lock="$STATE/daemon.respawn.lock"
  dpid="$(head -c 32 "$HEARTBEAT" 2>/dev/null | cut -d' ' -f1)"
  kill -0 "$dpid" 2>/dev/null && return 0            # live daemon (its own ticks land here too)
  if [ -f "$HEARTBEAT" ]; then
    age=$(( $(date +%s) - "$(stat -c %Y "$HEARTBEAT" 2>/dev/null || date +%s)" ))
  fi
  [ "$age" -lt $(( INTERVAL * 2 )) ] && return 0     # fresh heartbeat: daemon mid-wake
  mkdir "$lock" 2>/dev/null || return 0              # another tick is already respawning
  nohup bash "$SELF" daemon >>"${SAI_GROKBOT_LOG:-$PLUGIN_DIR/../grokbot.log}" 2>&1 &
  printf '[grokbot] daemon respawned from stale heartbeat (new pid %s)\n' "$!"
  rmdir "$lock"
}
# -----------------------------------------------------------------------------

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
  # Channel-first delivery (spec specs/2026-08-25-sai-cli-layer-over-atomic.md §0):
  # mentions reach the bot's LIVE REPL as ONE submitted turn; .sent parks only on success.
  if command -v tmux >/dev/null 2>&1; then
    channel_alive "$AGENT" || launch_agent "$AGENT" || true    # auto-birth on drain (§0.2)
    if deliver_to_channel "$AGENT" "$combined"; then
      for m in "$STATE"/inbox/*.md; do mv "$m" "$m.sent" 2>/dev/null || rm -f "$m"; done
      printf '[grokbot] delivered %d mention(s) into %s as ONE turn\n' "$n" "$(channel_session "$AGENT")"
      return 0
    fi
    printf '[grokbot] channel delivery failed for %s; falling back to headless tracked launch\n' "$AGENT" >&2
  fi
  # Named fallback (CI-debugger parity): headless tracked launch, same exactly-once parking.
  command -v atomic >/dev/null 2>&1 || { printf 'atomic CLI missing; %d request(s) stay parked\n' "$n" >&2; return 1; }
  for m in "$STATE"/inbox/*.md; do mv "$m" "$m.sent" 2>/dev/null || rm -f "$m"; done
  spawn_tracked inbox 0 "$combined"
  printf '[grokbot] drained %d parked mention(s) as one follow-up turn\n' "$n"
}

turn_debug_chain() {  # contract §10(2): on turn end, a debugger subagent evaluates the LAST
  # turn against the targeted goals BEFORE wake automation runs. Cheap when clean (§10.4):
  # nothing broken turn-over-turn -> one log line, wake proceeds. Broken -> launch a debugger
  # worker (gateway decision `debugger-launch`, atomic CLI, never a self-loop) carrying the
  # exact last-turn output, goal refs, and authority to edit + re-run gates (skill §9).
  local n="$1"
  local last_log
  last_log=$(tail -c 4000 /root/pr141-grunt/grokbot.log 2>/dev/null || printf '(no log)')
  local ci_state="unobservable"
  if command -v gh >/dev/null 2>&1; then
    if gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" 2>/dev/null | grep -qE '\|\s*(fail|failing)'; then
      ci_state="red"
    elif gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG" >/dev/null 2>&1; then
      ci_state="green-or-pending"
    fi
  fi
  # Breakage signals from the last turn: CI red, or refusals/errors in the wake log.
  if [ "$ci_state" != "red" ] && ! printf '%s' "$last_log" | grep -qE 'refused|[Ee]rror|Traceback|failed'; then
    printf '[grokbot] turn-debug eval (tick %s): clean — no debugger needed (§10.4 wake)\n' "$n"
    return 0
  fi
  local last; last=$(cat "$STATE/last-turn-debug" 2>/dev/null || echo 0)
  [ $((n - last)) -ge 2 ] || { printf '[grokbot] turn-debug skipped: launched at tick %s\n' "$last"; return 0; }
  command -v atomic >/dev/null 2>&1 || { printf '[grokbot] turn-debug skipped: atomic CLI missing\n' >&2; return 0; }
  local prompt
  prompt=$(printf '%s' "Turn-end debugger (contract §10.2, wake tick $n): evaluate the LAST turn of ${REPO_SLUG}#${PR_NUMBER} against the GENERAL GOALS (https://github.com/Dezocode/Sai/pull/141#issuecomment-5402885809). Last-turn output: ${last_log}. CI state: ${ci_state}. Use the debugger skill: name the exact failure, fix with one failing-behavior test first, re-run the gates (pytest, bash -n on hook scripts, gateway audit tail). You have authority to edit and re-run gates. Zero gaming/placeholders (§10.3); report verdicts as a PR comment on #${PR_NUMBER}.")
  if "$GATEWAY" debugger-launch "$SELF" spawn debugger "$prompt"; then
    printf '%s' "$n" > "$STATE/last-turn-debug"
    printf '[grokbot] turn-debug debugger launched (tick %s) — tracked for self-heal\n' "$n"
  else
    printf '[grokbot] turn-debug launch refused by gateway (named refusal above)\n' >&2
  fi
}
maybe_debugger_launch() {  # §10(2)/skill §9: CI-red wake -> debugger subagent via atomic CLI,
  # never a self-loop. Bounded: skip if the immediately previous wake already launched one.
  [ "$1" = "tdd" ] || return 0
  local last; last=$(cat "$STATE/last-debugger-launch" 2>/dev/null || echo 0)
  [ $(($2 - last)) -ge 2 ] || { printf '[grokbot] debugger launch skipped: launched at tick %s\n' "$last"; return 0; }
  command -v atomic >/dev/null 2>&1 || { printf '[grokbot] debugger launch skipped: atomic CLI missing\n' >&2; return 0; }
  local prompt
  prompt=$(printf '%s' "CI on ${REPO_SLUG}#${PR_NUMBER} is red (wake tick $2). Debug the failing checks: run 'gh pr checks ${PR_NUMBER} --repo ${REPO_SLUG}' to name them, then fix with the tdd skill — one failing-behavior test first, smallest green change. You have authority to edit the failing code and re-run the gates. Zero gaming/placeholders (contract §10.3); report verdicts as a PR comment on #${PR_NUMBER}.")
  if "$GATEWAY" debugger-launch "$SELF" spawn debugger "$prompt"; then
    printf '%s' "$2" > "$STATE/last-debugger-launch"
    printf '[grokbot] debugger worker launched (tick %s) — tracked for self-heal\n' "$2"
  else
    printf '[grokbot] debugger launch refused by gateway (named refusal above)\n' >&2
  fi
}

cmd_tick() {
  # Serialize concurrent ticks (hook stop + daemon can overlap): flock guards the
  # counter read-modify-write and keeps two wakes from double-posting wake-proof.
  if command -v flock >/dev/null 2>&1; then exec 9>"$STATE/ticks.lock"; flock 9; fi
  n=$(cat "$STATE/ticks" 2>/dev/null || echo 0); n=$((n+1)); printf '%s' "$n" > "$STATE/ticks"
  maybe_restart_daemon  # self-heal: revive a wedged/dead daemon from its stale heartbeat
  self_heal; drain_requeue  # sweep launches BEFORE new drains so errored work requeues first
  turn_debug_chain "$n"  # §10(2): debugger evaluates last turn BEFORE wake automation
  cmd_name >/dev/null; cmd_inbox; cmd_flightboard >/dev/null
  STATE_DIR="$STATE" "$GATEWAY" channel-probe "$0" channel-probe >/dev/null || true   # tmux liveness → state/channels.json (spec 2026-08-25)
  wake_proof "$n"
  skill="$(continuation_prompt)"
  printf '[grokbot] wake %s @ %s — continuation skill: %s\n' "$n" "$(date -u +%H:%M:%SZ)" "$skill"
  maybe_debugger_launch "$skill" "$n"
  if command -v flock >/dev/null 2>&1; then flock -u 9; exec 9>&-; fi
  # Explicit success: a bare `[ -f STOP ] && exit 0` would leave exit status 1 on an
  # ordinary wake (no stop file), which hook runners read as a failed hook.
  [ ! -f "$STATE/GROKBOT_STOP" ] || printf '[grokbot] stop-file seen; waking no more\n'
  return 0  # hook-7 fix: was `exit 0`, which killed the daemon after its FIRST wake —
            # cmd_tick is shared by cmd_daemon's loop. Standalone `tick` invocations
            # still exit 0 via the case dispatch below (hook-runner contract kept).
}

cmd_hook() {  # structural parity with production .cursor wiring (19 events); no side effects
  printf '{"continue":true}\n'; exit 0
}

cmd_daemon() {
  printf '[grokbot] daemon started: interval=%ss stop-file=%s\n' "$INTERVAL" "$STATE/GROKBOT_STOP"
  while [ ! -f "$STATE/GROKBOT_STOP" ]; do
    printf '%s %s\n' "$$" "$(date +%s)" > "$HEARTBEAT"  # liveness proof for stale-heartbeat respawn
    cmd_tick; sleep "$INTERVAL"
  done
  printf '[grokbot] stop-file seen; exiting\n'
}

case "${1:-tick}" in
  name) cmd_name ;;
  inbox) cmd_inbox ;;
  flightboard) cmd_flightboard ;;
  tick) cmd_tick; exit 0 ;;  # hook-7: standalone tick keeps hook-runner exit-0 contract
  hook) cmd_hook ;;
  daemon) cmd_daemon ;;
  spawn) spawn_tracked "$2" 0 "$3" ;;  # gateway re-entry for tracked debugger launches
  channel-probe) STATE_DIR="$STATE"; export STATE_DIR; write_channel_state ;;   # gateway re-entry for tmux liveness reporting
  *) fail "usage: grokbot.sh [name|inbox|flightboard|tick|hook|daemon|spawn]" ;;
esac
