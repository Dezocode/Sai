# Handoff — Cora A-008 / v8 for PR #62

Consumed qualifying Saul REQUEST_CHANGES run 31761796169
(comment 5288500483) on exact head
f4443fa0b00ec950768ba7aff14020732e338e9d. codex_invoked true,
synthetic false. Issued immutable A-008 → v8 for CTO-028 P0,
CTO-025 P0 (keep open BLOCKED_EXTERNAL), CTO-026 P0 (keep
uncleared), and CTO-027 P1 (icm-enforcement SUCCESS on f4443fa is
not technical PASS). authority_expanding false.
cora_admin_complete true on v8 is administration complete, not
technical PASS.

Contractor ctr-code-pr62smoke reused. lease-c3a003pr62q1 bumped to
v8. allowed_paths unchanged. denied_paths adds
`.ai/authorizations/**` (narrow). Kept task_id
20260813-2017-pr62-queue-ctr-code and existing task_ids. Did not
edit blockers/ledger.yaml or blockers/items. Did not write
`.ai/authorizations` or `.ai/_config`. Did not implement
scripts/workflows.

Officer SHA-bound pins already recorded by Sai at
2a578424f4879f2bad4e4391deff5f30231db19f. Cora did not rewrite them.

This commit uses original grant Task-ID
20260813-2016-pr62-queue-cora so authorization PASSES without
HEAD-union and without a contractor HEAD pin.

Contractor next (do not PASS): remove `_config` pins; verifier
loads only officer records under `.ai/authorizations/`; negative
fixture that a contractor-authored HEAD pin cannot authorize a
historical commit; append CTO-028 item without PASS; keep CTO-025
BLOCKED_EXTERNAL; keep CTO-026 uncleared. Exact-head Saul clearance
still required. Do not restore candidate-HEAD trust. Do not disable
Hostinger pull_request trigger until main has the trusted file.

Cora did not implement. implements false. Do not merge. Do not mark
ready. Not a technical PASS.
