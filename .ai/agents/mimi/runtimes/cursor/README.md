# Cursor runtime — Mimi (optional)

Mimi's **primary runtime is Claude Code** (`claude-code-cli`). This suite
holds an optional Cursor Automations spec only if monaecode later runs Mimi
in Cursor Desktop.

Do not run `agent-verify-caps` from Cursor against
`runtimes/claude/tools.json` — cross-runtime surveys corrupt inventory.

See `runtimes/claude/automation/profile.md` for the historical Cursor UI
spec generated at init; live automation is documented in `hooks.json`.
