# Plan — Cora A-008 / v8 for PR #62

Qualifying Saul run 31761796169 (comment 5288500483) on exact head
`f4443fa0b00ec950768ba7aff14020732e338e9d` is REQUEST_CHANGES,
codex_invoked true, synthetic false. Contract revision reviewed: v7.
authority_expanding false on every finding.

Issue immutable A-008 → v8 (copy v7 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand allowed_paths.
Add denied_paths `.ai/authorizations/**` (narrow; contractor already
lacks it in allowed_paths). Bump lease + contract.json to v8 only.
Keep lease.task_id `20260813-2017-pr62-queue-ctr-code` and existing
task_ids.

This commit uses original grant Task-ID `20260813-2016-pr62-queue-cora`
so authorization PASSES without HEAD-union and without a contractor
HEAD pin.

Officer work already landed at `2a578424f4879f2bad4e4391deff5f30231db19f`
(`.ai/authorizations/sha-bound-authorization.yaml`). Cora does not
write `.ai/authorizations` or `.ai/_config`. Contractor removes
`_config` pins and makes the verifier load only officer records.

Findings bound, not PASSED:

- CTO-028 P0 authorization narrow: contractor-authored
  sha_bound_authorization rows in `.ai/_config` are invalid because
  this contractor can write `_config`. Pins must live in
  contractor-DENIED independently approved records with
  issuer/source/provenance. Negative: a contractor HEAD pin cannot
  authorize a historical commit.
- CTO-025 P0 saul_review_workflow: keep open BLOCKED_EXTERNAL.
  origin/main still lacks the trusted pull_request_target workflow.
  PR artifact is not activation.
- CTO-026 P0 verification: keep uncleared. Exact-head Saul clearance
  still required. B-RALPH-001 cannot pass while CTO-025 and CTO-028
  remain. Implementation/self-tests are not clearance.
- CTO-027 P1 human_gate: icm-enforcement already SUCCESS on f4443fa
  (agent-audit 31761796108 / 31761793891). That is not technical PASS.
  After issuing A-008/v8, set cora_admin_complete true
  (administration complete only).

Contractor work (Cora does not implement): remove `_config` pins;
verifier loads only officer records under `.ai/authorizations/`;
negative fixture that a contractor-authored HEAD pin cannot authorize
a historical commit; append CTO-028 blocker item without PASS; do not
clear CTO-025/026/027.

Do not write blockers/ledger or blockers/items. Do not implement
scripts/workflows/decisions/.cursor. Do not PASS technical blockers.
Do not merge. Do not restore candidate-HEAD trust.
