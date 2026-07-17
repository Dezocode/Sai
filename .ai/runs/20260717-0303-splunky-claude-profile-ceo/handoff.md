# Handoff — Splunky Claude profile P1

## Done

- Replaced `.ai/agents/splunky/runtimes/claude/automation/profile.md` with a Claude Code session/delegated profile (no Cursor Automations UI instructions).
- Replaced root `.ai/agents/splunky/automation/profile.md` with a canonical alias pointer for semantic hierarchy.

## Verification

- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`

## Next

- Splunky ONBOARDING Phase 5B: populate `runtimes/claude/tools.json` with verified capabilities before any scheduled task or MCP claims.
- Consider extending `scripts/agent-automation-spec` with `--runtime-suite claude` so scaffold cannot reintroduce Cursor UI into `runtimes/claude/` (follow-up, not in this commit).

## Review gate

dezocode: confirm P1 addressed on PR #17.
