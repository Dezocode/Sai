# Handoff — redact intake email

- Task-ID: `20260813-0133-redact-intake-email-cursor-cloud`
- Agent: `cursor-cloud`
- Branch: `cursor/redact-intake-email-10de`
- Base: `3186cfb` (`Dezocode/Sai:main` after PR #57)

## Done

- Removed the personal email from the pstack run intake requester line.
  Requester is now `dezocode (U0BHYH0NMCY)` only.
- Conventions, intake stage contract, and security-policy now forbid
  committing personal email; identify people by username and Slack ID.

## Not done

- Git history on `main` still contains the prior intake line (no rewrite
  authorized). Current tree is redacted.
- Drive sync pending (`SAI_DRIVE_REMOTE` unset).

## Next safe action

Co-founder review of the follow-up draft PR. After merge, working tree on
`main` no longer publishes the address.
