#!/usr/bin/env bash
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"
gitdir=$(git rev-parse --absolute-git-dir)
base=$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)
if [ -n "$base" ] && git cat-file -e "$base:cmd/sai-verify/main.go" 2>/dev/null; then srcid=$( { git show "$base:cmd/sai-verify/main.go"; git show "$base:go.mod"; } | sha256sum | cut -c1-16 ); bin="$gitdir/sai-verify-$base-$srcid"; if [ ! -x "$bin" ]; then src=$(mktemp -d); git archive "$base" cmd/sai-verify go.mod | tar -x -C "$src"; (cd "$src" && GOTOOLCHAIN=local GO111MODULE=on go build -o "$bin" ./cmd/sai-verify); rm -rf "$src"; fi; exec "$bin" --root "$ROOT" --evidence "$gitdir/sai-verify-evidence.json" hook; fi
python3 -c 'import json,sys; d=json.loads(sys.stdin.read() or "{}"); ev=str(d.get("hook_event_name") or ""); tn=str(d.get("tool_name") or ""); cmd=str(d.get("command") or "").strip(); mut=ev in ("beforeMCPExecution","afterFileEdit") or tn in ("Write","StrReplace","Delete","ApplyPatch") or (ev=="beforeShellExecution" and (any(c in cmd for c in ";|&`$()") or cmd not in ("go run ./cmd/sai-verify drive","go run ./cmd/sai-verify proof"))); ctx="FEATURE CONTEXT\nbootstrap: BASE has no sai-verify kernel. Exact recovery: go run ./cmd/sai-verify drive or proof. Mutations denied until a BASE kernel exists.\n"; print(json.dumps({"permission":"deny","user_message":"sai-verify bootstrap","agent_message":ctx,"additional_context":ctx} if mut else {"additional_context":ctx})); sys.exit(2 if mut else 0)'
