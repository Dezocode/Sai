# Handoff — ctr-code-pr62smoke (TPR-001 / TPR-002)

Lease `lease-c3a003pr62q1`, contract v12 (Cora reused; no A-013).
Task-ID `20260813-2017-pr62-queue-ctr-code`. Wave
`20260814-1540-pr62-queue-ctr-code`. Parent pr62-primary.

TPR-001: deleted `.github/workflows/trusted-reviewer-provision.yml`.
Stopped `sai_auth_wait.py` provisioner poll. Kept provision python
module + `--self-test`. Hermetic `assert_provisioner_workflow()`
rejects `checkout ref: from_sha` then execute provisioner. Live
file absent. Did not execute freeze-from-candidate. Did not
delete Decision 0008. Did not add `on: pull_request`.

TPR-002: Codex default sandbox `workspace-write`; `--ephemeral`
kept; `--ignore-user-config` on skip-git line. `codex_exec_env`
strips GITHUB_TOKEN/GH_TOKEN/SSH_AUTH_SOCK/DOCKER_HOST; keeps
model keys. Invoke Codex env has no GITHUB_TOKEN. Token remains
on Post/Status/Claim. Fixture retargeted in place.

Ledger: TPR-001 / TPR-002 IMPLEMENTED_AWAITING_SAUL; clearance
Saul. Did not PASS. Did not merge. Did not push. Did not restore
`saul-review.yml`. Did not write denied_paths. Did not rework
CTO-015..030. Residual: Codex model credential; Landlock may be
weak in Hostinger container; runner-group UNKNOWN/VERIFY_REQUIRED.

`self_pass: false`. `do_not_merge: true`. `do_not_push: true`.

TPR-002 follow-up (Cora v12 reuse, no A-013): Invoke Codex as
Saul now sets `GITHUB_TOKEN: ""` / `GH_TOKEN: ""` and unsets both
before chmod/invoke. Publisher Claim/Post/Status keep GH_TOKEN.
tpr-d requires the empty override. Status stays
IMPLEMENTED_AWAITING_SAUL. Did not PASS. Did not push.

Next: qualifying Saul review of this exact head. Human merge of
PR #62 remains the trusted-workflow activation event.

## Wave SAUL-IDENTITY-001 (v12 reuse, no A-013)

Canonical Hostinger Ed25519 attestation. Cursor named subagent is not
Saul. `attempt_clear` actor=saul without `--from-file` → REJECT
INVALID_SAUL_IDENTITY. resume spoof `{reviewer:saul, runtime:cursor}`
does not satisfy exit. consume APPROVE unsigned → FAIL. Blocker
SAUL-IDENTITY-001 IMPLEMENTED_AWAITING_SAUL, not PASSED. No production
key in repo. Did not push. Did not merge. Did not restore saul-review.yml.

Next safe action: Hostinger Saul signs this exact head; humans merge PR #62
if satisfied. Do not claim READY_FOR_HUMAN_REVIEW.

## Wave live-rev callers (20260814-saul-identity-live-rev)

`attempt_clear` and `consume` now compare attestation to the live
pointer revision and live HEAD, not the review's self-claim.
Hermetic fixtures without a pointer still fall back to the review
revision. Signed rev 11 vs live v12 → REJECT INVALID_SAUL_IDENTITY.
Did not PASS. Did not push. `sai_auth_review.py` remains 500 lines.

Next safe action: Hostinger Saul signs this exact head against v12.
Do not claim READY_FOR_HUMAN_REVIEW.

## Wave CI import path (20260814-saul-identity-ci)

`saul-hostinger-bootstrap-review` used `REPO/lib` on `sys.path` and
imported `sai_auth` before `--self-test`. CI `sai-blockers --self-test`
failed with `ModuleNotFoundError`. Fixed to `scripts/lib` and early
`--self-test` exit 2 `NOT_HOSTINGER_SAUL`. Identity-test subprocess
sets `PYTHONPATH` to `scripts/lib`. Did not PASS. Did not push.

Next safe action: Hostinger Saul signs this exact head against v12.
Do not claim READY_FOR_HUMAN_REVIEW.
