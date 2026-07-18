# Claude Agent SDK — Mimi dispatcher

Contract: `20260717-mimi-dispatcher-bootstrap-monaecode` (when merged)  
Reference: `.ai/shared/references/claude-agent-sdk.md`

## Required for @mimi Slack/GitHub dispatch

1. **`dispatch/` service** — Node or Python using `@anthropic-ai/claude-agent-sdk` / `claude-agent-sdk`.
2. **`config/agent-options.json`** — hooks (`PreToolUse` / `PostToolUse`), MCP (GitHub, Slack), subagents (`mimi-dispatcher`).
3. **Smoke test** — read-only `query()` log → `.ai/runs/<task-id>/04_verify/output/agent-sdk-smoke.txt`.
4. **tools.json** — `claude-agent-sdk` capability with evidence (verifier does not auto-detect yet).

Desktop project + `.claude/agents/mimi-dispatcher.md` remain human-interactive entry points; **automated** @mention handling must go through the SDK harness.

## Layout (M0 implemented on this branch)

```
agent-sdk/
  README.md                     # this file
  pyproject.toml                # pins claude-agent-sdk>=0.1.0 (Python >=3.10)
  src/run_agent.py              # query() entrypoint: --check | --smoke | "<prompt>"
  config/agent-options.json     # ClaudeAgentOptions (tools, hooks, subagent, MCP)
  dispatch/slack-github-bridge/ # bridge design → run_agent.py (not deployed)
```

## Run

```bash
pip install -e .ai/agents/mimi/runtimes/claude/agent-sdk    # or: pip install claude-agent-sdk
python .ai/agents/mimi/runtimes/claude/agent-sdk/src/run_agent.py --check   # offline, no auth
python .ai/agents/mimi/runtimes/claude/agent-sdk/src/run_agent.py --smoke   # live, needs auth
python .ai/agents/mimi/runtimes/claude/agent-sdk/src/run_agent.py "<dispatch prompt>"
```

**Auth:** the Agent SDK honors the same credential resolution as the Claude
Code CLI — `ANTHROPIC_API_KEY`, or a subscription-backed `claude setup-token`
/ `ant auth login` profile. It does **not** require metered API tokens. No
key is committed or read from the repo.

## Status (honest)

`--check` PASSES against SDK v0.2.121 (import OK, options build, subagent
resolved). `--smoke` reaches the CLI subprocess and stops only at headless
auth in this session. `claude-agent-sdk` is recorded `building` in
`../tools.json`; promote to `verified` only after an authenticated exit-0
smoke, per Sai's instruction. Evidence:
`.ai/runs/20260717-0229-mimi-dispatcher-bootstrap-mimi/04_verify/output/agent-sdk-smoke.txt`.
