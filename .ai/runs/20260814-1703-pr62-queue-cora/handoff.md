# Handoff — Cora SAUL-IDENTITY-001 reuse of v12

reuse=true. v13=false. lease-c3a003pr62q1. contractor
ctr-code-pr62smoke. contract 20260813-pr62-saul-smoke v12
unchanged. HEAD 11c39ae4443f125a1cf8bd8a49bb04ba49651c3b.

allowed_paths cover qualifying_saul_review(), Ed25519
attestation with fixture test keys, attempt_clear
artifact consume, shared validator, spoof tests,
Hostinger-only bootstrap/attest scripts, and appending
the SAUL-IDENTITY-001 blocker item. denied_paths
unchanged. Production key stays in .ai/authorizations/
(officer/Sai later). Appended REQ-SAUL-IDENTITY-001.
Did not write blockers/items. Did not PASS. implements
false. do_not_merge true. do_not_push true.
technical_pass false.

Contractor next work-item: implement identity attestation
under v12; append blocker DISCOVERED or
IMPLEMENTED_AWAITING_SAUL not PASS. Do not restore
saul-review.yml. Do not write authorizations. Do not
generate a production private key. Do not merge. Do not
mark ready. Only Hostinger Codex with unforgeable
attestation may PASS.
