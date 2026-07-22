# Habbo chat room — game engine spec (full-screen immersive)

**Tab:** [CONTEXT.md](./CONTEXT.md)  
**Design:** [DESIGN-LANGUAGE.md](../../design/DESIGN-LANGUAGE.md) Mode B + [components.md](../../design/components.md) `ImmersiveGameShell`

## Layout: full-screen game within dashboard

The chat room is a **video-game-style viewport**, not a Cursor editor panel.

| Platform | Viewport | Chrome |
|---|---|---|
| **macOS** | Phaser 3 scales to **entire** Tauri window content below 35px tab/room bar | `ImmersiveGameShell` HUD overlays |
| **iOS** | Phaser (WKWebView) or SpriteKit **edge-to-edge** in Chat tab safe area | Rolodex slide panel + chat sheet |

Sidebar collapses automatically in `immersive-game` mode. Activity bar stays visible for tab switching.

## Engine choice

| Platform | Engine | Notes |
|---|---|---|
| macOS desktop | **Phaser 3** full viewport | Walk-up, multi-room, scale-to-fit isometric |
| iOS companion | **Phaser via WKWebView** or **SpriteKit** full screen | Same avatar assets; room fills screen; chat sheet overlay |

## Room generator

Service: `services/agent-presence/room-generator.ts` (VPS)

```
Input:  registry agents[], user's GitHub repos[], room template id
Output: room JSON (tiles, spawn points, agent positions, door links)
```

### Room templates

| Template | Scope |
|---|---|
| `lobby-sai` | All connected registry + subagents |
| `branch/<branch-name>` | Shared git branch |
| `proj/<slug>` | GitHub project |
| `personal/<agent_id>` | Agent personal room + friends |
| `private-dm` | User + one agent → Telegram handoff |

## Avatar pipeline

- `assets/agents/<agent_id>/sprite.png` (32×64)
- Disconnected: gray sprite; no walk-up until three-connection gate passes
- Walk-up proximity: 2 tile radius → bottom `ChatTranscript` HUD (dashboard tokens)

## HUD overlay rules (mandatory)

Game canvas may use pixel art. **All chrome must use dashboard design system:**

| HUD element | Component | Tokens |
|---|---|---|
| Agent list | `AgentRolodex` | 28px rows, 13px/11px, 6px dots |
| Chat | `ChatTranscript` | 13px body, max 40vh |
| Room bar | `TabBar` subset | 35px height |
| Buttons | `CursorButton` | 28px — back, friends, Telegram link |

No Phaser DOM text for HUD — render React/SwiftUI overlays above canvas.

## Live VPS data

- Presence positions: `presence/stream` WebSocket
- Rolodex activity age: `ingest/stream` per `agent_id`
- Room agent list: registry poll 60s + presence push

## Telegram + Rolodex

See [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md) and [agent-rolodex.md](./agent-rolodex.md).

Build phases: [BUILD.md](./BUILD.md)
