# Auth providers — Apple, GitHub, Composio

**Settings surface:** [settings/auth/](../settings/auth/CONTEXT.md)  
**Design:** [design/DESIGN-LANGUAGE.md](../design/DESIGN-LANGUAGE.md) → `EmbeddedBrowser`

## Provider matrix

| Provider | Desktop | iOS | VPS secret | Dashboard UI |
|---|---|---|---|---|
| **GitHub** | OAuth App + PKCE | ASWebAuthenticationSession | client secret on VPS | Primary identity; repo scope |
| **Sign in with Apple** | OAuth via web + native bridge | Native Sign in with Apple | Apple key on VPS | Optional link to GitHub user |
| **Composio Telegram** | Connect Link + EmbeddedBrowser | SFSafariView → deep link | Composio API key VPS | Toolkit tile |
| **Composio Google Drive** | Same | Same | Same | Toolkit tile |
| **Composio Gemini/Notebook** | Same + export import | Same | Same | Toolkit tile |
| **OpenClaw Gateway** | Token / pairing QR | Node pairing | `~/.openclaw/` VPS | Host health link |

## GitHub (required)

- Scopes: `read:user`, `repo` (or fine-grained: contents read, actions read)
- Maps user → dezocode vs monaecode workspace access in research tab
- Session JWT issued by VPS auth service; desktop/iOS store Keychain only

## Sign in with Apple

- Services ID + key on VPS
- Link Apple `sub` to GitHub account row after first login
- iOS: native button in auth settings (Human Interface Guidelines layout)

## Composio

- `composio sessions.create` with MCP enabled
- Each toolkit: Connected | Pending | Blocked tile (Cursor settings row style)
- OAuth completion via EmbeddedBrowser → VPS callback → WebSocket notify desktop

## Live browsing (full-featured)

1. **Desktop:** `EmbeddedBrowser` component streams VPS browser (Playwright CDP).
2. **iOS:** OAuth via SFSafariView; authenticated browse via WKWebView + VPS proxy.
3. Auth toolbar shows: GitHub ● Apple ○ Composio ● Gateway ● (live status dots)

## 100% availability gate

Auth hub health check runs every 60s; any required provider unreachable → status bar warning + Telegram MCQ to dezocode (see mcq-actions.md).

Build: [settings/auth/BUILD.md](../settings/auth/BUILD.md)
