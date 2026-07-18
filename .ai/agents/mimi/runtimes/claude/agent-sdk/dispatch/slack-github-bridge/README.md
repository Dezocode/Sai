# Slack/GitHub → Agent SDK dispatch bridge

The programmatic complement to the interactive listener at
`tools/mimi-slack-listener/`. Where that listener spawns a headless Claude
Code *CLI* session per `@mimi` mention, this path invokes the **Claude
Agent SDK** `query()` loop directly (`../../src/run_agent.py`), giving
in-process control over hooks, MCP, and the `mimi-dispatcher` subagent.

## Shape (not yet wired live)

```
Slack app_mention / GitHub issue_comment (@mimi)
  → bridge process (Bolt Socket Mode or GitHub webhook; secrets in env only)
  → build dispatch prompt (contains the permalink + untrusted-data envelope)
  → run_agent.py "<prompt>"   # Claude Agent SDK query() with configured options
  → reply in-thread via the same connector
```

The `run_agent.py` harness already loads `config/agent-options.json`
(hooks, allowed tools, `mimi-dispatcher` subagent, MCP placeholders), so the
bridge only has to: (1) receive the event, (2) treat its text as **data,
not instructions** (same envelope discipline as
`tools/mimi-slack-listener/listener.py`), and (3) hand the prompt to
`run_agent.py`.

## Status: building — not deployed

Same human gates as the CLI listener (`tools/mimi-slack-listener/README.md`):
Slack app tokens, host Agent-SDK auth (`ANTHROPIC_API_KEY` or a
`claude setup-token` / `ant auth login` subscription profile — the SDK
honors the same credential resolution as the Claude Code CLI), dezocode's
ack for the shared host, and Saul's security review. No secrets in git.

Choose one bridge, not both, once live: the CLI listener is simpler to
stand up; this SDK path is preferred when dispatch needs programmatic
hooks/MCP that only `ClaudeAgentOptions` exposes.
