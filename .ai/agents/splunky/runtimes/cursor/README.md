# Cursor runtime — Splunky (optional)

Splunky's **primary runtime is Claude Code** (`claude-code-cli`). This suite
exists only if monaecode later runs Splunky in Cursor Desktop (`@splunky`).

Do not run `agent-verify-caps` from Cursor against
`runtimes/claude/tools.json` — cross-runtime surveys corrupt inventory.

Live automation for Splunky is documented in
`runtimes/claude/automation/profile.md` and `hooks.json` (session-driven
Claude Code). No Cursor Automations spec is verified or required today.
