# Handoff — ctr-code-pr62smoke (A-012/v12 CTO-030)

Lease `lease-c3a003pr62q1`, contract v12 (Cora A-012 at `307df46`).
Task-ID `20260813-2017-pr62-queue-ctr-code`. Wave
`20260814-0512-pr62-queue-ctr-code`.

Deleted `.github/workflows/saul-review.yml` (candidate-controlled
Hostinger `pull_request` + `workflow_dispatch` path). Skip-guard is
not a trust boundary. Hardened
`.github/workflows/saul-cto-review.default-branch.yml` job-level
`if:`: Hostinger only for same-repo `pull_request_target` OR
`workflow_dispatch` from the default-branch ref (evaluated before
runner assignment). Candidate remains DATA at `path: candidate-data`,
`persist-credentials: false`. No `on: pull_request` on the trusted
file. No `allow-unsafe-pr-checkout`. Fail closed
`TRUSTED_REVIEWER_UNAVAILABLE`.

Retargeted trust tests. Absent `saul-review.yml` is PASS.
`authorization.yaml` workflow pointer now names the trusted file.
Ledger: CTO-030 IMPLEMENTED_AWAITING_SAUL; CTO-031 TRIAGED;
CTO-025 note that CTO-030 supersedes skip-guard; 026 uncleared.
Did not PASS. Did not merge. Did not push. Did not write
denied_paths. Did not grow `sai_auth_review.py` (500) or
`sai_auth_test.py` (497). Did not fake the trusted file onto
origin/main.

Merge-activated state = trusted file on main + no
`saul-review.yml`; dispatch only from default branch. Residual =
new collaborator self-hosted workflow (runner-group
UNKNOWN/VERIFY_REQUIRED). Last qualifying Saul 31771910025 on
4503f55.

`self_pass: false`. `do_not_merge: true`. `do_not_push: true`.
`cto025_activation_on_main: false`.

Next: qualifying Saul review of this exact head. Human merge of
PR #62 remains the trusted-workflow activation event. New SHA
needs its own CI (CTO-031).
