# Claude Agent SDK — Mimi dispatcher

Contract: `20260717-mimi-dispatcher-bootstrap-monaecode` (when merged)  
Reference: `.ai/shared/references/claude-agent-sdk.md`

## Required for @mimi Slack/GitHub dispatch

1. **`dispatch/` service** — Node or Python using `@anthropic-ai/claude-agent-sdk` / `claude-agent-sdk`.
2. **`config/agent-options.json`** — hooks (`PreToolUse` / `PostToolUse`), MCP (GitHub, Slack), subagents (`mimi-dispatcher`).
3. **Smoke test** — read-only `query()` log → `.ai/runs/<task-id>/04_verify/output/agent-sdk-smoke.txt`.
4. **tools.json** — `claude-agent-sdk` capability with evidence (verifier does not auto-detect yet).

Desktop project + `.claude/agents/mimi-dispatcher.md` remain human-interactive entry points; **automated** @mention handling must go through the SDK harness.
