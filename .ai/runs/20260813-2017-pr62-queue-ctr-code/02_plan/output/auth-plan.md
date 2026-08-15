# Plan — authenticity-primary-context (PR #62 slice)

Contractor `ctr-code-pr62smoke`. Standing run
`20260813-2017-pr62-queue-ctr-code`. Lease `lease-c3a003pr62q1`.
v12 reuse. Do not PASS, commit, push, merge, write
`.ai/authorizations/**`, or generate a production Saul key.

## Current vs desired

`qualifying_saul_review` is historical v1 (HEAD + revision + Ed25519).
`merge_viable_saul` currently treats any qualifying APPROVE as
merge-viable. GitHub Check name and actor strings are spoofable.
Primary program selection is not fail-closed for 0/>1 active
`primary_implementation` rows.

Desired: attestation **v2** canonical payload binds version, alg,
key_id, repository, PR/program, contract, revision, base, head,
diff, review type/scope, shard/architecture digests, findings,
disposition, `codex_invoked=true`, `synthetic=false`, review_id,
timestamp. One verifier (`verify_attestation_v2`) is the merge-viable
/ READY / shard / architecture / blocker-clearance primitive.
Trust anchor from `SAI_SAUL_ATTEST_PUB` or trusted-reviewer tree —
never candidate HEAD. Missing production pub → fail closed.
Check `Saul / Product Quality` is evidence surface, not proof.
Primary context: unique active `primary_implementation` or explicit
`logical_id`; else `NO_PRIMARY_CONTEXT` / `AMBIGUOUS_PRIMARY_CONTEXT`.
No hardcoded PR/contract/branch/SHA in reusable production code.

## File changes (exclusive)

- NEW schema `saul-attestation-v2.schema.json`
- NEW `sai_auth_saul_attestation_v2.py` — payload + verify
- NEW `sai_auth_saul_check.py` — Check evidence, not proof
- NEW `sai_auth_primary_context.py` + tests
- NEW `sai_auth_saul_attestation_v2_test.py` — lettered fixtures
- NEW `scripts/verify-saul-authenticity`, `scripts/saul-publish-check`
- SMALL `sai_auth_saul_identity.py` — `merge_viable_saul` requires
  `attestation.version=2` via v2 verifier; v1 still `qualifying`
- SMALL `sai_auth_resume.py` — READY uses same `merge_viable_saul`
- SMALL identity test: merge-viable path uses a v2 fixture

Denied this slice: workflows, code-health, shard/architecture
modules, `sai_auth_review.py`, authorizations, production keys.

## Verify

`scripts/verify-saul-authenticity --self-test`
`python3 scripts/lib/sai_auth_primary_context_test.py`
`python3 scripts/lib/sai_auth_saul_identity_test.py`
Line limits ≤500. Wrappers `chmod +x` + orphan comment-refs.
Not PASS.
