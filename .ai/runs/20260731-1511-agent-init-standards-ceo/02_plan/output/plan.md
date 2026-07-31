# Plan — 20260731-1511-agent-init-standards-ceo

## Trigger

Saul CTO governance review @ 20260731-1510 tagged @sai; PR #55
(`cursor/agent-initialization-standards-9991`) received REQUEST_CHANGES with
four inline findings.

## Remediation scope

| # | Finding | Fix |
|---|---------|-----|
| 1 | `20260730-0127` metadata still `in_progress` | Set `status: completed` |
| 2 | `20260730-0313` metadata still `in_progress` | Set `status: completed` |
| 3 | Validator hard-codes SHA/patterns separate from schema | Recursive schema walker; drift regression in self-test |
| 4 | Timestamp accepts only UTC Z | Use `datetime.fromisoformat` for RFC3339 offsets |

## Branch strategy

Fast-forward `cursor/agent-initialization-standards-0916` from PR #55 head
(`d950fd6`), apply remediations, push for fresh Saul review. Supersedes PR #55
branch naming only; human decides close/retarget.

## Verification

- `python3 scripts/lib/validate-agent-event.py --self-test`
- `scripts/verify-agent-audit origin/main..HEAD`
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-merge-handoff origin/main..HEAD`
