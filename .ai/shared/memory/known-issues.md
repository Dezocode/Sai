# SAI — Known issues and recurring failures

> Record verified, recurring problems and their workarounds. Remove entries
> when fixed at the source (rules, contracts, tests, or references).

## Open

- **Contract shell allowlist `git branch` wildcards** (CTO P1 PR #15, 2026-07-17):
  `Bash(git branch proj/…/*)` in Phase-5B allowlists can match destructive
  `git branch <prefix> -D <victim>`. Remediation: use `--list` / `checkout -b`
  only; merge PR #15 follow-up or amend `claude-desktop-bootstrap.json` on the
  contract branch. CI gate: `scripts/verify-contract-shell-allowlist`.
- **Mimi PR #21 — Cursor profile vs Claude-primary** (CTO P1, 2026-07-17):
  Draft dispatcher bootstrap must not ship pre-verification `Bash(git *)` /
  `Bash(gh *)` grants or a Cursor automation profile as primary for
  `claude-code-cli` agents. Remediate on PR #21 before CTO re-review.
- **No Google Drive credentials in cloud-agent VMs** (observed 2026-07-14):
  `scripts/agent-sync-drive` records status `pending` when
  `SAI_DRIVE_REMOTE` is unset. Drive mirroring must be run from a machine
  with a configured rclone remote.
- **`git reset --hard` in a test clone reverts locally patched scripts**
  (observed 2026-07-14 during hook testing): when exercising hooks in a
  scratch clone with uncommitted script fixes, a hard reset silently
  restores the committed versions. Re-copy patched files after any reset,
  or commit fixes before testing.

## Resolved

- **Slack MCP delivery from cloud agents failed silently** (2026-07-14):
  `slack_send_message` returned `no_text` and nothing appeared in
  #agentupdates. Root cause: the message body must be passed in the
  `message` parameter; passing it as `text` is silently ignored by the
  tool. Fixed by using the correct parameter (delivery now returns a
  message link). Always confirm delivery via the returned link or by
  reading the channel; on failure, queue via `scripts/agent-report`.
