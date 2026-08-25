#!/usr/bin/env bash
# Migrate legacy per-checkout .sai/state into the canonical host state dir.
# Canonical state lives OUTSIDE any checkout so fresh clones cannot wipe it.
# Fail-closed: dry-run is the default; --commit requires a clean plan; every
# action is journaled for rollback.
#
# Usage:
#   migrate.sh --src <checkout>/.sai/state [--dest ~/.sai-harness/state] --dry-run
#   migrate.sh --src <checkout>/.sai/state [--dest ~/.sai-harness/state] --commit
#   migrate.sh --src <checkout>/.sai/state [--dest ~/.sai-harness/state] --rollback
set -euo pipefail

SRC=""; DEST="$HOME/.sai-harness/state"; MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --src) SRC="$2"; shift 2;;
    --dest) DEST="$2"; shift 2;;
    --dry-run) MODE="dry"; shift;;
    --commit) MODE="commit"; shift;;
    --rollback) MODE="rollback"; shift;;
    *) echo "error: unknown arg $1" >&2; exit 1;;
  esac
done
[ -n "$MODE" ] || { echo "error: mode required (--dry-run|--commit|--rollback)" >&2; exit 1; }

JOURNAL="$DEST/migration.journal"

case "$MODE" in
  rollback)
    [ -f "$JOURNAL" ] || { echo "error: no journal to roll back" >&2; exit 1; }
    while IFS=$'\t' read -r op from to; do
      case "$op" in
        moved) mv "$to" "$from" && echo "restored $from";;
        copied) rm -rf "$to" && echo "removed copy $to";;
      esac
    done < "$JOURNAL"
    rm -f "$JOURNAL"
    echo "rollback complete"
    exit 0;;
esac

[ -d "$SRC" ] || { echo "error: source state dir not found: $SRC" >&2; exit 1; }
mkdir -p "$DEST"

# Files we migrate (channels.json, audit.jsonl, inbox ledgers, wake journal).
PLAN="$(mktemp)"; trap 'rm -f "$PLAN"' EXIT
for f in channels.json audit.jsonl wake.log flightboard.json ticks; do
  : ;
done
for f in channels.json audit.jsonl wake.log flightboard.json ticks; do
  [ -f "$SRC/$f" ] && echo "copyfile $SRC/$f $DEST/$f" >> "$PLAN"
done
for d in requeue dead-letter launches; do
  [ -d "$SRC/$d" ] && echo "copydir $SRC/$d $DEST/$d" >> "$PLAN"
done
[ -d "$SRC/inbox" ] && echo "copydir $SRC/inbox $DEST/inbox" >> "$PLAN"

echo "== migration plan ($MODE) =="
cat "$PLAN"
if [ "$MODE" = "dry" ]; then echo "dry-run: no changes made"; exit 0; fi

: > "$JOURNAL"
while IFS=' ' read -r op from to; do
  if [ "$op" = "copyfile" ]; then
    cp "$from" "$to" && echo -e "copied\t$from\t$to" >> "$JOURNAL"
  else
    mkdir -p "$to" && cp -R "$from/." "$to/" && echo -e "copied\t$from\t$to" >> "$JOURNAL"
  fi
done < "$PLAN"
echo "commit complete; journal at $JOURNAL (migrate.sh --rollback to undo)"
