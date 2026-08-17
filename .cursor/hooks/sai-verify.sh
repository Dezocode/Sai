#!/usr/bin/env bash
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"
gitdir=$(git rev-parse --absolute-git-dir)
head=$(git rev-parse HEAD)
bin="$gitdir/sai-verify-$head"
need=0; [ -x "$bin" ] || need=1
for f in cmd/sai-verify/*.go go.mod; do [ -e "$f" ] && [ "$f" -nt "$bin" ] && need=1; done
if [ "$need" = 1 ]; then
  if [ -f .git ]; then src=$(mktemp -d); cp -a cmd go.mod "$src/"; (cd "$src" && GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify); rm -rf "$src"
  else GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify; fi
fi
exec "$bin" --root "$ROOT" --evidence "$gitdir/sai-verify-evidence.json" hook
