#!/usr/bin/env bash
# lane-connector.sh — prototype gh-auth bridge (cross-intercom lane).
# Authenticates with the LOCAL gh identity, reads the public sessions-API planes,
# and upserts a sai-sessions-v2 session row tagged side=local|repo for crosscomming.
# Prototype tier: read paths work today against the public API; the write path
# emits the exact request the API lane (PR #141 work) must accept per GOALS.md.
set -eu
SESSIONS_API_URL="${SESSIONS_API_URL:-https://srv1840454.hstgr.cloud/api/hermes-sessions}"
CROSSCOM_SIDE="${CROSSCOM_SIDE:-local}"          # local | repo
TASK_ID="${SAI_TASK_ID:-unknown-task-id}"
REPO_SLUG="${CROSSCOM_REPO:-Dezocode/Sai}"

fail() { printf 'lane-connector: %s\n' "$1" >&2; exit 1; }
command -v gh >/dev/null 2>&1 || fail "gh CLI not found — local gh auth is this plugin's auth mechanism"
command -v curl >/dev/null 2>&1 || fail "curl not found"
gh auth token >/dev/null 2>&1 || fail "gh auth token unavailable — run: gh auth login"

GH_LOGIN=$(gh api user --jq .login 2>/dev/null) || GH_LOGIN="her"
head=$(git rev-parse --short HEAD 2>/dev/null || printf '0000000')
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
session_id="crosscomm-${REPO_SLUG#*/}-${TASK_ID}"

row=$(python3 -c '
import json,sys
print(json.dumps({"id":sys.argv[1],"pr":None,"agent":"her","harness":"gh-lane","model":"local-gh-auth",
 "head":sys.argv[2],"status":"active","heartbeat_at":sys.argv[3],"phase":"crosscomm",
 "side":sys.argv[4],"monitors":["crosscom"],"steer":"","task_id":sys.argv[5]}))
' "$session_id" "$head" "$now" "$CROSSCOM_SIDE" "$TASK_ID")

case "${1:-reconcile}" in
  read|reconcile)
    tmp=$(mktemp)
    for plane in sessions prs health; do
      code=$(curl -sS -o "$tmp" -w '%{http_code}' "$SESSIONS_API_URL/$plane" 2>/dev/null || printf '000')
      printf '[%s] GET /%s -> %s\n' "$CROSSCOM_SIDE" "$plane" "$code"
      [ "$code" = "200" ] || continue
      TASK_ID="$TASK_ID" python3 -c '
import json,os,sys
d=json.load(open(sys.argv[1]))
rows=d.get("sessions") or d.get("prs") or []
tid=os.environ["TASK_ID"]
mine=[r for r in rows if isinstance(r,dict) and str(r.get("task_id",""))==tid]
print("   schema=%s rows=%d mine=%d" % (d.get("schema"), len(rows), len(mine)))
for r in mine[:3]: print("   crosscomm peer:", r.get("id"), r.get("status"), r.get("side","repo-side-default"))
' "$tmp" || true
    done
    rm -f "$tmp" ;;
  upsert)
    # Write path is the contract defined in docs/GOALS.md goal 3: the API lane must
    # accept local gh Bearer credentials. Until then this prints the request instead
    # of firing it — an unauthenticated guess would be a silent no-op at best.
    printf 'lane-connector: WRITE CONTRACT (not fired in prototype)\n'
    printf 'POST %s/reconcile\nAuthorization: Bearer <LOCAL_GH_TOKEN login=%s>\nX-Sessions-Agent: her\nContent-Type: application/json\n%s\n' \
      "$SESSIONS_API_URL" "$GH_LOGIN" "$row" ;;
  *) fail "usage: lane-connector.sh [read|reconcile|upsert]" ;;
esac
