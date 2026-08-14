# Plan — shard ledger, CTO-021 artifact, A-005 tests

Contract v6, lease `lease-c3a003pr62q1`. Do not merge. Do not self-PASS.

## Current vs desired

- `blockers/ledger.yaml` is 354 lines (yaml bloat 300). Desired: index ≤300 plus `blockers/items/<id>.yaml` for every historical blocker.
- CTO-021 is bound by A-006 but not yet a ledger row. Desired: append P0 IMPLEMENTING then IMPLEMENTED_AWAITING_SAUL after the workflow+test exist. Never PASSED.
- `origin/main` has no `saul-review.yml`. `pull_request_target` on this PR branch is not used by GitHub. Desired: intended default-branch workflow artifact + honest transitional `pull_request` workflow; regression that candidate `saul-review.yml` evil `run:` cannot appear in trusted executed commands.
- A-005: `sai-blockers --clear B-CORA-TODO-001` rejects for cursor/contractor/ctr-admin; `sai-wait` last-resort skip when work-exists digest is provided.

## File changes

- `scripts/lib/sai_auth_blockers.py` (+test): load/save sharded layout; never delete items.
- `blockers/ledger.yaml` + `blockers/items/*.yaml`: shard; append CTO-021, B-BLOAT-001.
- `.github/workflows/saul-cto-review.default-branch.yml`: `pull_request_target` + workflow_dispatch; runner-image or default-branch checkout is the only executable tree; candidate SHA is DATA.
- `.github/workflows/saul-review.yml`: keep `pull_request` transitional; comment CTO-021 open until main activation; no candidate freeze.
- `scripts/verify-saul-workflow-trust` + lib/test; wire CI.
- `scripts/lib/sai_auth_wait.py` (+test): `--work-exists-digest` skips wait with `reason=other_work`.

## Verification

`scripts/sai-blockers --self-test`; `scripts/verify-code-health`; YAML parse; `scripts/verify-saul-workflow-trust --self-test`; `scripts/sai-wait --self-test`; `scripts/invoke-saul-review --self-test` if cheap; `scripts/verify-agent-authorization`.

## Risks

- Do not fake main activation.
- Do not mark CTO-015..020 PASSED (later heads exist; clearance_head must match).
- Parallel Cora/officer dirty trees in this VM must not be staged.
