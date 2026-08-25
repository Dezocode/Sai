#!/usr/bin/env bash
# Resolve an agent handle to its canonical Sai Harness identity, or look up all
# aliases for one. Fails closed (exit 1) on unknown handles so unregistered
# identities get zero authority.
#
# Usage:
#   resolve.sh <handle>            print canonical identity for <handle>
#   resolve.sh --lookup <identity> print every alias resolving to <identity>
#   resolve.sh --list              print the whole alias table
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="$DIR/aliases.json"

die() { echo "error: $*" >&2; exit 1; }

[ -f "$REGISTRY" ] || die "registry not found: $REGISTRY"

# Emit "alias<TAB>canonical" rows without requiring jq.
rows() {
  sed -n 's/^[[:space:]]*"\([^"]*\)"[[:space:]]*:[[:space:]]*"\([a-z][^"]*\)"[[:space:]]*,\{0,1\}[[:space:]]*$/\1\t\2/p' "$REGISTRY"
}

case "${1:-}" in
  --list)
    rows
    ;;
  --lookup)
    [ $# -eq 2 ] || die "--lookup requires exactly one identity"
    out="$(rows | awk -F'\t' -v id="$2" '$2 == id { print $1 }')"
    [ -n "$out" ] || die "unknown identity: $2"
    printf '%s\n' "$out"
    ;;
  "")
    die "usage: resolve.sh <handle> | --lookup <identity> | --list"
    ;;
  -*)
    die "unknown option: $1"
    ;;
  *)
    [ $# -eq 1 ] || die "resolve takes exactly one handle"
    out="$(rows | awk -F'\t' -v h="$1" '$1 == h { print $2 }')"
    [ -n "$out" ] || die "unregistered handle: $1"
    printf '%s\n' "$out"
    ;;
esac
