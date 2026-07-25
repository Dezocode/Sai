#!/usr/bin/env bash
# subagent-connection-gate-negative.sh — Saul P1 regression (review 4751481118)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
exec "$ROOT/scripts/verify-agent-telegram.sh" --self-test
