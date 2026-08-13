#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
python3 scripts/config_integrity.py
python3 scripts/qualityctl.py init
python3 scripts/phase0_preflight.py
python3 scripts/architecture_guard.py self-test
python3 scripts/toolchain_manager.py detect
python3 scripts/qualityctl.py status
cat <<'EOF'
Phase-0 bootstrap control plane is ready.
Next: python3 scripts/qualityctl.py build --through G03
G04+ is deferred until co-founder approval. Do not pin or install third-party tools.
EOF
