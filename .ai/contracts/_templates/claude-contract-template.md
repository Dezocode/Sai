# Claude Code contractor contract template

Use with `scripts/agent-contract-scaffold --runtime claude`.

## Runtime-specific notes

- **primary_runtime:** `claude-code-cli`
- **Capability survey:** Claude Code MCP connectors; read `CLAUDE.md` first
- **Verify command:**
  ```bash
  SAI_AGENT_ID=<ctr-agent-id> scripts/agent-verify-caps \
    --tools-file .ai/agents/<name>/runtimes/claude/tools.json \
    --environment claude-code-cli
  ```
- **Automation profile:** `runtimes/claude/automation/profile.md` — document
  real scheduled tasks; do not claim Cursor UI automation as live
- **Claude Agent SDK (required):** `.ai/shared/references/claude-agent-sdk.md`
  — scaffold `runtimes/claude/agent-sdk/` with pinned
  `@anthropic-ai/claude-agent-sdk` or `claude-agent-sdk`, `config/agent-options.json`
  (hooks, MCP, subagents), and smoke-test evidence in tools.json
- **Invoke:** Open repo in Claude Code; read `CLAUDE.md` → `AGENT.md`
- **Dispatch (@mention):** implement via Agent SDK `query()` + webhook bridge;
  `.claude/agents/*.md` alone is insufficient for automated Slack/GitHub triggers

## ONBOARDING focus

1. Enumerate Claude Code MCP connectors relevant to contract scope.
2. Ask owner approval for each before adding to `runtimes/claude/tools.json`.
3. Document automation in `hooks.json` with real Claude mechanisms only.
4. Persona gate requires live demonstration of verified Claude connectors.

## Branch pattern

`proj/<project-slug>/<ctr-agent-id>/<task-slug>`

Example: `proj/splunk-clone/ctr-code-alpha1/ingest-pipeline`
