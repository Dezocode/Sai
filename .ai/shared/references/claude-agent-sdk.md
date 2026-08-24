# Claude Agent SDK — SAI runtime reference (Layer 3)

> Canonical requirement for **Claude-primary** agents (`primary_runtime: claude-code-cli`)
> and Claude contractor contracts. Subagents + `.claude/settings.json` alone are
> **not sufficient** for dispatch automation (@mimi Slack/GitHub) — the Agent SDK
> is the programmatic harness for production triggers, hooks, and MCP.

Official overview: [Agent SDK overview](https://docs.claude.com/en/docs/agent-sdk/overview)  
Claude Code settings/subagents (complementary): [Settings](https://docs.anthropic.com/en/docs/claude-code/settings), [Subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## Packages

| Language | Install | Import |
|---|---|---|
| TypeScript | `npm install @anthropic-ai/claude-agent-sdk` | `@anthropic-ai/claude-agent-sdk` |
| Python | `pip install claude-agent-sdk` (venv, Python ≥3.10) | `claude_agent_sdk` |

Auth: `ANTHROPIC_API_KEY` (never commit). Bedrock/Vertex flags per Anthropic docs.

## ICM scaffold layout (required for Claude contracts)

Every Claude contractor or principal-agent evolution contract must reference:

```
.ai/agents/<folder>/runtimes/claude/
  tools.json                    # verified caps only
  automation/profile.md
  agent-sdk/
    README.md                   # how this agent uses the SDK
    package.json OR pyproject.toml  # pin @anthropic-ai/claude-agent-sdk / claude-agent-sdk
    src/run-agent.ts OR run_agent.py  # minimal query() entrypoint
    config/
      agent-options.json        # ClaudeAgentOptions: allowedTools, hooks, mcpServers, agents
```

Optional repo-root dispatch service (Mimi dispatcher):

```
.ai/agents/mimi/runtimes/claude/agent-sdk/dispatch/
  slack-github-bridge/          # OSS webhook → SDK query() — document, no secrets in git
```

Contract deliverable IDs should include **`Claude Agent SDK harness`** when
`primary_runtime` is `claude-code-cli`.

## SDK features to map to SAI artifacts

| SDK feature | SAI mapping |
|---|---|
| `query()` / agent loop | Dispatch runner for @mimi / contractor jobs |
| Hooks (`PreToolUse`, `PostToolUse`, `SessionStart`, …) | Mirror `.claude/settings.json` + enforce ICM `[SAI][PLAN]` before edits |
| Subagents (`agents` option) | `.claude/agents/<name>.md` + registry `agent_id` |
| MCP servers | `approved_capabilities[]` after owner Phase 3 |
| Plugins | Optional; record in tools.json if verified |

## Verification (Phase 5B extension)

After scaffold, contractor or Mimi must:

1. Run minimal SDK smoke test (read-only prompt, allowedTools `Read` only) and capture log under `.ai/runs/<task-id>/04_verify/output/agent-sdk-smoke.txt`.
2. Add capability to `runtimes/claude/tools.json`:

```json
{
  "id": "claude-agent-sdk",
  "kind": "sdk",
  "server": "anthropic",
  "tool": "@anthropic-ai/claude-agent-sdk",
  "status": "verified",
  "evidence": "query() smoke test exit 0; options loaded from config/agent-options.json",
  "verified_at": "YYYY-MM-DD"
}
```

`scripts/agent-verify-caps` does not auto-detect SDK yet — **manual verified entry with smoke evidence is required** until a verifier step lands.

## Contract Administrator rule

`scripts/agent-contract-scaffold --runtime claude` must point onboarding to:

- This reference
- `.ai/contracts/_templates/claude-contract-template.md` (SDK section)
- Per-agent `runtimes/claude/agent-sdk/README.md` created by scaffold or first ONBOARDING commit

Cora gap acknowledged 2026-07-17: prior Splunky/Mimi scaffolds used subagent files only; remediated via contract amendments + this reference.

## Dispatch (@mimi / @cora triggers)

Preferred architecture:

1. Slack Events / GitHub webhook → small Node or Python service using **Agent SDK** `query()`.
2. Prompt loads `.ai/agents/mimi/AGENT.md` + contract + task brief.
3. Hooks block writes without prior `[SAI][PLAN]` event id in prompt context.

Desktop project sessions remain valid for human-driven work; **automated** @mention dispatch requires SDK or documented OSS bridge with the same hook semantics.

## CI enforcement

`scripts/verify-agent-setup` runs on every push and PR (`agent-audit.yml`):

- Claude-primary agents: `runtimes/claude/agent-sdk/` scaffold present
- **Active** agents: ≥1 verified capability with evidence
- **Active** contracts with live contractors: non-empty `deliverables[]`

Set `SAI_CI_REQUIRE_SDK_SMOKE=1` in CI when Mimi (or any dispatcher) must show verified `claude-agent-sdk` before merge.
