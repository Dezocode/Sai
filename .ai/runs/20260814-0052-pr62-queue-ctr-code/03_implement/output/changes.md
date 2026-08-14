# Implement — shard + CTO-021 artifact

- Sharded `blockers/ledger.yaml` to policy+index (40 lines) and `blockers/items/<id>.yaml` for B-TRUST-001 through CTO-020 plus B-CORA-TODO-001, B-RALPH-001, B-NO-IDLE-SAUL-001, CTO-021, B-BLOAT-001.
- Loader/save in `scripts/lib/sai_auth_blockers.py` never deletes item files.
- Appended CTO-021 (P0, Saul, IMPLEMENTED_AWAITING_SAUL) and B-BLOAT-001 (PROVISIONAL, IMPLEMENTED_AWAITING_SAUL). Did not mark CTO-015..020 PASSED.
- Added intended default-branch workflow `saul-cto-review.default-branch.yml` (`pull_request_target`, candidate as DATA). Kept transitional `pull_request` on `saul-review.yml`.
- Added `scripts/verify-saul-workflow-trust` with negative fixture (evil candidate `run:` does not appear in trusted commands).
- A-005: live `--clear B-CORA-TODO-001` rejects cursor/contractor/ctr-admin; `sai-wait --work-exists-digest` skips with `reason=other_work`.
