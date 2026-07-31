# Composio Telegram connector (dashboard toolkits)

**Deliverable:** A2 — Composio connections  
**Native path:** OpenClaw Telegram channel handles agent DM / contract-sender reporting (already live).  
**This connector:** Dashboard-only CRUD for Telegram toolkits via Composio (auth hub, not the bot layer).

## Dual-path Telegram

| Layer | Purpose | Runtime | Token / Key |
|---|---|---|---|
| **OpenClaw native Telegram** | Agent sessions, contract-sender reporting, heartbeat notifications | OpenClaw Gateway | `TELEGRAM_BOT_TOKEN` in `/etc/openclaw/sai.env` |
| **Composio `telegram` toolkit** | Dashboard CRUD: send messages, fetch history, manage groups from `/settings/auth` | Composio sessions | `COMPOSIO_API_KEY` in `/etc/openclaw/sai.env` + user OAuth |

These paths are **complementary**, not replacements. Agent reporting always uses the OpenClaw native bot.

## Files

- `connector.js` — stub; loads `COMPOSIO_API_KEY` from env, exposes `connect()`, `listChats()`, `sendMessage()`.
- No env files in repo; only the variable name `COMPOSIO_API_KEY` is referenced.

## Auth flow

1. Dashboard Auth hub → **Connect Telegram** → `composio sessions.create` with the `telegram` toolkit.
2. User completes OAuth in an embedded browser or Composio Connect Link.
3. VPS stores the connection entity in Composio cloud; tokens never commit to Git.
4. Tile updates from `Pending` → `Connected` or `Blocked`.

## Verification

- [ ] Live test call after dezocode toolkit approval.
- [ ] `openclaw-dashboard/scripts/verify-secrets-compliance.sh` PASS.
