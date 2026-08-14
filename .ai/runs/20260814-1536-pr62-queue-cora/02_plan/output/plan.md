# Plan — Cora TPR-001/002 reuse of v12

HEAD `01fe60609d6d61d71cb401a06619b71601ed94f6`. Contract
`20260813-pr62-saul-smoke` v12. Lease `lease-c3a003pr62q1`.
Contractor `ctr-code-pr62smoke`. Task-ID
`20260813-2017-pr62-queue-ctr-code`.

**reuse=true. v13=false. A-013=false.** Both remediations sit
under already-granted v12 `allowed_paths`. Not authority
expanding. Not path expansion. denied_paths unchanged.

Coverage:

- TPR-001 DELETE `.github/workflows/trusted-reviewer-provision.yml`
  plus `sai_auth_wait.py` poll stop plus optional provision
  python/fixture work → `.github/workflows/**`, `scripts/**`,
  `tests/**`, contract tree.
- TPR-002 in-place `sai_auth_review.py` (500, no net lines),
  retarget `sai_auth_test.py` (~497), new small test module,
  strip Invoke Codex `env:` on
  `saul-cto-review.default-branch.yml` → `scripts/**`,
  `.github/workflows/**`, `tests/**`.

v12 already: trusted default-branch file is the only
self-hosted Saul workflow; do not restore `saul-review.yml`
or candidate-HEAD trust; do not grow `sai_auth_review.py` /
`sai_auth_test.py`. TPR-001/002 fit those constraints.

Cora writes: compact REQ-TPR-001 / REQ-TPR-002 rows on
`requirements/ledger.yaml` (stays ≤300); this wave dir;
standing-run handoff append. Does not write A-013, v13,
blockers/items, scripts, workflows, `_config`, authorizations,
decisions, or `.cursor`. Does not bump lease or
`contract.json`. Commit uses grant Task-ID
`20260813-2016-pr62-queue-cora`. This wave does not push.

Contractor next: write TPR-001 / TPR-002 blocker items
without PASS, then implement under v12.
