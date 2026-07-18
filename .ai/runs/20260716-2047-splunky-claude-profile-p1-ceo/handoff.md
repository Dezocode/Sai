# Handoff — Splunky Claude profile P1 fix

## Result

Replaced Splunky `runtimes/claude/automation/profile.md` and legacy
`automation/profile.md` (Cursor Automations UI copies from
`scripts/agent-automation-spec`) with a **Claude Code session-driven**
operating profile aligned with Saul Codex stub pattern and
`.ai/INITIALIZE.md` Phase 7 Claude rules.

Updated `hooks.json` to forbid claiming Cursor Automations as Splunky's
primary trigger; documented session-driven invocation via `splunk-clone/CLAUDE.md`.

## Verification

- `scripts/verify-semantic-hierarchy` — OK
- `python3 -m json.tool .ai/agents/splunky/hooks.json` — OK

## Next safe action

- monaecode: complete Splunky Phase 5B in Claude Code (`agent-verify-caps`).
- After verified scheduled task (if any), update registry `automation` field with evidence.

## Risks

None; registry remains `delegated:` until principal verifies Claude automation.
