# Verify — SAUL-IDENTITY-001 + live revision callers

## Commands (all exit 0)

- `scripts/saul-attest --self-test` — 22 fixtures (includes
  `signed-rev11-live-pointer-v12`)
- `scripts/sai-blockers --self-test` — 35 fixtures (13 ledger + 22 identity)
- `scripts/invoke-saul-review --self-test` — 30 fixtures
  (`saul-omitted-codex-invoked-blocked` still PASS)
- `scripts/consume-saul-contract-review --self-test` — 3 fixtures
- no `.github/workflows/saul-review.yml`

## Line counts

sai_auth_review.py 500; sai_auth_blockers.py 312;
sai_auth_saul_identity_test.py 233.

SAUL-IDENTITY-001 status IMPLEMENTED_AWAITING_SAUL. Not PASSED.
Did not push.
