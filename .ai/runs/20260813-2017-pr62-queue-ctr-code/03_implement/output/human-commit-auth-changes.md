# Implement — human principal commit Agent-trailer allowlist

PR `pull_request` icm-enforcement failed on HEAD `47f7439` because
`verify-agent-authorization` replays `origin/main..HEAD` and seven human
Dezocode spec commits have no `Agent:` trailer. Push CI only saw the
new range. History is not rewritten. Identity cutoff stays at `d113fa0`.

`audit.preserve_malformed_task_id` remains grammar-only.

New `audit.preserve_human_principal_commits` skip is fail-closed: listed
SHA + git `%ae` in `principal_emails` + no Agent trailer. Wrong SHA,
wrong author, or Agent present still fails.

## Files

- `.ai/_config/authorization.yaml` — seven SHAs + Dezocode noreply email
- `scripts/lib/sai_auth.py` — `commit_author_email`, `human_principal_identity_skip`
- `scripts/lib/sai_auth_verify.py` — skip in `verify_commit`; `--self-test` wire
- `scripts/lib/sai_auth_human_commit_test.py` — four fixtures

Did not write `.ai/authorizations/**`. Did not raise bloat limits.
Did not PASS blockers. Did not merge. Did not push. Did not wake Cora.
