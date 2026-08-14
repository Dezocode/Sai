# Plan — A-011 restore pull_request + skip-guard

A-010 full trigger removal is operationally incompatible with Cloud
gh `actions=read` HTTP 403. Restore narrow `on: pull_request` and
keep `workflow_dispatch`. Add fail-closed skip when
`origin/main:.github/workflows/saul-cto-review.default-branch.yml`
exists. Do not PASS. Do not merge. Do not push. Do not fake trusted
file onto origin/main. Do not restore candidate-HEAD trust.
