# Composio auth flow

**Deliverable:** A2 — Composio connections  
**Settings:** [settings/auth/HUB.md](../settings/auth/HUB.md)  
**Provider matrix:** [auth-matrix.md](./auth-matrix.md) | [providers.md](../settings/auth/providers.md)

## Secrets

All values live on the VPS only (`/etc/openclaw/sai.env`):

- `COMPOSIO_API_KEY` — Composio account API key (never in Git)

Only the variable name appears in this repo.

## Connect Link flow

1. Dashboard Auth hub shows the **Composio** provider tile.
2. User clicks **Connect** → backend calls `composio sessions.create` with the MCP/toolkit list.
3. Composio returns a Connect Link URL.
4. Embedded browser or desktop browser opens the link; the user completes OAuth for each toolkit.
5. Composio stores the connection; the dashboard polls status until `Connected` or `Blocked`.
6. The VPS never stores toolkit tokens in the repo; only connection status and env var name are tracked.

## Dual-path Telegram

| Path | Purpose | Runtime | Token / Key |
|---|---|---|---|
| **OpenClaw native Telegram** | Agent DMs, contract-sender reporting, heartbeat notifications | OpenClaw Gateway | `TELEGRAM_BOT_TOKEN` in `/etc/openclaw/sai.env` |
| **Composio `telegram` toolkit** | Dashboard CRUD (send messages, history, groups) from `/settings/auth` | Composio sessions | `COMPOSIO_API_KEY` in `/etc/openclaw/sai.env` |

These paths are **complementary**, not replacements. Agent reporting and contract-sender messaging always use the OpenClaw native Telegram channel.

## Supported toolkits (A2)

- `telegram` — dashboard Telegram CRUD
- `googledrive` — second-brain Drive mirror
- `googleai` / NotebookLM — export/import pipeline (no live write API)

## Troubleshooting

- `Blocked` tile → documented in `auth-matrix.md` notes; open ticket for owner OAuth.
- `Pending` tile → waiting for Connect Link completion or dezocode toolkit approval.
