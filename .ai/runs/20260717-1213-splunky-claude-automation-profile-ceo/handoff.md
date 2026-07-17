# Handoff — Splunky Claude automation profile (CEO)

## Done

- Replaced `.ai/agents/splunky/runtimes/claude/automation/profile.md` with a
  Claude Code session-driven operating profile (no Cursor Automations UI).
- Legacy `.ai/agents/splunky/automation/profile.md` is now an alias pointer.
- Updated `hooks.json` automation_triggers to document session mechanism;
  scheduled/Slack/GitHub marked `not_built`.
- Clarified optional Cursor suite in `runtimes/cursor/README.md`.

## Verification

- `scripts/verify-semantic-hierarchy` — OK
- `scripts/verify-agent-audit origin/main..HEAD` — OK (before this commit)

## Next

- monaecode: complete Splunky Phase 5B (`agent-verify-caps` claude-code-cli)
  before any scheduled-task automation claim.
- PR #21: re-review Splunky automation paths after push.
