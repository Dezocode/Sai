# Implement — redact intake email

- Task-ID: `20260813-0133-redact-intake-email-cursor-cloud`

| Path | Change |
|---|---|
| `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/01_intake/output/intake.md` | Requester line is Slack ID only. |
| `.ai/shared/memory/conventions.md` | Run artifacts forbid personal email. |
| `.ai/stages/01_intake/CONTEXT.md` | Intake records username + Slack ID, not email. |
| `.ai/_config/security-policy.md` | Sensitive-data rule includes personal email. |

History of `main` is unchanged (no rewrite).
