# Mimi — Claude runtime suite (primary)

Primary runtime: `claude-code-cli`. Contents:

| File | Role |
|---|---|
| `tools.json` | Verified capability survey (session-evidence discipline; only `verified` entries count) |
| `automation/profile.md` | Claude-native automation truth (scheduled task, trigger status, hard limits) |
| `claude-desktop-bootstrap.json` | Machine-readable Desktop project bootstrap + `sai_contract` block |

Repo-level Claude surfaces: `.claude/agents/mimi-dispatcher.md`,
`.claude/skills/mimi-dispatcher/`, `.claude/settings.json`. Entry point:
`CLAUDE.md` → `.ai/agents/mimi/AGENT.md`. Cursor (secondary):
`../cursor/automation/profile.md`.
