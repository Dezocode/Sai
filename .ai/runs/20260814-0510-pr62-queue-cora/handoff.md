# Handoff — Cora A-012 / v12 for PR #62

Consumed qualifying Saul run 31771910025 comment 5289717183 on
exact head `4503f55250efde4166e4877473d4a9268b37c166`:
REQUEST_CHANGES, codex_invoked true, synthetic false, runner
hostinger-saul-codex, contract_revision 11, event
`pull_request`, idempotency_key 08c26942e30d3e7c. Did not run
`scripts/consume-saul-contract-review` (mechanical output would
omit contractor-authorization notes and stale the lease). Recorded
`reviews/consumed-08c26942e30d3e7c.yaml`. Issued immutable
A-012 → v12: remove candidate-controlled Hostinger path from
`saul-review.yml`; trusted default-branch file is the only
self-hosted Saul workflow; job-level `if:` so
`workflow_dispatch` from mutable non-default refs does not
acquire Hostinger. A-011 skip-guard is insufficient (CTO-021
persistent-runner trust boundary, not DEFERRED_NONBLOCKING).
REQUIRED_FOR_CURRENT_BLOCKER, not a waiver, not path expansion.
authority_expanding false. cora_admin_complete true on v12 is
administration complete, not technical PASS. technical_pass false.

Contractor ctr-code-pr62smoke reused. lease-c3a003pr62q1 bumped to
v12. allowed_paths unchanged. denied_paths unchanged. Kept task_id
20260813-2017-pr62-queue-ctr-code and existing task_ids. Did not
edit blockers/ledger.yaml or blockers/items. Did not write
`.ai/authorizations`, decisions, `.cursor`, scripts, workflows,
or `.ai/_config`.

ICM agent-audit SUCCESS on 4503f55 after Saul (31771910146
pull_request, 31771907870 push) is not technical PASS. Cora did
not PASS CTO-030, CTO-031, or CTO-025. CONDITIONAL_PASS_ON_HUMAN_MERGE
is Saul-only.

This commit uses original grant Task-ID
20260813-2016-pr62-queue-cora so authorization PASSES without
HEAD-union and without a contractor HEAD pin. This Cora wave does
not push.

Contractor next (do not PASS): delete or convert
`saul-review.yml` so it cannot acquire Hostinger; keep/harden
`saul-cto-review.default-branch.yml` as the only self-hosted Saul
workflow (`pull_request_target` + job-level `if:` on
`workflow_dispatch`); retarget tests; update
`.ai/_config/authorization.yaml` workflow pointer; append
CTO-030 / CTO-031 blocker items without PASS; optional history
note on CTO-025 that CTO-030 supersedes the skip-guard; update
threat-trace + merge-readiness. Keep CTO-026 uncleared. Do not
rework 015..021/024/028/029. Do not fake trusted file on
origin/main. Do not restore candidate-HEAD trust. Do not add
allow-unsafe-pr-checkout. Do not grow `sai_auth_review.py` or
`sai_auth_test.py`. Do not merge. Do not mark ready.

Last this-PR Hostinger continuity is Saul 31771910025 on 4503f55.
After removing the candidate self-hosted `pull_request` workflow,
this Cloud `gh` cannot `workflow_dispatch` (actions=read / 403).
Post-merge review path is trusted `pull_request_target`. Do not
leave Dezocode a required dispatch chore as the only path.

Cora did not implement. implements false. Do not merge. Do not
push. Do not mark ready. Not a technical PASS.
