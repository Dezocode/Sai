# Handoff — 20260824-0620-pr77-saul-p1-close-ox-alpha

## What changed - planEnrich: checks-step condition uses cprobe (CHECKS_RETRY_AT window) not the detail-path probe — capped checks now replan after backoff expiry (Saul 97338826287 P1-1). - loadPrs: fbc[pk] telemetry stored only AFTER whole-group validation (vc>0) — an all-invalid group's flightboard can never publish via a valid sibling (Saul 97338826287 P1-2). - Selftest locks: invalid-group-fli
