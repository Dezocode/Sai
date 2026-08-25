#!/usr/bin/env bash
# T7: deletion safety — production has ZERO references to the Harness tree and
# the sai-verify kernel still builds with the Harness tree removed.
set -euo pipefail
S="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$S/../../.." && pwd)"   # repo root (prototypes/plugins/sai-harness -> up 3)
# 1. no production path references the harness tree
if grep -rn "plugins/sai-harness" \
     "$ROOT/cmd" "$ROOT/internal" "$ROOT/services" "$ROOT/.github" "$ROOT/go.mod" \
     2>/dev/null | grep -v "^Binary"; then
  echo "FAIL: production references sai-harness prototype"; exit 1
fi
echo "PASS: zero production references to sai-harness"
# 2. sai-verify kernel builds with the harness tree deleted (temp clone of worktree index)
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git -C "$ROOT" archive HEAD | tar -x -C "$T"
rm -rf "$T/prototypes/plugins/sai-harness"
GO="$(command -v go || echo /usr/local/go/bin/go)"
if [ ! -x "$GO" ]; then echo "SKIP: go toolchain unavailable — build proof must run where go exists"; exit 2; fi
(cd "$T" && "$GO" build ./cmd/sai-verify && "$GO" vet ./cmd/sai-verify) || { echo "FAIL: kernel broken without harness"; exit 1; }
echo "T7 PASS: production green with Harness tree deleted"
