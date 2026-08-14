# Changes — CTO-030

Deleted `.github/workflows/saul-review.yml`. Hardened trusted
`saul-cto-review.default-branch.yml` job `if:` so Hostinger is
acquired only for same-repo `pull_request_target` or default-branch
`workflow_dispatch`. Retargeted workflow-trust / Saul tests.
Updated authorization.yaml pointer, threat-trace, merge-readiness,
architectural-review one-liners, and blocker ledger (030/031).
Did not PASS.
