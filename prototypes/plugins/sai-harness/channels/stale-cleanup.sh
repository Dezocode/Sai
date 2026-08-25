#!/usr/bin/env bash
# Stale channel cleanup: mark channels dead > STALE_AFTER seconds (default 3600)
# as stale in channels.json (never delete ledgers — state survives, G2).
# Bounded: single pass per invocation, no polling loop. Dry-run by default.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHANNELS="${SAI_CHANNELS_JSON:-$HOME/.sai-harness/state/channels.json}"
AFTER="${STALE_AFTER:-3600}"
DRY=1; [ "${1:-}" = "--commit" ] && DRY=0
[ -f "$CHANNELS" ] || { echo "error: no channels file: $CHANNELS" >&2; exit 1; }
python3 - "$CHANNELS" "$AFTER" "$DRY" <<'PY'
import json,sys,time
p,after,dry=sys.argv[1],int(sys.argv[2]),sys.argv[3]=="--commit"
d=json.load(open(p)); now=time.time(); n=0
for c in d.get("channels",[]):
    if not c.get("alive"):
        act=c.get("activity_at")
        age=None
        if act:
            try:
                import datetime
                t=datetime.datetime.fromisoformat(act.replace("Z","+00:00")).timestamp()
                age=now-t
            except Exception: pass
        if age is None or age>after:
            if dry: print(f"would mark stale: {c['bot']} (age={age})")
            else: c["stale"]=True; n+=1
if dry: print("dry-run: no changes")
else:
    d["stale_cleanup_at"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
    json.dump(d,open(p,"w"),indent=1); print(f"marked {n} stale")
PY
