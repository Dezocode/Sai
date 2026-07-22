#!/usr/bin/env bash
# verify-secrets-compliance.sh — PR #45 secrets structure gate
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$ROOT/.." && pwd)
FAIL=0

check_file() {
  if [ -f "$1" ]; then echo "OK $2"; else echo "FAIL missing $2"; FAIL=1; fi
}

check_file "$ROOT/docs/secrets-security.md" "secrets-security.md"
check_file "$ROOT/docs/auth-matrix.md" "auth-matrix.md"
check_file "$ROOT/settings/secrets/CONTEXT.md" "settings/secrets/CONTEXT.md"
check_file "$ROOT/.gitignore" "openclaw-dashboard/.gitignore"
check_file "$REPO/.ai/agents/alfred/runtimes/openclaw/gateway/config/secrets-store.schema.json" "secrets-store.schema.json"

python3 -m json.tool "$REPO/.ai/agents/alfred/runtimes/openclaw/gateway/config/secrets-store.schema.json" >/dev/null

CONTRACT="$REPO/.ai/contracts/20260722-openclaw-dashboard-dezocode/contract.json"
python3 - <<'PY' "$CONTRACT"
import json, sys
c = json.load(open(sys.argv[1]))
ss = c.get("secrets_security")
if not ss:
    raise SystemExit("FAIL contract.json missing secrets_security block")
for k in ("doctrine", "auth_matrix", "settings_panel", "vps_schema", "verify_script"):
    if k not in ss:
        raise SystemExit(f"FAIL secrets_security missing {k}")
print("OK contract.json secrets_security block")
PY

# Scan openclaw-dashboard for obvious secrets
SECRET_FOUND=0
while IFS= read -r f; do
  case "$f" in
    */docs/secrets-security.md|*/docs/auth-matrix.md) continue ;;
  esac
  if grep -qE 'xox[baprs]-[A-Za-z0-9-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' "$f" 2>/dev/null; then
    echo "FAIL possible secret in $f"
    SECRET_FOUND=1
  fi
done < <(find "$ROOT" -type f \( -name '*.json' -o -name '*.md' -o -name '*.sh' -o -name '*.ts' -o -name '*.tsx' -o -name '*.yaml' -o -name '*.yml' \) 2>/dev/null)
if [ "$SECRET_FOUND" -eq 1 ]; then FAIL=1; else echo "OK no secret patterns in product tree"; fi

# auth-matrix must not contain fake token values
if grep -qE 'xox[baprs]-|ghp_|gho_|github_pat_' "$ROOT/docs/auth-matrix.md" 2>/dev/null; then
  echo "FAIL auth-matrix.md contains token-like values"
  FAIL=1
else
  echo "OK auth-matrix has names/status only"
fi

if [ "$FAIL" -ne 0 ]; then
  echo "verify-secrets-compliance.sh: FAILED"
  exit 1
fi
echo "verify-secrets-compliance.sh: OK"
exit 0
