# Plan — Cora A-007 / v7 for PR #62

Qualifying Saul run 31760665414 (comment 5288363871) on exact head
5ad0b94035182bf088715dd36b95db14fc496a98 is REQUEST_CHANGES,
codex_invoked true, synthetic false. Contract revision reviewed: v6.
authority_expanding false on every finding.

Issue immutable A-007 → v7 (copy v6 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand allowed_paths.
Do not change denied_paths. Bump lease + contract.json to v7 only.
Keep lease.task_id 20260813-2017-pr62-queue-ctr-code and existing
task_ids. No path expansion.

This commit uses original grant Task-ID 20260813-2016-pr62-queue-cora
so authorization PASSES without HEAD-union. Saul rejected HEAD-union
as CTO-024.

Findings bound, not PASSED:

- CTO-024 P0 authorization narrow: REMOVE retrospective HEAD/working-tree
  task_id aliasing. Auth replay must use immutable auth at that commit OR
  an independently approved SHA-bound remediation record. Negative fixtures:
  uncommitted and later-HEAD aliases cannot alter historical authorization.
- CTO-025 P0 saul_review_workflow: CTO-021 still open. origin/main lacks
  trusted pull_request_target workflow. Transitional saul-review.yml still
  candidate-sourced on the persistent runner. Land+human-review trusted
  workflow on default branch, then disable candidate persistent-runner
  workflow. Artifact on this PR is not activation. Activation = human merge
  to main (security gate). Do not tell contractor to disable Hostinger
  pull_request trigger until main has the trusted file.
- CTO-026 P0 verification: exact-head Saul clearance still required for
  CTO-015..021 and B-CORA-TODO/RALPH/NO-IDLE. Do not treat older-head
  remediation as clearance.
- CTO-027 P1 human_gate: after A-007/v7, set cora_admin_complete: true.
  That is administration complete, NOT technical PASS.

Contractor work (Cora does not implement): SHA-bound auth records; revert
HEAD-union; orphan fix sai_auth_rebind_test.py; append CTO-024..027 items.
Officer: none required unless grants need a note.

Do not write blockers/ledger. Do not implement scripts/workflows/decisions/.cursor.
Do not PASS technical blockers. Do not merge. Do not restore candidate-HEAD trust.
