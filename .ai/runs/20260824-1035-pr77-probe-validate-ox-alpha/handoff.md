# Handoff — 20260824-1035-pr77-probe-validate-ox-alpha

probeSessions() no longer treats bare HTTP-200 as liveness: the response must parse as JSON with schema sai-sessions-v2 and a sessions array. Selftest locks: malformed-schema 200 leaves SESSIONS_TS untouched; valid envelope updates it. Gates ALL PASS.
