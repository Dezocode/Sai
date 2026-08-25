#!/usr/bin/env bash
# aspectizer.sh — prototype hook (cross-intercom lane): decompose an incoming user
# request into named aspects on receipt. Prototype tier: fail-open with honest
# stderr; production hooks remain sai-verify's.
set -u
payload=$(cat)

summary_aspects=$(printf '%s' "$payload" | python3 -c '
import json, sys, re
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
prompt = next((d[k] for k in ("prompt", "user_prompt", "input", "ticket", "message")
               if isinstance(d.get(k), str) and d[k].strip()), "")
if not prompt.strip():
    print("aspectizer: no prompt text in hook payload; aspects not derived.")
    print("[]")
    raise SystemExit
parts = [p.strip(" \t-*.") for p in re.split(r"(?i)(?<=[.!?])\s+|\n+|;\s+", prompt) if len(p.strip()) >= 4]
named = []
for i, p in enumerate(parts[:8], 1):
    kind = ("goal" if re.search(r"\b(goal|must|should|want|need|make it)\b", p, re.I)
            else "context" if re.search(r"\b(refer|per|see|docs?|contract|pr #?\d+)\b", p, re.I)
            else "task")
    named.append({"aspect": "A%d" % i, "kind": kind, "text": p[:180]})
if not named:
    print("aspectizer: request too short to aspectize."); print("[]"); raise SystemExit
print("aspectizer: %d aspects — %s" % (len(named), ", ".join("%s:%s" % (x["aspect"], x["kind"]) for x in named)))
print(json.dumps(named))
') || { printf '{"additionalContext":"aspectizer: payload parse failure"}'; exit 0; }

summary=$(printf '%s\n' "$summary_aspects" | sed -n '1p')
aspects=$(printf '%s\n' "$summary_aspects" | sed -n '2p')
clean() { printf '%s' "$1" | tr '\n\r\t"\\' '   ..'; }
printf '{"additionalContext":"%s | %s"}' "$(clean "$summary")" "$(clean "$aspects")"
