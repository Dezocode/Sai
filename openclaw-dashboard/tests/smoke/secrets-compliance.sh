#!/usr/bin/env bash
# secrets-compliance.sh — smoke gate for PR #45 secrets control
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
exec "$ROOT/scripts/verify-secrets-compliance.sh"
