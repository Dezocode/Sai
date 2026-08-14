# Implement — SAUL-IDENTITY-001

Canonical `qualifying_saul_review` in `scripts/lib/sai_auth_saul_identity.py`.
`attempt_clear` no longer treats `actor=="saul"` as PASS. Resume, human_gate,
and consume APPROVE fail closed without Hostinger Ed25519 attestation.
`saul-attest` refuses in-tree keys. Bootstrap exits `NOT_HOSTINGER_SAUL`
unless Hostinger env is set. Trusted workflow signs only if the Hostinger
key file exists; missing key stays unsigned (verifier fail-closed).
Blocker SAUL-IDENTITY-001 is IMPLEMENTED_AWAITING_SAUL, not PASSED.

## Live revision callers (20260814-saul-identity-live-rev)

`attempt_clear` loads the live contract pointer (`doc.contract_id` or
ledger `contract_id` or `20260813-pr62-saul-smoke`) and passes
`revision_int(current_revision)` into `qualifying_saul_review`. Missing
pointer (hermetic tempfile) falls back to the review's own revision.
`consume` qualifies against `a.head_sha(root)` and live `current` before
copying YAML into `reviews/`. Qualify predicates unchanged.
`sai_auth_review.py` stays at 500 lines.
