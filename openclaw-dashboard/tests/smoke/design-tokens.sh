#!/usr/bin/env bash
# design-tokens.sh — enforce unified Cursor design language imports
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TOKENS="$ROOT/design/tokens.json"
python3 -m json.tool "$TOKENS" >/dev/null
VIOLATIONS=0
if [ -d "$ROOT/apps/desktop/src/tabs" ]; then
  while IFS= read -r f; do
    if ! grep -q 'design-system/tokens\|@/design-system' "$f" 2>/dev/null; then
      if grep -E '#[0-9a-fA-F]{3,8}' "$f" >/dev/null 2>&1; then
        echo "FAIL inline hex in $f — use design tokens"
        VIOLATIONS=$((VIOLATIONS + 1))
      fi
    fi
  done < <(find "$ROOT/apps/desktop/src/tabs" -name '*.tsx' 2>/dev/null || true)
fi
if [ ! -f "$ROOT/design/DESIGN-LANGUAGE.md" ]; then
  echo "FAIL missing DESIGN-LANGUAGE.md"; exit 1
fi
if [ "$VIOLATIONS" -gt 0 ]; then exit 1; fi
echo "design-tokens.sh: OK (stub — expand when desktop src exists)"
exit 0
