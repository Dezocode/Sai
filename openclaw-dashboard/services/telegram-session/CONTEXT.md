# Service: Telegram session memory + contract sender reporting

**Protocol:** [telegram-session-protocol.md](../../docs/telegram-session-protocol.md)  
**Behaviors:** `.ai/agents/alfred/runtimes/openclaw/telegram/BEHAVIORS.md`

## Responsibility

- Persist VPS session state per Telegram `chat_id`
- On ICM stage hooks: format + send Telegram update to contract sender
- Mirror to Slack via OpenClaw channel or `scripts/agent-report`
- Write redacted `telegram-session.jsonl` into `.ai/runs/<task-id>/`

## VPS paths

- State: `~/.openclaw/sessions/<agent_id>/<chat_id>/`
- Config: OpenClaw `agents.<agent_id>.telegram` in `openclaw.json`

## Build

See [BUILD.md](./BUILD.md)
