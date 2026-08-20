#!/usr/bin/env bash
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"
gitdir=$(git rev-parse --absolute-git-dir)
head=$(git rev-parse HEAD); srcid=$( { printf '%s\n' "$ROOT"; cat cmd/sai-verify/*.go go.mod; } | sha256sum | cut -c1-16)
bin="$gitdir/sai-verify-$head-$srcid"
if [ ! -x "$bin" ]; then
  if [ -f .git ]; then src=$(mktemp -d); cp -a cmd go.mod "$src/"; (cd "$src" && GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify); rm -rf "$src"
  else GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify; fi
fi
exec "$bin" --root "$ROOT" --evidence "$gitdir/sai-verify-evidence.json" hook
