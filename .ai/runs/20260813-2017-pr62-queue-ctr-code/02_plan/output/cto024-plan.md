# Plan — CTO-024 SHA-bound authorization (not HEAD-union)

Qualifying Saul run 31760665414 / comment 5288363871 / head
`5ad0b94035182bf088715dd36b95db14fc496a98` rejected retrospective
HEAD/working-tree `task_ids` union in `matching_grant` /
`lease_task_id_bound`.

## Current vs desired

Current: commit-time grant/lease plus a union of HEAD and working-tree
`task_id`/`task_ids` for the same grant/lease id. That lets later or
even staged aliases authorize older SHAs.

Desired: replay uses only immutable authorization at that commit, plus
SHA-bound remediation rows loaded from `git show HEAD:.ai/_config/authorization.yaml`
(never the dirty working tree).

## Changes

- `scripts/lib/sai_auth_grant.py`: remove HEAD/working-tree alias union.
  Add `sha_bound_task_ids()` from committed HEAD only.
- `.ai/_config/authorization.yaml`: pin wave SHAs that used 0041/0052
  Task-IDs before aliases existed. Do not pin 5ad0b94 / 7b03b97 / 5684304.
- `scripts/lib/sai_auth_rebind_test.py`: six negative/positive fixtures.
- `scripts/verify-agent-authorization`: filename reference so ICM orphans PASS.
- Blocker items CTO-024..027 (append only). CTO-024 ends
  IMPLEMENTED_AWAITING_SAUL. CTO-025 BLOCKED_EXTERNAL. Do not disable
  candidate `saul-review.yml` pull_request job. Do not PASS.

Cora owns A-007/v7 (untracked). This contractor commit stays on v6
trailers until v7 is pushed. Do not edit grants, decisions, `.cursor`,
`contract.json`, or the lease.

## Verification

`verify-agent-authorization --self-test`, `origin/main..HEAD`,
`verify-code-health`, `sai-blockers --self-test`,
`invoke-saul-review --self-test` if cheap.

`self_pass: false`. `do_not_merge: true`.
