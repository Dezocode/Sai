# Tab: Chat room — Habbo-style 2D agents

| Field | Value |
|---|---|
| **Deliverable** | A6 |
| **Research** | [§7](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#7-habbo-clone-chat-room) |
| **Services** | `services/agent-presence/` |
| **Desktop route** | `/chat-room` |

## Owner requirement

- **2D character** per registered agent **and every OpenClaw subagent** (Alfred- or user-created)
- **Three-connection gate:** Telegram inbox + Slack intro with DM link + Habbo avatar (or BLOCKED)
- **Agent Rolodex** — all agents listed with status dot + **activity age** (Cursor 13px/11px mono)
- **Room types:** shared branch, GitHub project, **personal room** + **friends system**
- User walks up to avatar → direct chat (connected agents only)
- Private room → **Telegram PM** via OpenClaw messaging
- **Same Cursor buttons/font/spacing** on Mac desktop and iOS (see [agent-rolodex.md](./agent-rolodex.md))

**Protocol:** [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md)

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

- [ ] Every subagent passes three-connection gate (TG + Slack intro + Habbo)
- [ ] Agent Rolodex shows 100% agents with activity age
- [ ] Personal room + friends list for each agent
- [ ] Walk-up chat round-trip < 3s LAN
- [ ] Private room message on paired Telegram
- [ ] iOS rolodex matches desktop tokens

Build: [BUILD.md](./BUILD.md)
