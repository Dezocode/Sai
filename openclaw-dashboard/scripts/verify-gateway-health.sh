#!/usr/bin/env bash
# verify-gateway-health.sh — A0 Gateway health gate (loopback only)
#
# Usage:
#   verify-gateway-health.sh [--port 18789] [--self-test]
#
# Exit 0 when OpenClaw Gateway responds on 127.0.0.1 (HTTP probe or openclaw doctor).
# Exit 1 when Gateway unreachable — start per vps-bootstrap.md before re-run.
set -euo pipefail

PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
HOST="127.0.0.1"

while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="${2:-18789}"; shift 2;;
    --self-test)
      bash -n "$0"
      echo "verify-gateway-health.sh --self-test: PASS"
      exit 0
      ;;
    -h|--help)
      echo "Usage: verify-gateway-health.sh [--port PORT] [--self-test]"
      exit 0
      ;;
    *) echo "verify-gateway-health.sh: unknown option $1" >&2; exit 2;;
  esac
done

if ! command -v openclaw >/dev/null 2>&1; then
  echo "verify-gateway-health.sh: FAIL — openclaw CLI not in PATH" >&2
  echo "  Remediation: npm install -g openclaw@latest && openclaw onboard" >&2
  exit 1
fi

# Prefer openclaw doctor when available (records structured health)
if openclaw doctor >/tmp/openclaw-doctor.out 2>&1; then
  echo "verify-gateway-health.sh: PASS (openclaw doctor)"
  exit 0
fi

# Fallback: loopback HTTP probe (Gateway may expose root or health)
for path in "/" "/health" "/api/health"; do
  if curl -sf --max-time 3 "http://${HOST}:${PORT}${path}" >/dev/null 2>&1; then
    echo "verify-gateway-health.sh: PASS (HTTP ${HOST}:${PORT}${path})"
    exit 0
  fi
done

echo "verify-gateway-health.sh: FAIL — Gateway not healthy on ${HOST}:${PORT}" >&2
echo "  Start: openclaw gateway --host 127.0.0.1 --port ${PORT}" >&2
echo "  Guide: openclaw-dashboard/docs/vps-bootstrap.md" >&2
if [ -f /tmp/openclaw-doctor.out ]; then
  echo "  openclaw doctor output:" >&2
  tail -20 /tmp/openclaw-doctor.out >&2 || true
fi
exit 1
