# Handoff — ctr-code-pr62smoke (A-011/v11 skip-guard)

Lease `lease-c3a003pr62q1`, contract v11 (Cora A-011 at `20bcfb4`).
Task-ID `20260813-2017-pr62-queue-ctr-code`. Wave
`20260814-0450-pr62-queue-ctr-code`.

Implemented A-011 only: restored narrow `on: pull_request`
(opened/synchronize/reopened/ready_for_review) and kept
`workflow_dispatch`. Same-repo job `if:` is the pre-A-010 guard.
Skip-guard `id: retire` cat-files
`saul-cto-review.default-branch.yml` on `origin/<default>` and
`origin/main`; if present, writes
`TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN`, `codex_invoked: false`,
sets `skip=true`, does not invoke Codex, exits 0 without APPROVE.
This PR: origin/main still lacks that file, so Codex still runs.

Did not PASS CTO-025. Did not merge. Did not push. Did not write
denied_paths. Did not grow `sai_auth_review.py`. Did not rework
CTO-015..021/024/028/029. Did not fake the trusted file onto
origin/main. Did not restore candidate-HEAD trust / freeze /
allow-unsafe-pr-checkout.

`self_pass: false`. `do_not_merge: true`.
`cto025_activation_on_main: false`.

Next: qualifying Saul review of this exact head. Human merge of
PR #62 remains the trusted-workflow activation event.
