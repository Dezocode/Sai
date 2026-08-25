#!/usr/bin/env bash
# sai-channel.sh — channel-per-agent transport (OpenBot-derived), prototype tier.
# ONE tmux session per REGISTERED bot (session name = agents.yaml tmux.session, else id):
# window "repl" = persistent sai REPL — THE drain target (her directive 2026-08-25).
# Registration is the vocabulary: ids AND declared handles resolve; strangers are refused.
#
# Contract (spec specs/2026-08-25-sai-cli-layer-over-atomic.md):
#   launch_agent ⚠      sole door that births a channel (irreversible: spawns runtime)
#   channel_alive       pure liveness probe; NEVER mutates
#   deliver_to_channel  paste combined mentions as ONE submitted turn (caller owns gating,
#                       flock, and .sent parking — see grokbot.sh cmd_inbox)
set -u

HARNESS_DIR="${HARNESS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PLUGIN_DIR="${PLUGIN_DIR:-$(dirname "$HARNESS_DIR")}"
SAI_AGENTS_YAML="${SAI_AGENTS_YAML:-$HARNESS_DIR/agents.yaml}"
SAI_TMUX_SERVER="${SAI_TMUX_SERVER:-}"   # optional explicit tmux server; empty = default

sai_tmux() {  # all tmux traffic passes here so tests can shim one place
  command tmux ${SAI_TMUX_SERVER:+-L "$SAI_TMUX_SERVER"} "$@"
}

registered_ids() {  # the vocabulary: ids AND declared runtime handles (e.g. sai-grunt-f36750)
  python3 -c '
import sys
try:
    import yaml
except ImportError:
    sys.exit(3)
try:
    doc = yaml.safe_load(open(sys.argv[1]))
except Exception:
    sys.exit(2)
for a in (doc or {}).get("agents", []):
    i = a.get("id")
    if isinstance(i, str) and i.strip():
        print(i.strip())
    for h in (a.get("handles") or []):
        if isinstance(h, str) and h.strip():
            print(h.strip())
' "$SAI_AGENTS_YAML" 2>/dev/null
}

is_registered() {  # Named refusal: UnregisteredBot. No side effects either way.
  local want="$1" id
  [ -r "$SAI_AGENTS_YAML" ] || { printf 'UnregisteredBot: %s (no %s)\n' "$want" "$SAI_AGENTS_YAML" >&2; return 1; }
  while IFS= read -r id; do
    [ "$id" = "$want" ] && return 0
  done <<EOF
$(registered_ids)
EOF
  printf 'UnregisteredBot: %s — register in .sai/agents.yaml first\n' "$want" >&2
  return 1
}

_agent_field() {  # _agent_field <bot-id-or-handle> <yaml-key-path-dotted> <default>
  python3 -c '
import sys, yaml
doc = yaml.safe_load(open(sys.argv[2])) or {}
want, path, default = sys.argv[1], sys.argv[3], sys.argv[4]
def match(a):
    if a.get("id") == want:
        return True
    return want in (a.get("handles") or [])
for a in doc.get("agents", []):
    if match(a):
        cur = a
        for key in path.split("."):
            if not isinstance(cur, dict):
                cur = None
                break
            cur = cur.get(key)
        print(cur if cur else default)
        break
else:
    print(default)
' "$1" "$SAI_AGENTS_YAML" "$2" "$3" 2>/dev/null
}

channel_cwd() {      # per-bot anchor: agents.yaml tmux.cwd, else plugin checkout root
  _agent_field "$1" "tmux.cwd" "$PLUGIN_DIR"
}
channel_session() {  # tmux session NAME: agents.yaml tmux.session, else the id/handle itself
  _agent_field "$1" "tmux.session" "$1"
}

repl_target() {  # resolve "<session>:<window>.<pane>" for the repl window.
  # Hosts set base-index/pane-base-index freely (this one: 1/1) — never hard-code :0.0.
  local bot="$1" sess w p
  sess="$(channel_session "$bot")"
  w=$(sai_tmux list-windows -t "$sess" -F '#{window_name} #{window_index}' 2>/dev/null \
      | awk '$1=="repl"{print $2; exit}')
  [ -n "$w" ] || { printf '[sai] no repl window in session %s\n' "$sess" >&2; return 1; }
  p=$(sai_tmux show-options -gv pane-base-index 2>/dev/null || echo 0)
  printf '%s:%s.%s\n' "$sess" "$w" "$p"
}

channel_alive() {  # live RIGHT NOW means: session exists AND its repl pane is not dead
  local bot="$1" t
  sai_tmux has-session -t "$(channel_session "$bot")" 2>/dev/null || return 1
  t="$(repl_target "$bot")" || return 1
  ! sai_tmux list-panes -t "$t" -F '#{pane_dead}' 2>/dev/null | grep -q '^1$'
}

launch_agent() {  # ⚠ THE birth door. Registered ids only; refuses rather than improvising.
  local bot="$1" sess cwd t
  is_registered "$bot" || return 1
  command -v tmux >/dev/null 2>&1 || { printf 'TmuxMissing: cannot birth channel for %s\n' "$bot" >&2; return 2; }
  channel_alive "$bot" && { printf '[sai] channel %s already live\n' "$bot"; return 0; }
  cwd="$(channel_cwd "$bot")"
  sess="$(channel_session "$bot")"
  [ -d "$cwd" ] || { printf 'SpawnFailed: cwd %s missing for %s\n' "$cwd" "$bot" >&2; return 3; }
  # Window named "repl" is ALWAYS the delivery target — deliver_mention pastes there.
  if ! sai_tmux has-session -t "$sess" 2>/dev/null; then
    sai_tmux new-session -d -s "$sess" -n repl -c "$cwd" "exec env TERM=xterm-256color atomic --name $sess"
  elif ! t="$(repl_target "$bot")"; then
    sai_tmux new-window -d -t "$sess" -n repl -c "$cwd" "exec env TERM=xterm-256color atomic --name $sess"
  else
    sai_tmux respawn-pane -k -t "$t" -c "$cwd" "exec env TERM=xterm-256color atomic --name $sess"
  fi
  printf '[sai] launched channel %s as tmux:%s (window repl, cwd=%s)\n' "$bot" "$sess" "$cwd"
}

deliver_to_channel() {  # paste as ONE turn into the repl window. Caller handled gating + .sent ledger.
  local bot="$1" combined="$2" t
  channel_alive "$bot" || return 1
  t="$(repl_target "$bot")" || return 1
  printf '%s' "$combined" | sai_tmux load-buffer -b sai-inbox -
  sai_tmux paste-buffer -b sai-inbox -t "$t" -d
  sai_tmux send-keys -t "$t" Enter
  sai_tmux delete-buffer -b sai-inbox 2>/dev/null || true
}

channel_report() {  # machine-readable liveness for ALL registered channels (API monitoring surface).
  # Emits one JSON doc; written to state/channels.json each wake so the sessions-API
  # fleet probe / owner dashboards can watch every bot's atomic computer live.
  python3 - "$SAI_AGENTS_YAML" <<'PYEOF'
import json, subprocess, sys, yaml, datetime, os
yaml_path = sys.argv[1]
doc = yaml.safe_load(open(yaml_path)) or {}

def tmux(*args):
    return subprocess.run(["tmux", *args], capture_output=True, text=True)

channels = []
for a in doc.get("agents", []):
    aid = a.get("id", "")
    if not aid:
        continue
    sess = (a.get("tmux") or {}).get("session") or aid
    handles = [aid] + [h for h in (a.get("handles") or []) if isinstance(h, str)]
    entry = {"bot": aid, "handles": handles, "session": sess,
             "pr_assignment": str(a.get("pr_assignment", "")),
             "alive": False, "repl_pane_dead": None, "activity_at": None}
    r = tmux("has-session", "-t", sess)
    if r.returncode == 0:
        w = tmux("list-windows", "-t", sess, "-F", "#{window_name}\t#{window_active} #{window_index}")
        repl_idx = next((line.split("\t")[1].split()[1] for line in w.stdout.splitlines()
                         if line.startswith("repl")), None)
        entry["alive"] = True
        entry["windows"] = [l.split("\t")[0] for l in w.stdout.splitlines()]
        if repl_idx:
            p = tmux("display-message", "-p", "-t", f"{sess}:{repl_idx}",
                     "#{pane_dead} #{pane_current_command}")
            dead, cmd = (p.stdout.split() + ["?", "?"])[:2]
            entry["repl_pane_dead"] = dead == "1"
            entry["repl_process"] = cmd
            act = tmux("display-message", "-p", "-t", f"{sess}:{repl_idx}", "#{session_activity}")
            try:
                ts = int(act.stdout.strip())
                entry["activity_at"] = datetime.datetime.fromtimestamp(
                    ts, datetime.UTC).isoformat().replace("+00:00", "Z")
            except Exception:
                pass
    channels.append(entry)

out = {"schema": "sai-channels-v1",
       "generated_at": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
       "host": os.uname().nodename, "channels": channels}
print(json.dumps(out, indent=1))
PYEOF
}

write_channel_state() {  # called by cmd_tick: gated externally as decision `channel-probe`
  mkdir -p "$STATE_DIR"
  channel_report > "$STATE_DIR/channels.json.tmp" && mv "$STATE_DIR/channels.json.tmp" "$STATE_DIR/channels.json"
  printf '[sai] channel-probe wrote %s\n' "$STATE_DIR/channels.json"
}
