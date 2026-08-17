#!/usr/bin/env bash
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"
bin="$ROOT/.git/sai-verify-bin"
need=0
[ -x "$bin" ] || need=1
for f in cmd/sai-verify/*.go go.mod; do [ -e "$f" ] && [ "$f" -nt "$bin" ] && need=1; done
[ "$need" = 1 ] && GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify
exec "$bin" --root "$ROOT" hook
