# Runtime suites — Mimi (`mimi`)

| Suite | Status | Capability file |
|---|---|---|
| **claude** (primary) | active | `runtimes/claude/tools.json` |
| cursor | optional spec | `runtimes/cursor/README.md` — not primary |
| codex | stub | `runtimes/codex/README.md` — awaiting live Codex Desktop init |

Canonical manifest: root `tools.json` → `runtimes/claude/tools.json`.

Invoke: Claude Code with `monaecode/Sai` repo open; read `CLAUDE.md` and
load `.ai/agents/mimi/AGENT.md`. **Not** the Anthropic `@Claude` Slack app.

Automation: `mimi-protocol-upkeep` (Claude Code cron) — see
`hooks.json` and `runtimes/claude/automation/profile.md` (spec; Cursor UI
sections are not live automation for this agent).
