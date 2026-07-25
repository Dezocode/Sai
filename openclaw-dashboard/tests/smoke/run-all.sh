#!/usr/bin/env bash
# run-all.sh — dashboard smoke suite (organization gate: zero blocking errors)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
echo "openclaw-dashboard smoke: STUB — implement per tab BUILD.md phases"
for t in tracking github auth host-health; do
  echo "  [pending] $t"
done
exit 2
