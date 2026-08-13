# Handoff — contractor (CTO-012 + first-write cue)

Starting HEAD was `de821c737c8ef8fc7dff26ccb15e2ddf6184aa18`.
Contract `20260813-pr62-saul-smoke` v3, lease `lease-c3a003pr62q1`.

## What landed

- **CTO-012:** `saul-review.yml` no longer `git archive HEAD` / 
  `pr-bootstrap-until-main`. Trusted sources are runner-image
  `SAI_TRUSTED_REVIEWER_ROOT` or `git archive` of **BASE_SHA**. Else
  `BLOCKED` / `TRUSTED_REVIEWER_UNAVAILABLE` and Codex is not invoked.
- **Shell-safety:** review `reason` is never interpolated via
  `${{ steps.saul.outputs.* }}`. Disposition is read from
  `/tmp/saul/review.yaml` and sanitized before `gh api`.
- **saul_review_key:** same
  `(repo, pr, type, contract, revision, head, requirement digest, scope)`
  → `NOOP_ALREADY_REVIEWED` (cache + tracked reviews). 10 duplicate
  lookups hit cache; new head or requirement digest mints a new key.
- **First-write cue:** unbound pre-commit emits one-line JSON
  `SAI_IDENTITY_REQUIRED` plus `SAI_CUE CORA_ADMISSION` or
  `RESUME_CONTRACTOR`. Worktree is not mutated. Existing assignment on
  the branch resumes the contractor.
- **Event adapter:** `scripts/sai-event-adapter` digest-compares
  material events; duplicates are NOOP.

## Verify (this tree)

`scripts/invoke-saul-review --self-test` and
`scripts/verify-agent-authorization --self-test` passed, including
cue, event, and trusted-reviewer negative fixtures.

## Next

Push; allow real Hostinger Saul to review the new SHA. WAITING_EXTERNAL
is nonterminal. Do not merge. Do not mark ready.
