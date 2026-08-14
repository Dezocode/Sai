# Plan — Cora A-009 / v9 for PR #62

Qualifying Saul run 31763018964 (comment 5288630796) on exact head
`9382d1fdbf3f878983db8b8beb4ce4bfb83f98b2` is REQUEST_CHANGES,
codex_invoked true, synthetic false. Contract revision reviewed: v8.
authority_expanding false on every finding.

Issue immutable A-009 → v9 (copy v8 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand allowed_paths.
denied_paths unchanged (keep `.ai/authorizations/**`). Bump lease +
contract.json to v9 only. Keep lease.task_id
`20260813-2017-pr62-queue-ctr-code` and existing task_ids.

This commit uses original grant Task-ID `20260813-2016-pr62-queue-cora`
so authorization PASSES without HEAD-union and without a contractor
HEAD pin.

Officer pin file already exists at
`2a578424f4879f2bad4e4391deff5f30231db19f`
(`.ai/authorizations/sha-bound-authorization.yaml`). After intake,
Sai bound `introduced_by_sha` / `source` / `source_head` at
`e84e5d7a7e76c5f9da567c8b8df9d75e9d4cb087`. Cora does not write
`.ai/authorizations` or `.ai/_config`. Contractor enforces
provenance in `sha_bound_rows()`.

Findings bound, not PASSED:

- CTO-029 P0 authorization narrow: complete CTO-028 provenance.
  `sha_bound_rows()` currently accepts a HEAD pin when issuer names
  an officer and issuer_grant names a HEAD grant for that principal;
  it ignores approved_by, source, source_head, and the commit that
  introduced the pin. Validate the pin was introduced by an
  independently authorized officer commit; bind approval source and
  issuer grant immutably. Negative fixtures: forged metadata or a
  later rewritten HEAD grant cannot retrospectively authorize a
  historical commit.
- CTO-025 P0 saul_review_workflow: keep open BLOCKED_EXTERNAL.
  origin/main still lacks the trusted pull_request_target workflow.
  PR artifact is not activation.
- CTO-026 P0 verification: keep uncleared. Exact-head Saul clearance
  still required. B-RALPH-001 cannot pass while CTO-025 and CTO-029
  remain. Implementation/self-tests are not clearance.
- CTO-027 P1 human_gate: icm-enforcement already SUCCESS on 9382d1f
  (agent-audit 31763018953 / 31763016803). That is not technical PASS.
  After issuing A-009/v9, set cora_admin_complete true
  (administration complete only).

Contractor work (Cora does not implement): enforce pin provenance in
the verifier; negative fixtures for forged metadata and rewritten
HEAD grant; append CTO-029 blocker item without PASS; do not clear
CTO-025/026/027.

Officer work already landed at e84e5d7 (Cora does not rewrite):
`introduced_by_sha` / `source` / `source_head` on the pin file.

Do not write blockers/ledger or blockers/items. Do not implement
scripts/workflows/decisions/.cursor. Do not write authorizations pins.
Do not PASS technical blockers. Do not merge. Do not restore
candidate-HEAD trust.
