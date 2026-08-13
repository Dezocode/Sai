# Plan — Saul follow-up remediations

## Current vs desired

| Gate | Current | Desired |
|---|---|---|
| PR #62 agent-audit | FAIL `d14402e` Task-ID missing HHMM | PASS via SHA-pinned grammar exception; authorization unchanged |
| PR #62 saul-cto-review | BLOCKED bwrap/userns | Real Codex invoke with `-s danger-full-access`; BLOCKED still not APPROVE |
| consume YAML | banner prefix fails `read_yaml` | strip `=== path ===` banners |
| GitHub status | description > 140 chars | truncate to 140 |
| PR #64 draft | ready / non-draft with unsatisfied gates | convert to draft |
| PR #64 CTO-001 | three pre-contract commits fail Contract-ID replay | SHA-pinned `skip_commits_missing_contract_at_or_before` |
| PR #64 registry | `ctr-code-ri1` unbound | provisional registry + agent folder |

## File changes (PR #62 first)

- `scripts/lib/sai_auth.py` — banner strip; grammar-preserve helper
- `scripts/lib/sai_auth_review.py` — Codex sandbox default
- `scripts/lib/sai_auth_verify.py` — pre-contract Contract-ID skip window
- `scripts/lib/sai_auth_test.py` — fixtures
- `scripts/verify-agent-audit` / `scripts/verify-merge-handoff` — honor preserve list
- `.github/workflows/saul-review.yml` — 140-char status
- `.ai/_config/authorization.yaml` — pin `d14402e`; empty contract-skip on this PR

## PR #64 (after PR #62 push)

- Convert to draft
- Strip banner from committed disposition YAML
- Set contract-skip cutoff to `46e73c3`
- Bind `ctr-code-ri1` provisionally (Cora-class paths; human source is this Slack instruction)
- Merge parent only if conflicts are mechanical; no force-push

## Verification

- `scripts/invoke-saul-review --self-test`
- `scripts/consume-saul-contract-review --self-test`
- `scripts/verify-agent-authorization --self-test` and `origin/main..HEAD`
- `scripts/verify-agent-audit origin/main..HEAD`
- `scripts/verify-merge-handoff origin/main..HEAD`
- `scripts/verify-code-health --self-test` and live
- `scripts/verify-semantic-hierarchy`

## Review gates

- Do not mark PR #62 ready; do not merge.
- Do not treat Saul BLOCKED as a technical disposition.
- Force-push remains forbidden unless dezocode names that action.
