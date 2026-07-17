# Automation profile alias — Splunky (ctr-code-splunky)

Splunky's **primary runtime is Claude Code** (`claude-code-cli`), not Cursor
Automations.

**Canonical profile (read and maintain this file):**

`.ai/agents/splunky/runtimes/claude/automation/profile.md`

This path exists because `verify-semantic-hierarchy` requires
`automation/profile.md` on every agent folder. Do **not** create a Cursor
Scheduled automation for Splunky unless the principal explicitly adds an
optional `@splunky` helper — the CEO/registry record automation as **delegated**
to the Claude profile above.
