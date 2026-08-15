# Implement — authenticity-primary-context

Canonical v2 Ed25519 verifier. `merge_viable_saul` now requires
`attestation.version=2`. Historical v1 still qualifies; never merge-viable.
Check name is evidence, not proof. Primary context fail-closes on 0/>1
active `primary_implementation` without `logical_id`. No production key.
Not PASS. Did not commit/push/merge.

## Files

- `.ai/shared/schemas/saul-attestation-v2.schema.json` — signed field set
- `scripts/lib/sai_auth_saul_attestation_v2.py` — canonical payload + verify
  (`shard_pass_ok` / `architecture_pass_ok` / `technical_clearance_ok` wrap
  the same function)
- `scripts/lib/sai_auth_saul_check.py` — `Saul / Product Quality` surface
- `scripts/lib/sai_auth_primary_context.py` — live git/config resolver
- tests + `scripts/verify-saul-authenticity` + `scripts/saul-publish-check`
- SMALL `sai_auth_saul_identity.py` — merge_viable imports v2 verifier
- SMALL `sai_auth_resume.py` — READY uses same `merge_viable_saul`
- identity test merge-viable path uses `make_signed_review_v2`

Trust: `SAI_SAUL_ATTEST_PUB` or trusted-reviewer tree. Candidate-tree
pub → `CANDIDATE_KEY_SUBSTITUTION`. Missing pub → `TRUST_ANCHOR_UNAVAILABLE`.
