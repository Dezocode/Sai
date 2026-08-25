#!/usr/bin/env bash
# telegram-bridge.sh — live Telegram inbox/outbox for Sai Harness (prototype tier).
# Owner talks to the bot from a phone; messages are aspectized, queued into the
# composer inbox, and drained by grokbot into atomic (tmux or background workers).
# Steering verbs: /status /stop /wake. Outbox: replies land back in the chat.
#
# Requires (in /root/.sai-fleet/tokens.env): TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
set -u
HARNESS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$HARNESS_DIR/state"
[ -f /root/.sai-fleet/tokens.env ] && { set -a; . /root/.sai-fleet/tokens.env; set +a; }
: "${TELEGRAM_BOT_TOKEN:?telegram-bridge: TELEGRAM_BOT_TOKEN missing from fleet creds}"
: "${TELEGRAM_CHAT_ID:?telegram-bridge: TELEGRAM_CHAT_ID missing from fleet creds}"
case "$TELEGRAM_CHAT_ID" in *[!0-9-]*|"") fail "TELEGRAM_CHAT_ID malformed (got ${#TELEGRAM_CHAT_ID} chars, want numeric) — re-provision in fleet creds";; esac
API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}"
TMUX_SESSION="${SAI_HARNESS_TMUX:-sai-harness}"

tg() { curl -sS -X POST "$API/$1" -H 'Content-Type: application/json' -d "$2"; }
out() { tg "sendMessage" "$(python3 -c 'import json,sys;print(json.dumps({"chat_id":int(sys.argv[1]),"text":sys.argv[2][:4000]}))' "$TELEGRAM_CHAT_ID" "$1")" >/dev/null; }

aspectize() {  # reuse the aspectizer: prompt -> aspectized context for the atomic worker
  printf '{"prompt":%s}' "$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1")" \
    | bash "$HARNESS_DIR/hooks/aspectizer.sh" 2>/dev/null
}

ensure_tmux() {  # root atomic runtime in tmux — the native /prompt surface
  tmux has-session -t "$TMUX_SESSION" 2>/dev/null || tmux new-session -d -s "$TMUX_SESSION" -c /root/worktrees/sai-pr77 'bash -lc "export PATH=/usr/local/go/bin:$PATH; atomic"' 
}

cmd_status() {
  local ticks ci
  ticks=$(cat "$STATE/ticks" 2>/dev/null || echo 0)
  ci=$(cd /root/worktrees/sai-pr77 && gh pr checks 146 2>/dev/null | grep -cE '\|(pass|fail)' )
  out "sai-harness status: agent=her ticks=$ticks tmux=$([ -n "$(tmux has-session -t "$TMUX_SESSION" 2>/dev/null && echo y)" ] && echo up || echo down) ci-checks-observed=$ci stop-file=$([ -f "$STATE/GROKBOT_STOP" ] && echo SET || echo none)"
}

handle() {  # $1 = raw message text; aspectize then route
  local text="$1"
  case "$text" in
    /status) cmd_status ;;
    /stop)   touch "$STATE/GROKBOT_STOP"; out "grokbot stopped (delete $STATE/GROKBOT_STOP to resume)" ;;
    /wake)   rm -f "$STATE/GROKBOT_STOP"; bash "$HARNESS_DIR/hooks/grokbot.sh" tick; out "manual wake fired" ;;
    /tmux\ *) prompt="${text#/tmux }"; ensure_tmux
              a=$(aspectize "$prompt")
              tmux send-keys -t "$TMUX_SESSION" "$prompt" Enter
              out "sent to atomic tmux [$TMUX_SESSION]. aspects: ${a:0:500}" ;;
    *)       mkdir -p "$STATE/inbox"
             printf '%s\n' "$(aspectize "$text")" > "$STATE/inbox/tg-$(date +%s%N).md"
             out "queued for next wake (grokbot drains inbox into atomic workers)" ;;
  esac
}

case "${1:-daemon}" in
  daemon)
    printf '[tg-bridge] live: polling Telegram for chat %s\n' "$TELEGRAM_CHAT_ID"
    offset=$(cat "$STATE/tg-offset" 2>/dev/null || echo 0)
    while [ ! -f "$STATE/GROKBOT_STOP" ]; do
      resp=$(curl -sS "$API/getUpdates?timeout=50&offset=$((offset+1))" 2>/dev/null) || { sleep 10; continue; }
      offset=$(printf '%s' "$resp" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); r=d.get("result",[])
    print(r[-1]["update_id"] if r else sys.argv[1])
except Exception: print(sys.argv[1])' "$offset")
      printf '%s' "$offset" > "$STATE/tg-offset"
      printf '%s' "$resp" | python3 -c '
import json,sys
d=json.load(sys.stdin)
for u in d.get("result",[]):
    m=u.get("message") or {}
    t=(m.get("text") or "").strip()
    if t: print(t.replace("\x00",""))
' | while IFS= read -r msg; do [ -n "$msg" ] && handle "$msg"; done
    done
    printf '[tg-bridge] stop-file seen; exiting\n' ;;
  send) shift; out "$*" ;;
  tmux) shift; handle "/tmux $*" ;;
  status) cmd_status ;;
  *) printf 'usage: telegram-bridge.sh [daemon|send <text>|tmux <prompt>|status]\n' ;;
esac
