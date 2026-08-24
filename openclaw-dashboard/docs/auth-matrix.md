# Auth matrix — providers × status (no secret values)

**Security:** [secrets-security.md](./secrets-security.md)  
**Updated by:** Alfred on VPS bootstrap — commit **status only**, never values.

| provider | env_var(s) | vps_store | dashboard_route | status | owner | last_rotated | notes |
|---|---|---|---|---|---|---|---|
| openclaw_gateway | `OPENCLAW_GATEWAY_TOKEN` | `/etc/openclaw/sai.env` | /settings/secrets | pending | alfred | — | Loopback bind 127.0.0.1 |
| telegram_bot | `TELEGRAM_BOT_TOKEN` | `/etc/openclaw/sai.env` | /settings/auth | pending | alfred | — | Pairing per agent_id |
| slack_socket | `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN` | `/etc/openclaw/sai.env` | /settings/secrets | pending | alfred | — | Socket Mode |
| composio | `COMPOSIO_API_KEY` | Composio cloud | /settings/auth | pending | dezocode | — | MCQ before enable |
| github_oauth | `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET` | `/etc/openclaw/sai.env` | /settings/auth | pending | dezocode | — | Secret VPS-only |
| sai_reporting | `SAI_SLACK_BOT_TOKEN` | VPS + GitHub Actions secret | — | pending | dezocode | — | Not in repo |
| tailscale | `TAILSCALE_AUTH_KEY` | `/etc/openclaw/sai.env` | /settings/secrets | optional | dezocode | — | Remote dashboard |
| gemini_notebook | via Composio Google AI | Composio | /settings/auth | pending | dezocode | — | Export ingest only |

### Status values

- `pending` — not yet provisioned on VPS
- `connected` — verified health check PASS
- `blocked` — documented remediation in auth-matrix notes
- `optional` — not required for MVP fulfillment

### Rules

1. Alfred updates **status** and **last_rotated** columns only in Git commits
2. Values live exclusively on VPS per [secrets-store.schema.json](../../.ai/agents/alfred/runtimes/openclaw/gateway/config/secrets-store.schema.json)
3. Dashboard UI reads status via health API — never returns secret values to client logs
