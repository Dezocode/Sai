# Handoff — 20260824-0945-pr77-honest-liveness-ox-alpha

## What changed
- Removed if(SRC==="prs")SESSIONS_TS=Date.now() — /prs success faked sessions-plane liveness and could mask a dead /sessions endpoint behind Agent NONE (Saul 97376638286 acceptance FAIL).
- probeSessions() GETs SESSIONS_URL every load cycle and is now the ONLY liveness evidence: real /sessions OK -> Agent NONE for sessionless PRs; dead plane -> UNKNOWN/unavailable. C-04 invariant preserved with corrected rationale.

## Verification
py_compile OK; --selftest ALL PASS; --check ALL PASS features=11 + prs-probe; additions within budget.
