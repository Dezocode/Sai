#!/usr/bin/env bash
# verify-ingest-latency — contract gate: host CLI → dashboard p99 <= 15ms
#
# Usage: verify-ingest-latency [--samples N] [--slo-ms N]
# Exit 0 when p99 latency <= SLO (default 15ms).
# Stub until activity-ingest service exists — exits 2 with message.
set -euo pipefail

SLO_MS=15
SAMPLES=1000

while [ $# -gt 0 ]; do
  case $1 in
    --slo-ms) SLO_MS=$2; shift 2;;
    --samples) SAMPLES=$2; shift 2;;
    *) echo "verify-ingest-latency: unknown option $1" >&2; exit 2;;
  esac
done

echo "verify-ingest-latency: STUB — activity-ingest service not implemented yet" >&2
echo "  Required: p99 <= ${SLO_MS}ms over ${SAMPLES} synthetic events (dezocode org onboarding gate)" >&2
echo "  Implement: openclaw-dashboard/services/activity-ingest/" >&2
exit 2
