#!/usr/bin/env bash
# verify-all-dependencies.sh — A0 dependency gate (Hostinger VPS bootstrap)
#
# Usage:
#   verify-all-dependencies.sh           # enforce all required tools
#   verify-all-dependencies.sh --self-test # syntax-only (CI/scaffold)
#
# Exit 0 when Node, npm, git, python3, jq, gh, and openclaw CLI are available.
set -euo pipefail

MODE="${1:-verify}"
ROOT=$(cd "$(dirname "$0")/.." && pwd)

if [ "$MODE" = "--self-test" ]; then
  bash -n "$0"
  echo "verify-all-dependencies.sh --self-test: PASS"
  exit 0
fi

if [ "$MODE" = "-h" ] || [ "$MODE" = "--help" ]; then
  echo "Usage: verify-all-dependencies.sh [--self-test]"
  exit 0
fi

errors=0
need() {
  local name="$1"
  shift
  if command -v "$name" >/dev/null 2>&1; then
    echo "  OK $name ($("$@" 2>/dev/null | head -1))"
  else
    echo "  FAIL missing: $name"
    errors=$((errors + 1))
  fi
}

echo "verify-all-dependencies.sh: checking A0 toolchain..."
need node node -v
need npm npm -v
need git git --version
need python3 python3 --version
need jq jq --version
need gh gh --version
need openclaw openclaw --version

if [ "$errors" -gt 0 ]; then
  echo "verify-all-dependencies.sh: FAIL ($errors missing)" >&2
  echo "  Remediation: openclaw-dashboard/docs/vps-bootstrap.md §1" >&2
  exit 1
fi

echo "verify-all-dependencies.sh: PASS"
exit 0
