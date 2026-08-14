# Plan — Cora A-010 / v10 for PR #62

Principal P0 comment 5289020312 (Dezocode, 2026-08-14T03:21:41Z)
is append-only overnight-convergence instruction. Not a Saul
consume. Do not run `scripts/consume-saul-contract-review`.

Latest qualifying Saul on current HEAD
`c51c9cf221a8f4682e2c9e2287bd06d550c6c44e`: run 31764010391,
REQUEST_CHANGES. CTO-025 still BLOCKED_EXTERNAL. CTO-026 uncleared.
CTO-027 icm-enforcement SUCCESS on c51c9cf is not technical PASS.
Do not rework IMPLEMENTED_AWAITING_SAUL items.

Issue immutable A-010 → v10 (copy v9 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand
allowed_paths. denied_paths unchanged. Bump lease + contract.json
to v10 only. Keep lease.task_id `20260813-2017-pr62-queue-ctr-code`
and existing task_ids.

This commit uses original grant Task-ID `20260813-2016-pr62-queue-cora`
so authorization PASSES without HEAD-union and without a contractor
HEAD pin.

Findings bound, not PASSED:

- REQ-5289020312 / B-META-P0-001: principal meta-P0 cannot pass
  from documentation alone. Saul clears it last after quality
  profile, independent P0/P1 Saul-cleared or legitimately
  merge-conditional, architectural review, trust boundaries, CI
  green, transitional path merge-time retirement, no ballooning,
  merge package complete, then Sai on same state.
- CTO-025 REASSESS: authorize merge-activation design in THIS PR.
  Harden trusted `pull_request_target` artifact; retire candidate
  `pull_request` trigger in the same merge SHA; keep
  `workflow_dispatch`; replace `transitional-pr-trigger-kept`
  fixture; threat trace; do not PASS. Saul may classify
  CONDITIONAL_PASS_ON_HUMAN_MERGE. Cora/contractor must not emit
  that as clearance. Obsolete "HUMAN MUST LAND THIS FIRST as a
  separate PR" is no longer the only allowed remediation.
- Architectural Saul plane: compact candidate-packaged files under
  the contract tree; copy via `sai_auth_package.py` only. Do not
  grow `sai_auth_review.py`. Do not rewrite `.ai/agents/saul/**`.
- Quality profile REQUIRED_FOR_FINAL_MERGE_QUALITY under contract
  tree. Do not claim an SLSA level. Uninspectable repo settings
  are UNKNOWN/VERIFY_REQUIRED, not fabricated PASS.
- Anti-bloat: warning/triage policy in `.ai/_config` (contractor).
  Classify REQUIRED_FOR_CURRENT_BLOCKER |
  REQUIRED_FOR_FINAL_MERGE_QUALITY | DEFER_TO_FOLLOWUP.
- Merge-readiness package under contract tree. Do not merge. Do
  not mark ready.
- Officer (Sai, not Cora): amend Decision 0008 in place (no 0009)
  + small `.cursor/rules/sai-orchestration.mdc` pointer.
- Keep CTO-026 uncleared. Keep CTO-015..021, 024, 028, 029
  IMPLEMENTED_AWAITING_SAUL. CTO-027 SUCCESS is not technical PASS.

Cora does not implement. Cora does not write blockers items,
scripts, workflows, tests, decisions, `.cursor`, or
`.ai/authorizations`. YAML ≤300 lines. Do not restore
candidate-HEAD trust. Do not merge.

Files claimed: A-010.yaml, v10.yaml, contract.json, lease
(revision bump only), requirements/ledger.yaml (append
REQ-5289020312), optional principal review receipt, this run
directory, standing-run handoff append.
