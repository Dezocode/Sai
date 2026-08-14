# Handoff — Cora A-004 / v4 for PR #62

Ingested Saul run 31756720206 (comment 5287885648), disposition
REQUEST_CHANGES, codex_invoked true, synthetic false.

CTO-016: contractor denied_paths unchanged. Officer decisions stay under
grant-pr62-queue-ceo. Restored `.ai/agents/saul` to origin/main so the
candidate PR does not redefine the trusted Saul persona.

Did not technically PASS any blocker. Did not implement CTO-015/017/018.
Do not merge.

2026-08-14: Aliased contractor wave Task-ID on lease-c3a003pr62q1 without
changing paths, agent, status, or v6. Kept task_id
20260813-2017-pr62-queue-ctr-code and added task_ids including
20260814-0052-pr62-queue-ctr-code so HEAD can union the wave. Did not
mark cora_admin_complete. Did not PASS blockers. Do not merge.

## A-008 / v8 (grant Task-ID standing run)

Issued A-008 → v8 from Saul run 31761796169 comment 5288500483 on
exact head f4443fa. cora_admin_complete true is administration
complete, not technical PASS. Wave artifacts:
`.ai/runs/20260814-0158-pr62-queue-cora/`. implements false.
do_not_merge true.

## A-009 / v9 (grant Task-ID standing run)

Issued A-009 → v9 from Saul run 31763018964 comment 5288630796 on
exact head 9382d1f. cora_admin_complete true is administration
complete, not technical PASS. Wave artifacts:
`.ai/runs/20260814-0218-pr62-queue-cora/`. implements false.
do_not_merge true. denied_paths unchanged. Officer pin provenance
already at e84e5d7; contractor enforces verifier provenance.

## A-010 / v10 (grant Task-ID standing run)

Issued A-010 → v10 from principal P0 comment 5289020312
(Dezocode, 2026-08-14T03:21:41Z). Not a Saul consume. Latest
qualifying Saul on c51c9cf: run 31764010391 REQUEST_CHANGES.
cora_admin_complete true is administration complete, not
technical PASS. technical_pass false. Did not PASS CTO-025.
Wave artifacts: `.ai/runs/20260814-0415-pr62-queue-cora/`.
implements false. do_not_merge true. denied_paths unchanged.
lease-c3a003pr62q1 reused. Contractor next: merge-activation
design, quality profile, architectural package, anti-bloat,
merge package; append B-META-P0-001 / B-QUALITY-001 /
B-MERGE-PKG-001 without PASS. Officer next: Decision 0008 in
place + orchestration pointer. CONDITIONAL_PASS_ON_HUMAN_MERGE
is Saul-only. Do not merge. Do not mark ready.

## A-011 / v11 (grant Task-ID standing run)

Issued A-011 → v11 from operational evidence on exact head
6ad1dc6: Cloud gh workflow_dispatch HTTP 403; accepted
permissions actions=read; no Saul run on 6ad1dc6; ICM
agent-audit SUCCESS 31770830268/31770828271. Not a Saul
consume. Not a waiver. Not path expansion.
cora_admin_complete true is administration complete, not
technical PASS. technical_pass false. Did not PASS CTO-025
or B-META-P0-001. Wave artifacts:
`.ai/runs/20260814-0448-pr62-queue-cora/`. implements false.
do_not_merge true. do_not_push true. denied_paths unchanged.
lease-c3a003pr62q1 reused (v11). Contractor next: restore
narrow pull_request plus post-merge skip-guard
TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN; keep workflow_dispatch;
replace candidate-pr-trigger-retired; hermetic skip-guard
fixture; update threat-trace + merge-readiness. Officer
optional: one-sentence Decision 0008 note (Sai, not Cora).
CONDITIONAL_PASS_ON_HUMAN_MERGE is Saul-only. Do not merge.
Do not push. Do not mark ready.

## A-012 / v12 (grant Task-ID standing run)

Issued A-012 → v12 from Saul run 31771910025 comment
5289717183 on exact head 4503f55. REQUEST_CHANGES,
codex_invoked true, synthetic false, runner
hostinger-saul-codex, contract_revision 11.
cora_admin_complete true is administration
complete, not technical PASS. technical_pass false.
Did not PASS CTO-030, CTO-031, or CTO-025.
Wave artifacts:
`.ai/runs/20260814-0510-pr62-queue-cora/`. implements false.
do_not_merge true. do_not_push true. denied_paths unchanged.
lease-c3a003pr62q1 reused (v12). consume_script_invoked false
(mechanical consume would omit contractor notes and stale the
lease). Contractor next: remove candidate self-hosted
saul-review.yml Hostinger path; keep/harden trusted
default-branch file as the only self-hosted Saul workflow
with job-level if: on workflow_dispatch; retarget tests;
update authorization.yaml pointer; append CTO-030/CTO-031
items without PASS; threat-trace + merge-readiness.
CTO-025 may stay IMPLEMENTED_AWAITING_SAUL with a history
note that CTO-030 supersedes the skip-guard. Keep CTO-026
uncleared. Last this-PR Hostinger continuity is Saul
31771910025 on 4503f55; post-merge path is trusted
pull_request_target. CONDITIONAL_PASS_ON_HUMAN_MERGE is
Saul-only. Do not merge. Do not push. Do not mark ready.

## TPR-001 / TPR-002 reuse v12 (grant Task-ID standing run)

Evaluated independent third-party findings on exact head
01fe606. reuse=true. v13=false. Did not issue A-013.
allowed_paths already cover both remediations
(.github/workflows/**, scripts/**, tests/**, contract
tree). denied_paths unchanged. lease-c3a003pr62q1 reused
(v12). ctr-code-pr62smoke reused. Appended REQ-TPR-001 /
REQ-TPR-002 without PASS. Did not write blockers/items.
Wave artifacts: `.ai/runs/20260814-1536-pr62-queue-cora/`.
implements false. do_not_merge true. do_not_push true.
technical_pass false. Contractor next: write TPR-001 /
TPR-002 blocker items without PASS, then delete
trusted-reviewer-provision.yml, stop sai_auth_wait poll,
default Codex sandbox workspace-write or read-only, strip
GITHUB_TOKEN/GH_TOKEN/SSH_AUTH_SOCK/DOCKER_HOST from Codex
subprocess and Invoke Codex env, in-place sai_auth_review.py
(no net lines), retarget danger-full-access assertion.
Do not restore saul-review.yml. Do not PASS. Do not merge.
Do not push. Do not mark ready.


