# CODEX.md — OpenAI Codex Desktop entry point for this repo

This is the Codex Desktop equivalent of `.cursor/rules/sai-coordination.mdc`
(Cursor) and `CLAUDE.md` (Claude Code). Read this before doing anything else
when working in **OpenAI Codex Desktop** against this repository.

## Read first

1. `.ai/CONTEXT.md` — Layer 0 workspace identity, governed repositories,
   people/agents, non-negotiable rules.
2. If you are not yet listed as `active` in `.ai/agents/registry.json`
   under your current identity: read and execute `.ai/INITIALIZE.md`
   before accepting tasks.
3. Load your named profile from `.ai/agents/<your-name>/AGENT.md` after
   your principal grants name and role title in Phase 6.

## Codex Desktop is not Cursor or Claude Code

This repo's `.ai/` framework was built for Cursor agents first. When
operating in Codex Desktop:

- There is no Cursor **Automations** UI and no Claude Code **scheduled-tasks**
  API. Do not claim automation exists until your principal confirms a real
  Codex mechanism and you record evidence in
  `runtimes/codex/tools.json`.
- Read `.ai/shared/references/agent-runtimes.md` for the canonical runtime
  index. Your capability survey belongs in
  `.ai/agents/<name>/runtimes/codex/tools.json`, not another agent's folder.
- `.cursor/rules/sai-coordination.mdc` is not auto-loaded — read it manually
  as Layer 1 context; its rules still bind you.
- Slack bots (@Claude, ChatGPT, etc.) are **not** registered SAI agents unless
  explicitly listed in `.ai/agents/registry.json`.

## Initialization (Codex branch)

Follow `.ai/INITIALIZE.md` Phases 0–9. For Phase 5B and Phase 7 use the
Codex branch documented in `agent-runtimes.md`:

```bash
export SAI_AGENT_ID=<your-agent-id>
scripts/agent-verify-caps \
  --tools-file .ai/agents/<name>/runtimes/codex/tools.json \
  --environment codex-desktop
```

Phase 7: deliver a Codex-specific automation spec at
`.ai/agents/<name>/runtimes/codex/automation/profile.md` or record
`delegated:` in `registry.json` — never `unavailable`.

## Non-negotiable rules

Same as `.ai/CONTEXT.md` and `CLAUDE.md`: no secrets in Slack/logs/commits;
no fabricated verification; human review gates absolute; one agent per
working tree; preserve existing agent changes.
