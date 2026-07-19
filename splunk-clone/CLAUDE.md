# Splunk Clone — isolated prototype (monaecode/Sai)

This directory is the **product root** for contract `20260715-splunk-clone-monaecode`.
It is intentionally isolated from future SAI application code until an approved
integration gate (see `docs/integration-manifest.md`).

## Claude Code entry (Splunky)

1. Open **`monaecode/Sai`** in Claude Code / Claude Desktop.
2. `cd splunk-clone` (recommended working directory).
3. Load contract + onboarding:
   - `../.ai/contracts/20260715-splunk-clone-monaecode/onboarding-prompt.md`
4. Your subagent definition: `.claude/agents/splunky.md`
5. Optional: set `"agent": "splunky"` in `.claude/settings.json` to run the main session as Splunky.

## ICM agent mirror

Registry profile: `../.ai/agents/splunky/AGENT.md`

## Branch

`proj/splunk-clone/ctr-code-splunky/<task-slug>` on **monaecode/Sai** only.

## Slack

`#splunk-clone-project` — PLAN before PR, VERIFY after push (see contract.md).
