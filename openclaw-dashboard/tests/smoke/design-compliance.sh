#!/usr/bin/env bash
# design-compliance.sh — unified design language + immersive chat layout gate
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TOKENS="$ROOT/design/tokens.json"
LANG="$ROOT/design/DESIGN-LANGUAGE.md"
COMPONENTS="$ROOT/design/components.md"
VIOLATIONS=0

python3 -m json.tool "$TOKENS" >/dev/null

# v2 token schema checks
python3 - <<'PY' "$TOKENS"
import json, sys
t = json.load(open(sys.argv[1]))
required = ["layout", "liveData", "motion", "components"]
for k in required:
    if k not in t:
        raise SystemExit(f"FAIL tokens.json missing key: {k}")
modes = t.get("layout", {}).get("modes", {})
if "immersive-game" not in modes:
    raise SystemExit("FAIL tokens.json missing layout.modes.immersive-game")
if "select" not in t.get("components", {}):
    raise SystemExit("FAIL tokens.json missing components.select")
print("tokens schema v2: OK")
PY

for f in "$LANG" "$COMPONENTS"; do
  if [ ! -f "$f" ]; then
    echo "FAIL missing $f"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done

if ! grep -q 'immersive-game' "$LANG"; then
  echo "FAIL DESIGN-LANGUAGE.md must document immersive-game mode"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if ! grep -q 'ImmersiveGameShell' "$COMPONENTS"; then
  echo "FAIL components.md must define ImmersiveGameShell"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if ! grep -q 'CursorSelect' "$COMPONENTS"; then
  echo "FAIL components.md must define CursorSelect dropdown"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if ! grep -q 'liveDataHost\|liveData' "$TOKENS"; then
  echo "FAIL tokens.json must define liveData"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# Run base token import gate
"$ROOT/tests/smoke/design-tokens.sh"

if [ "$VIOLATIONS" -gt 0 ]; then exit 1; fi
echo "design-compliance.sh: OK"
exit 0
