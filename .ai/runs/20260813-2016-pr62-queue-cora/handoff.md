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

## Saul quality loop P0 reuse v12 (grant Task-ID standing run)

Evaluated B-SAUL-QUALITY-LOOP-001 / REQ-5300146420 and
AUTHENTICATION.md / REQ-5300187244 on exact head
516893c. reuse=true. v13=false. Did not issue A-013.
allowed_paths already cover executable machinery
(scripts/**, tests/**, .github/workflows/**,
.ai/_config/**, .ai/shared/schemas/**). Quality docs
under .ai/shared/quality/** are officer read-only spec;
contractors must not rewrite them. Pubkey pin is
officer/Hostinger (`.ai/authorizations/**` denied).
denied_paths unchanged. lease-c3a003pr62q1 reused (v12).
ctr-code-pr62smoke reused. Appended REQ-5300187244;
REQ-5300146420 already present. Did not write
blockers/items. Wave artifacts:
`.ai/runs/20260815-0302-pr62-queue-cora/`. Admin review:
`reviews/cora-saul-quality-loop-v12-reuse.yaml`.
implements false. do_not_merge true. do_not_push true.
technical_pass false. code-health.yaml 321>300 fails
icm-enforcement; contractor may split/include under
_config only. Contractor next: four disjoint slices
(sha-shard, architecture, authenticity-primary-context,
finding-ci-detectors-bloat) without PASS. Do not rewrite
quality docs. Do not write authorizations. Do not PASS.
Do not merge. Do not push. Do not mark ready.

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

## SAUL-IDENTITY-001 reuse v12 (grant Task-ID standing run)

Evaluated P0 SAUL-IDENTITY-001 on exact head 11c39ae.
Principal VOIDED Cursor-named-subagent Saul APPROVE
(codex_invoked=false); that false projection is historical
evidence, not deleted. reuse=true. v13=false. Did not
issue A-013. allowed_paths already cover identity work
(scripts/**, tests/**, contract tree, schemas). denied_paths
unchanged (.ai/authorizations/** remains officer-only).
lease-c3a003pr62q1 reused (v12). ctr-code-pr62smoke reused.
Appended REQ-SAUL-IDENTITY-001 without PASS. Did not write
blockers/items. Wave artifacts:
`.ai/runs/20260814-1703-pr62-queue-cora/`. implements false.
do_not_merge true. do_not_push true. technical_pass false.
Contractor next: canonical qualifying_saul_review() +
Ed25519 attestation (openssl; test keys in fixtures only);
attempt_clear consumes review artifact not --actor saul;
resume/human_gate/consume share the validator; negative
spoof tests; Hostinger-only bootstrap/attest scripts;
append SAUL-IDENTITY-001 blocker DISCOVERED or
IMPLEMENTED_AWAITING_SAUL not PASS. Do not restore
saul-review.yml. Do not write .ai/authorizations/**. Do
not generate/commit a production private key. Only
Hostinger Codex with unforgeable attestation may PASS.
Do not self-PASS. Do not merge. Do not push. Do not mark
ready.

## Hostinger bootstrap P0-B/P0-C reuse v12 (grant Task-ID standing run)

Evaluated real external Hostinger Codex review on exact
head 0df9a51. SIGNED_ARTIFACT none, disposition BLOCKED,
reason TRUSTED_BOOTSTRAP_NOT_ESTABLISHED. reuse=true.
v13=false. Did not issue A-013. allowed_paths already
cover bootstrap script/tests (scripts/**, tests/**,
contract tree). denied_paths unchanged.
lease-c3a003pr62q1 reused (v12). ctr-code-pr62smoke
reused. Appended REQ-SAUL-BOOTSTRAP-HEAD-001 /
REQ-SAUL-BOOTSTRAP-FALLBACK-001 /
REQ-SAUL-BOOTSTRAP-EXT-001 without PASS. Did not write
blockers/items. Wave artifacts:
`.ai/runs/20260814-2008-pr62-queue-cora/`. implements
false. do_not_merge true. do_not_push true.
technical_pass false. P0-A `/opt/sai/trusted-reviewer`
absent is WAITING_EXTERNAL_OPERATOR; Cursor must not
provision Hostinger. P1-D generic `[self-hosted]` is
DEFERRED_NONBLOCKING; do not create a blocker.
Contractor next: prove SAI_CANDIDATE_TREE HEAD equals
`--head`; refuse fallback to candidate
root/scripts/invoke-saul-review and saul-attest (lines
66-69); append HEAD/FALLBACK blocker
DISCOVERED or IMPLEMENTED_AWAITING_SAUL not PASS. Do
not provision Hostinger. Do not create a P1-D blocker.
Do not restore saul-review.yml. Do not PASS. Do not
merge. Do not push. Do not mark ready.

## Saul quality loop P0 reuse v12 (grant Task-ID standing run)

Evaluated B-SAUL-QUALITY-LOOP-001 / REQ-5300146420 and
AUTHENTICATION.md / REQ-5300187244 on exact head
516893c. reuse=true. v13=false. Did not issue A-013.
allowed_paths already cover executable machinery
(scripts/**, tests/**, .github/workflows/**,
.ai/_config/**, .ai/shared/schemas/**). Quality docs
under .ai/shared/quality/** are officer read-only spec;
contractors must not rewrite them. Pubkey pin is
officer/Hostinger (`.ai/authorizations/**` denied).
denied_paths unchanged. lease-c3a003pr62q1 reused (v12).
ctr-code-pr62smoke reused. Appended REQ-5300187244;
REQ-5300146420 already present. Did not write
blockers/items. Wave artifacts:
`.ai/runs/20260815-0302-pr62-queue-cora/`. Admin review:
`reviews/cora-saul-quality-loop-v12-reuse.yaml`.
implements false. do_not_merge true. do_not_push true.
technical_pass false. code-health.yaml 321>300 fails
icm-enforcement; contractor may split/include under
_config only. Contractor next: four disjoint slices
(sha-shard, architecture, authenticity-primary-context,
finding-ci-detectors-bloat) without PASS. Do not rewrite
quality docs. Do not write authorizations. Do not PASS.
Do not merge. Do not push. Do not mark ready.

## Decision 0009 principal blockers reuse v12 (grant Task-ID standing run)

Evaluated Dezocode comments 5303750100 / 5303751556 /
5303753512 / 5303755356 / 5303757105 on exact head
abae75d. reuse=true. v13=false. Did not issue A-013.
Decision 0009 and architecture.md are officer writes
(grant-pr62-queue-ceo, agent ceo, Task-ID
20260813-2015-pr62-queue-ceo). Cora did not write them.
Comment 5303750100 is human authority; tracked officer
grant already covers .ai/**. Not a new human-expansion
gate. Not A-013 for officer paths. Contractor executable
work already in v12 allowed_paths. denied_paths unchanged
(decisions/** and authorizations/** remain contractor-
denied). lease-c3a003pr62q1 reused (v12).
ctr-code-pr62smoke reused. Appended compact REQ-5303750100
/ 1556 / 3512 / 5356 / 7105. Appended four DISCOVERED
blockers with clearance_authority saul; did not PASS.
Wave artifacts: `.ai/runs/20260815-1903-pr62-queue-cora/`.
Admin review: `reviews/cora-decision-0009-v12-reuse.yaml`.
implements false. do_not_merge true. do_not_push true.
technical_pass false. Decision 0009 does not supersede
0005/0006/0007/0008. Officer next: persist Decision 0009
+ architecture.md. Contractor next: four disjoint slices
(comptroller-readiness, frontier-quality-arch,
anti-balloon, ralph-ci-convergence) without PASS. Do not
write decisions or authorizations. Do not PASS. Do not
merge. Do not push. Do not mark ready.

## Quality-ref amendment reuse v12 (grant Task-ID standing run)

20260815-1928 Cora wave amended the incomplete 1903
rust-universal ingest in place. Principal comments
5303804678 / 5303809236 (and in-place updates to
5303750100 / 3512 / 5356) make rust-lang/rust
control-plane-only, not a universal product template.
Domain-aware mapping YAML is under the contract tree.
No new blockers. No A-013/v13. No new Decision 0009.
Officer next: persist ONE Decision 0009 (Sai/ceo)
including the quality-reference amendment. Contractor
next: the same four disjoint slices, with
frontier-quality-arch now domain-aware
(rust/tailscale/element-x/TCA-principles/isowords/swift-format/testing/OpenSSF
→ Decision-0005). Wave:
`.ai/runs/20260815-1928-pr62-queue-cora/`. Did not PASS.
Did not commit. Did not push. Do not merge. Do not mark
ready. Cursor is not Saul.

