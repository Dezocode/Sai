# Implement — trusted Check `Saul / Product Quality`

Contractor `ctr-code-pr62smoke`. Lease `lease-c3a003pr62q1`. v12 reuse.
Did not PASS. Did not push. Did not merge. Did not restore
`saul-review.yml` or trusted-reviewer-provision.yml.

## Changes

- `.github/workflows/saul-cto-review.default-branch.yml` — `checks: write`;
  after Attest, always-run publisher from `SAI_TRUSTED_TREE` only.
  Missing publisher → `TRUSTED_PUBLISHER_MISSING` exit 1. Job-level `if:`
  unchanged (Hostinger only for same-repo `pull_request_target` or
  default-branch dispatch). Codex still blanks `GITHUB_TOKEN`/`GH_TOKEN`.
- `scripts/lib/sai_auth_saul_check.py` — `--publish` POSTs Check via `gh`
  for exact `--head`. Unsigned/BLOCKED cannot `conclusion=success`.
  Output is signed-envelope digests only (no PEM/keys). `GH_TOKEN` required.
- Fixtures in `sai_auth_workflow_trust_test.py` and `sai_auth_saul_test.py`.

Check name is evidence, not proof. Not PASS.
