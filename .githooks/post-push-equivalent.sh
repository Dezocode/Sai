#!/usr/bin/env bash
# Git has no native post-push hook. This wrapper performs the push, then
# confirms the actual remote state before any success claim.
#
# Usage: .githooks/post-push-equivalent.sh [git-push-args...]
# Example: .githooks/post-push-equivalent.sh -u origin dezo/my-task
#
# CI (.github/workflows/agent-audit.yml) provides the server-side
# confirmation for pushes made without this wrapper.
set -uo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)

git push "$@"
push_status=$?
if [ $push_status -ne 0 ]; then
  "$REPO_ROOT/scripts/agent-report" emit BLOCKED \
    --purpose "git push $*" \
    --result "push failed with exit code $push_status" \
    --risks "remote state unchanged or unknown; do not claim success" || true
  exit $push_status
fi

# Determine the remote actually used (first non-flag argument, default origin).
remote="origin"
for arg in "$@"; do
  case "$arg" in -*) continue;; *) remote=$arg; break;; esac
done
exec "$REPO_ROOT/scripts/agent-report" push-confirm "$remote"
