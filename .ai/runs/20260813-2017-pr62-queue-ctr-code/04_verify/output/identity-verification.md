# Verify — SAUL-IDENTITY-001

## Commands (all exit 0)

- `scripts/saul-attest --self-test` — 21 fixtures
- `scripts/sai-blockers --self-test` — 34 fixtures (13 ledger + 21 identity)
- `scripts/invoke-saul-review --self-test` — 30 fixtures
- `scripts/verify-saul-workflow-trust --self-test` — 14 fixtures
- `scripts/sai-resume --self-test` — 8 fixtures (spoof cursor Saul does not exit)
- `scripts/verify-agent-authorization --self-test` — PASS (negative FAIL lines expected)
- `scripts/verify-agent-authorization -n 5 HEAD` — PASS
- `scripts/consume-saul-contract-review --self-test` — 3 fixtures
- `scripts/sai-blockers --clear B-CORA-TODO-001 --actor saul --review-id x --head <sha>`
  → `REJECT INVALID_SAUL_IDENTITY`
- no `.github/workflows/saul-review.yml`
- `git grep actor == .saul scripts/lib/sai_auth_blockers.py` — CLI reject only, not PASS
- no tracked `.pem` / production attestation key

## Line counts

sai_auth_review.py 500; sai_auth_test.py 497; sai_auth_verify.py 458;
sai_auth_blockers.py 302; sai_auth_saul_identity.py 307;
sai_auth_saul_identity_test.py 216; agent-audit.yml 184;
saul-cto-review.default-branch.yml 270; ledger.yaml 68.

SAUL-IDENTITY-001 status IMPLEMENTED_AWAITING_SAUL. Not PASSED.
