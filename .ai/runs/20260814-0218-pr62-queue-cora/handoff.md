# Handoff — Cora A-009 / v9 for PR #62

Consumed qualifying Saul REQUEST_CHANGES run 31763018964
(comment 5288630796) on exact head
9382d1fdbf3f878983db8b8beb4ce4bfb83f98b2. codex_invoked true,
synthetic false. Issued immutable A-009 → v9 for CTO-029 P0,
CTO-025 P0 (keep open BLOCKED_EXTERNAL), CTO-026 P0 (keep
uncleared), and CTO-027 P1 (icm-enforcement SUCCESS on 9382d1f is
not technical PASS). authority_expanding false.
cora_admin_complete true on v9 is administration complete, not
technical PASS.

Contractor ctr-code-pr62smoke reused. lease-c3a003pr62q1 bumped to
v9. allowed_paths unchanged. denied_paths unchanged. Kept task_id
20260813-2017-pr62-queue-ctr-code and existing task_ids. Did not
edit blockers/ledger.yaml or blockers/items. Did not write
`.ai/authorizations` or `.ai/_config`. Did not implement
scripts/workflows.

Officer pin provenance already landed at
e84e5d7a7e76c5f9da567c8b8df9d75e9d4cb087
(introduced_by_sha=2a57842, source_head=9382d1f). Cora did not
rewrite that tree.

This commit uses original grant Task-ID
20260813-2016-pr62-queue-cora so authorization PASSES without
HEAD-union and without a contractor HEAD pin.

Contractor next (do not PASS): enforce pin provenance in
`sha_bound_rows()` — validate the pin was introduced by an
independently authorized officer commit; bind approval source and
issuer grant immutably; do not accept a HEAD pin merely because
issuer is officer and issuer_grant matches the HEAD grant;
negative fixtures that forged metadata or a later rewritten HEAD
grant cannot retrospectively authorize a historical commit; append
CTO-029 item without PASS; keep CTO-025 BLOCKED_EXTERNAL; keep
CTO-026 uncleared. Exact-head Saul clearance still required. Do
not restore candidate-HEAD trust. Do not disable Hostinger
pull_request trigger until main has the trusted file.

Cora did not implement. implements false. Do not merge. Do not mark
ready. Not a technical PASS.
