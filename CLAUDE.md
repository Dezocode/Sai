# CLAUDE.md — Claude Code entry point for this repo

This is the Claude Code equivalent of `.cursor/rules/sai-coordination.mdc`
(Cursor's always-on rule). Read this before doing anything else in this
repository when using **Claude Code CLI**.

## Read first

1. `.ai/CONTEXT.md` — Layer 0 workspace identity, governed repositories,
   people/agents, non-negotiable rules.
2. `.ai/shared/references/agent-runtimes.md` — canonical multi-runtime index.
3. If you are not yet listed as `active` in `.ai/agents/registry.json`
   under your current identity: read and execute `.ai/INITIALIZE.md`
   before accepting tasks.
4. If you are a **named agent** (e.g. Mimi, agent-id `mimi`): load
   `.ai/agents/<name>/AGENT.md` and your charter under `.ai/agents/_roles/`.

## Claude Code is not Cursor

- Capability surveys belong in
  `.ai/agents/<name>/runtimes/claude/tools.json` — never overwrite another
  runtime's inventory (`runtimes/cursor/tools.json` on a Claude-primary agent).
- Phase 5B: `scripts/agent-verify-caps --environment claude-code-cli
  --tools-file .ai/agents/<name>/runtimes/claude/tools.json`
- Phase 7 automation: record real Claude Code mechanisms in
  `runtimes/claude/automation/profile.md` and `hooks.json` — do not fabricate
  Cursor Automations UI entries as "live" automation.
- `.cursor/rules/sai-coordination.mdc` is not auto-loaded — read manually.

## Slack is not your identity

The Anthropic **@Claude Slack app** is a separate integration. It does not
load this repo's agent profiles unless your session explicitly does. Registered
SAI agents are in `.ai/agents/registry.json` only.

## Other runtimes

- Cursor: `.cursor/rules/sai-coordination.mdc` and `@<name>`
- Codex Desktop: `CODEX.md`

## Non-negotiable rules

Same as `.ai/CONTEXT.md`: no secrets in Slack/logs/commits; evidence-backed
`tools.json`; human review gates; one agent per working tree.
