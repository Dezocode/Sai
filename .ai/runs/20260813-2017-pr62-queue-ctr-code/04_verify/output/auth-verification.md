# Verify — authenticity-primary-context

Did not commit, push, merge, or PASS. Fixture keys: openssl tempfile only.

## Commands (all exit 0)

- `scripts/verify-saul-authenticity --self-test` — 18 fixtures
  (14 authenticity + 4 primary; REQUIRED set complete)
- `python3 scripts/lib/sai_auth_primary_context_test.py`
- `python3 scripts/lib/sai_auth_saul_identity_test.py` — historical v1
  qualify fixtures still pass; merge-viable uses v2
- `python3 scripts/lib/sai_auth_resume_test.py` — READY still refuses spoof
- `python3 -m json.tool` on v2 schema

## Fixtures (`SELFTEST PASS  <name>`)

M cursor-fake-saul-bad  
N fake-github-check-bad  
O candidate-key-substitution-bad  
P wrong-public-key-bad  
Q tampered-shard-digest-bad  
R tampered-architecture-digest-bad  
S historical-v1-not-merge-viable-bad  
T exact-state-v2-fixture-good  
unsigned-bad, synthetic-review-bad, codex-not-invoked-bad,
wrong-head-bad, wrong-base-bad, stale-review-bad  
primary-unique-good, primary-none-bad, primary-ambiguous-bad,
primary-no-cross-contam-good

## Line counts (≤500)

attestation_v2.py 370; saul_check.py 155; primary_context.py 170;
primary_context_test.py 137; attestation_v2_test.py 223;
identity.py 321; resume.py 209; identity_test.py 240.

`merge_viable_saul` requires v2. Wrappers executable + comment-refs.
