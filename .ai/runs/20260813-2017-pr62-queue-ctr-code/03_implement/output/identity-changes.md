# Implement — SAUL-IDENTITY-001

Canonical `qualifying_saul_review` in `scripts/lib/sai_auth_saul_identity.py`.
`attempt_clear` no longer treats `actor=="saul"` as PASS. Resume, human_gate,
and consume APPROVE fail closed without Hostinger Ed25519 attestation.
`saul-attest` refuses in-tree keys. Bootstrap exits `NOT_HOSTINGER_SAUL`
unless Hostinger env is set. Trusted workflow signs only if the Hostinger
key file exists; missing key stays unsigned (verifier fail-closed).
Blocker SAUL-IDENTITY-001 is IMPLEMENTED_AWAITING_SAUL, not PASSED.
