# Settings: Auth hub

| Field | Value |
|---|---|
| **Deliverable** | A11 |
| **Research** | [§12](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#12-dashboard-auth-hub) |
| **Desktop route** | `/settings/auth` |

## Owner requirement

**100% reachable** auth flows from dashboard when Gateway healthy:

- GitHub account linking (humans)
- Composio Connect (Telegram, Google Drive, Gemini Notebook)
- Telegram bot token + pairing entry
- OpenClaw Gateway token / Tailscale identity
- Live **browser MCP** surface for OAuth consent in desktop client

## Tech stack

| Provider | Method |
|---|---|
| GitHub | OAuth App → JWT session |
| Composio | Connect Link / sessions.create |
| Browser MCP | Embedded webview + CDP on VPS bridge |

Build: [BUILD.md](./BUILD.md)
