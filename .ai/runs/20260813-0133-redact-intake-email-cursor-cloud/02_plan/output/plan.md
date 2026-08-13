# Plan — redact intake email

- Task-ID: `20260813-0133-redact-intake-email-cursor-cloud`

## Current / desired

Line 5 of the pstack run intake records a personal email next to Slack ID.
Desired: requester is `dezocode (U0BHYH0NMCY)` only.

## File changes

| Path | Change |
|---|---|
| `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/01_intake/output/intake.md` | Drop personal email from requester line. |
| `.ai/shared/memory/conventions.md` | Run artifacts: do not commit personal email; Slack ID + username suffice. |
| `.ai/stages/01_intake/CONTEXT.md` | Intake identifies requester without personal email. |
| `.ai/runs/20260813-0133-redact-intake-email-cursor-cloud/` | This follow-up run. |

## Out of scope

- History rewrite of `3186cfb` / `3dbd951` (hard gate).
- Scanning Drive mirrors (pending; no `SAI_DRIVE_REMOTE`).

## Verification

- `rg` for the former address returns no working-tree hits.
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`
- `scripts/verify-merge-handoff origin/main..HEAD`

## Review gate

None of the hard security gates. PLAN report then implement. New draft PR against `main`.
