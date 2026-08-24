# Handoff — Round-20 per-row sai-sessions-v2 validation (PR 77)

## What changed
- /prs feed: rows failing required fields (id/status/heartbeat_at) drop
  individually via rowValid(); valid rows survive; feed falls back to
  /sessions only when EVERY row is invalid (nothing invented).
- Sessions plane: invalid rows render as named honesty badges
  (invalidRow()) listing the missing fields — never rendered as live workers.
- client-side shortSha for session head cells.
- --check needles updated to assert rowValid/invalidRow invariants;
  agentOk alias removed (zero callers).

## Verification at authoring time
py_compile OK; --selftest ALL PASS; --check ALL PASS features=11 with
prs-probe (badrow + null-metrics cases); node --check clean; hierarchy OK.

## Next
CI + real-Codex Saul re-bind on pushed HEAD; stay draft.
