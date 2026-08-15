# Plan — human principal commit Agent-trailer allowlist

Contractor `ctr-code-pr62smoke`. Task-ID `20260813-2017-pr62-queue-ctr-code`.
Contract v12. Lease `lease-c3a003pr62q1`. Do not PASS. Do not merge. Do not push.

## Problem

PR `pull_request` icm-enforcement replays `origin/main..HEAD` through
`verify-agent-authorization`. Seven human Dezocode spec commits after
`skip_commits_missing_identity_at_or_before` (`d113fa0`) have no `Agent:`
trailer, so PR CI fails while push CI (new range only) stays green.

Do not force-push or rewrite those commits. Do not move the identity
cutoff forward to `516893c` (that would skip all trailer-less ancestors).
`audit.preserve_malformed_task_id` stays grammar-only and must not skip
authorization.

## Change

New explicit SHA allowlist `audit.preserve_human_principal_commits`.
Skip the Agent-trailer requirement only when ALL hold:

1. commit SHA is listed
2. git `%ae` is in `principal_emails` (pinned Dezocode noreply)
3. commit has no `Agent` trailer

Wrong SHA, wrong author, or Agent trailer present → still fail.

## Files

- `.ai/_config/authorization.yaml` — list seven SHAs + principal_emails
- `scripts/lib/sai_auth.py` — `%ae` helper + fail-closed skip predicate
- `scripts/lib/sai_auth_verify.py` — call skip in `verify_commit`; wire
  `--self-test`
- `scripts/lib/sai_auth_human_commit_test.py` — new fixtures (do not grow
  `sai_auth_test.py`)

YAML ≤300. `sai_auth.py` ≤500. `sai_auth_verify.py` ≤500. No
`.ai/authorizations/**`. No bloat-limit raise. No blocker PASS.

## Verify

- SELFTEST PASS: human-principal-listed-good,
  human-principal-wrong-author-bad, human-principal-unknown-sha-bad,
  agent-trailer-not-skipped-bad
- `scripts/verify-agent-authorization --self-test`
- live `scripts/verify-agent-authorization origin/main..HEAD` including
  the seven SHAs

## Overlap note

Stale in-progress runs still list `authorization.yaml` / `sai_auth*.py`.
Parent assigned these files exclusively for this slice. Same worktree;
not a semantic conflict. Do not wake Cora.
