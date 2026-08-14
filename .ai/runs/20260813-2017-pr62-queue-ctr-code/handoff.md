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
