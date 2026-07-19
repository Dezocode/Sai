# Handoff — Splunky zero-Bash provisional policy (PR #21 P1)

Addressed CTO P1: removed generic `Bash` from Splunky agent-level `tools:` in
`splunk-clone/.claude/agents/splunky.md`; removed all `Bash(...)` permissions
and Bash hooks from live settings and `claude-desktop-bootstrap.json`; tightened
`.ai/ONBOARDING.md` Phase 4 and splunk onboarding prompt to forbid any Bash
while registry status is `provisional`.

Next: Splunky completes Phase 3 owner approval loop and Phase 5B
`scripts/agent-verify-caps` before any narrow shell entries are added to
`approved_capabilities[]`. monaecode/dezocode re-review PR #21.
