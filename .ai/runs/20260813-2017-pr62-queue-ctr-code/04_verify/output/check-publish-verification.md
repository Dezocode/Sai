# Verify — trusted Check `Saul / Product Quality`

Did not PASS. Did not push. Did not merge. Did not restore
`saul-review.yml` or trusted-reviewer-provision.yml.

## Commands (exit 0 unless noted)

- `scripts/verify-saul-workflow-trust --self-test` — 16 fixtures, exit 0
  including `trusted-check-publish-from-trusted-tree-good` and
  `unsigned-check-not-pass-bad`
- `scripts/verify-saul-authenticity --self-test` — 18 fixtures, exit 0
- `python3 scripts/lib/sai_auth_saul_test.py` — includes
  `saul-check-unsigned-not-pass-bad` and `saul-check-publish-no-secret-good`
- `scripts/invoke-saul-review --self-test` — 32 fixtures, exit 0
- YAML parse of trusted workflow — ok
- unsigned `--dry-run` payload: `name=Saul / Product Quality`,
  `conclusion=failure`, `authority=ZERO_AUTHORITY`, exit 1 (fail-closed)
- `--publish` without `GH_TOKEN`: `BLOCKED GH_TOKEN_MISSING`, exit 1
- workflow 294 lines (cap 300); `sai_auth_saul_check.py` 204 (cap 500)
- `cto021_activation_on_main=false`; candidate `saul-review.yml` absent

Codex step still blanks `GITHUB_TOKEN`/`GH_TOKEN`. Publisher keeps `GH_TOKEN`.
Job-level `if:` unchanged. Not PASS.
