#!/usr/bin/env bash
# Exact-head CI probe: no carried counts. Usage: ci-probe.sh <pr> [repo]
# Prints pass/fail/pending counts; exits nonzero if any check failed.
set -euo pipefail
PR="${1:?usage: ci-probe.sh <pr> [repo]}"
REPO="${2:-Dezocode/Sai}"
OUT="$(gh pr checks "$PR" -R "$REPO" 2>/dev/null)" || true
P=$(echo "$OUT" | grep -c "pass" || true)
F=$(echo "$OUT" | grep -c "fail" || true)
N=$(echo "$OUT" | grep -c "pending" || true)
echo "pass=$P fail=$F pending=$N"
[ "$F" -eq 0 ]
