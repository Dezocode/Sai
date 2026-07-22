# Tab: Chat room — Habbo-style 2D agents

| Field | Value |
|---|---|
| **Deliverable** | A6 |
| **Research** | [§7](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#7-habbo-clone-chat-room) |
| **Services** | `services/agent-presence/` |
| **Desktop route** | `/chat-room` |

## Owner requirement

- **2D character** per registered agent in `.ai/agents/registry.json`
- User walks up to avatar → direct chat
- Rooms scoped to auth'd user's GitHub view (Dezocode/Sai main vs monaecode fork projects)
- Private room → **Telegram PM** via OpenClaw messaging
- Model config for Telegram in integrated chat section

## Tech stack

| Layer | Choice |
|---|---|
| Renderer | Phaser 3 or PixiJS in Electron/Tauri |
| Presence | WebSocket `services/agent-presence/` |
| Chat routing | OpenClaw session per agent |
| Telegram | OpenClaw Telegram channel + pairing |

## Dependencies

- A0 Gateway, A10 Telegram inbox verification
- A7 model config for channel models
- Registry sync

## Verification

- [ ] Walk-up chat round-trip < 3s LAN
- [ ] Private room message on paired Telegram
- [ ] Room filter respects GitHub OAuth repo scope

Build: [BUILD.md](./BUILD.md)
