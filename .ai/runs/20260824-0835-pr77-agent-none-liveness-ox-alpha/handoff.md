# Handoff — 20260824-0835-pr77-agent-none-liveness-ox-alpha

## What changed
- First run of the upgraded acceptance-contract engine flagged a real regression: C-04 windowing made successful-/prs polls leave SESSIONS_TS unset, so sessionless PRs rendered Agent UNKNOWN instead of Agent NONE.
- Fix: successful preferred-/prs load touches SESSIONS_TS (same backend serves both planes — success is liveness evidence). Unreachable plane still never authorizes Agent NONE (C-04 invariant kept).
- docs/pages-pr-sessions/README condensed (planner steps wording); line budget restored.

## Verification
py_compile OK; --selftest ALL PASS; --check ALL PASS features=11 + prs-probe.
