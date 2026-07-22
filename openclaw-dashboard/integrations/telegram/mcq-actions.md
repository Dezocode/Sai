# Telegram — multiple-choice action requests

**Integrations:** Composio Telegram + OpenClaw Telegram channel  
**UI mirror:** `McqActionCard` in dashboard bottom panel + iOS inbox

## Purpose

Responsive approval flows to **dezocode**, **monaecode**, and agents when:

- Auth provider down
- Fulfillment gate checkpoint
- Contract activation
- Smoke test failure
- Research cross-workspace share request
- Gateway config change (config-expert)

## Message format (Telegram)

```
🔔 SAI Action Required
Task: 20260722-…-alfred
Context: Auth hub — Composio Drive disconnected

Choose one:
1️⃣ Re-auth now (open dashboard link)
2️⃣ Defer 1h
3️⃣ Block and post [SAI][BLOCKED] to #agentupdates
```

Implementation: OpenClaw Telegram outbound + inline keyboard OR Composio telegram send with reply markup.

## Routing

| Recipient | Telegram | Fallback |
|---|---|---|
| dezocode | U0BHYH0NMCY mapped chat | Slack @mention |
| monaecode | U0BGNS7F0T1 mapped chat | Slack |
| Alfred | Bot DM verified (A10) | Queue `agent-report` |

## Dashboard mirror

When MCQ sent:

1. Ingest event → tracking tab pulse
2. `McqActionCard` in bottom panel with same options (Cursor buttons)
3. Answer syncs to VPS → resolves Telegram message edit

## Slack / GitHub automation

Parallel optional posts:

- `[SAI][BLOCKED]` or `[SAI][VERIFY]` to #agentupdates
- GitHub PR comment on bootstrap PR with MCQ summary (no secrets)

## Alfred smoke duty

`scripts/smoke-telegram-mcq.sh` — send test MCQ to dezocode sandbox chat; expect ack within 60s.

See [tests/smoke/telegram-mcq.sh](../../tests/smoke/telegram-mcq.sh).
