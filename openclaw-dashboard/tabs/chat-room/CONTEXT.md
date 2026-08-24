# Tab: Chat room — Habbo-style 2D agents (immersive full-screen)

| Field | Value |
|---|---|
| **Deliverable** | A6 |
| **Layout mode** | **`immersive-game`** — room fills screen like a video game |
| **Research** | [§7](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#7-habbo-clone-chat-room) |
| **Design** | [DESIGN-LANGUAGE.md](../../design/DESIGN-LANGUAGE.md) Mode B |
| **Services** | `services/agent-presence/` (VPS WebSocket) |
| **Desktop route** | `/chat-room` |

## Owner requirement

### Immersive game viewport (Mac + iOS)

The Chat tab is **not** a small panel widget. The 2D Habbo room **fills the screen**
within the dashboard — like the Habbo app — on **Mac desktop and iOS**:

- **Mac:** Phaser 3 canvas = full Tauri content area; minimal 35px room chrome; HUD overlays only
- **iOS:** Full-screen game viewport (SpriteKit or Phaser WKWebView); chat is a sheet overlay, not a substitute for the room
- **HUD chrome** (Rolodex, chat transcript, buttons) uses the **same unified design language** as all other tabs — 13px/28px Cursor tokens, not game-default UI fonts

### Agents + connections

- **2D character** per registered agent **and every OpenClaw subagent** (Alfred- or user-created)
- **Three-connection gate:** Telegram inbox + Slack intro with DM link + Habbo avatar (or BLOCKED)
- **Agent Rolodex** — all agents with status dot + **activity age** (live from VPS ingest)
- **Room types:** shared branch, GitHub project, **personal room** + **friends system**
- Walk-up chat (connected agents only); private room → **Telegram PM**

**Protocol:** [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md)

## Tech stack

| Layer | Choice |
|---|---|
| Renderer | Phaser 3 full viewport (Mac); Phaser WKWebView or SpriteKit full screen (iOS) |
| Shell | `ImmersiveGameShell` from design system |
| Presence | VPS WebSocket `services/agent-presence/` |
| Activity age | VPS `activity-ingest` WebSocket |
| Chat routing | OpenClaw session per agent |
| Telegram | OpenClaw Telegram channel + pairing |

## Dependencies

- A0 Gateway, A10 Telegram inbox verification
- Unified design tokens v2 (`design/tokens.json`)
- Registry sync

## Verification

- [ ] Chat tab enters `immersive-game` layout; canvas fills viewport on Mac and iOS
- [ ] HUD overlays use dashboard tokens — zero game-engine default UI fonts in chrome
- [ ] Every subagent passes three-connection gate
- [ ] Agent Rolodex shows 100% agents with live VPS activity age
- [ ] Personal room + friends list for each agent
- [ ] Walk-up chat round-trip < 3s LAN
- [ ] iOS full-screen room parity (not chat-only fallback)

Build: [BUILD.md](./BUILD.md) | Engine: [game-engine.md](./game-engine.md)
