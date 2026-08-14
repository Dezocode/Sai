# Verify — TPR-001 / TPR-002

- `scripts/verify-saul-workflow-trust --self-test` — 14 fixtures including tpr-a..h
- `scripts/invoke-saul-review --self-test` — 30 fixtures; sandbox default workspace-write
- `scripts/sai-blockers --self-test` — 13 fixtures; live ledger parses; no self-pass
- `scripts/verify-code-health` — 40 PASS (after staging deletion)
- `scripts/provision-trusted-reviewer-root --self-test` — 7 fixtures kept
- `test ! -f .github/workflows/trusted-reviewer-provision.yml` — OK
- `test ! -f .github/workflows/saul-review.yml` — OK
- line counts: sai_auth_review.py 495; sai_auth_test.py 497;
  saul-cto-review.default-branch.yml 255; all under limits
- Did not PASS. Did not merge. Did not push. Did not restore saul-review.yml.
