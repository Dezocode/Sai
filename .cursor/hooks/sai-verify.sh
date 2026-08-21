#!/usr/bin/env bash
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"
gitdir=$(git rev-parse --absolute-git-dir)
base=$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)
if [ -n "$base" ] && git cat-file -e "$base:cmd/sai-verify/main.go" 2>/dev/null; then srcid=$( { git show "$base:cmd/sai-verify/main.go"; git show "$base:go.mod"; } | sha256sum | cut -c1-16 ); bin="$gitdir/sai-verify-$base-$srcid"; if [ ! -x "$bin" ]; then src=$(mktemp -d); git archive "$base" cmd/sai-verify go.mod | tar -x -C "$src"; (cd "$src" && GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify); rm -rf "$src"; fi; exec "$bin" --root "$ROOT" --evidence "$gitdir/sai-verify-evidence.json" hook; fi
python3 -c 'import json,sys; json.loads(sys.stdin.read() or "{}"); print(json.dumps({"additional_context":"FEATURE CONTEXT\nbootstrap: BASE has no sai-verify kernel. Wrapper does not compile candidate Go. Mutations are allowed until a BASE kernel exists; after merge the BASE-built kernel denies unbound mutations.\n"}))'
