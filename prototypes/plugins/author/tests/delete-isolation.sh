#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"

if grep -R -n 'prototypes/plugins' apps/apple/ cmd/sai/ internal/ 2>/dev/null; then
  echo "FAIL: production references prototypes/plugins"
  exit 1
fi

test -f prototypes/plugins/author/Package.swift

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
if test -d prototypes/plugins/author; then
  mv prototypes/plugins/author "$tmp/author-backup"
  restore() { mv "$tmp/author-backup" prototypes/plugins/author; }
  trap restore EXIT
fi

go run ./cmd/sai-design-check
go test ./cmd/sai-verify/...

echo "PASS delete-isolation"
