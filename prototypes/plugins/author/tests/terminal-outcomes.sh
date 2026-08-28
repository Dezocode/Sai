#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"
python3 scripts/verify-author-terminal-outcomes.py
