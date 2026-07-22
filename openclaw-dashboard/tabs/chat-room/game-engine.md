# Habbo chat room — game engine spec

**Tab:** [tabs/chat-room/](../chat-room/CONTEXT.md)  
**Design:** Cursor panel chrome wrapping Phaser 3 canvas

## Engine choice

| Platform | Engine | Notes |
|---|---|---|
| macOS desktop | **Phaser 3** in Tauri webview panel | Full walk-up, multi-room |
| iOS companion | **SpriteKit** simplified room OR Phaser via WKWebView | Same avatar assets; chat-first on small screens |

## Room generator ("Habbo clone")

Service: `services/agent-presence/room-generator.ts`

```
Input:  registry agents[], user's GitHub repos[], room template id
Output: room JSON (tiles, spawn points, agent positions, door links)
```

### Room templates

| Template | Scope | Agents shown |
|---|---|---|
| `lobby-sai` | All **connected** registry + subagents | Full roster avatars |
| `branch/<branch-name>` | Shared git branch | Agents assigned to branch |
| `proj-<slug>` | GitHub project | Contract contractors + staff |
| `repo-dezocode-main` | Dezocode/Sai main | CEO, CTO, staff |
| `repo-monaecode-fork` | monaecode/Sai | Mimi, fork contractors |
| `personal/<agent_id>` | Agent personal room + **friends** | Owner agent + friended users/agents |
| `private-dm` | 2 parties | User + one agent → Telegram handoff |

**Rule:** Every subagent gets `personal/<agent_id>` on create + placement in `lobby-sai` when connected (see [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md)).

Generator reads `.ai/agents/registry.json`, `.openclaw/agents/*.md`, and `.ai/projects/*/branches-index.json`.

## Avatar pipeline

- `assets/agents/<agent_id>/sprite.png` (32×64 placeholder → replace in BUILD)
- Fallback: colored capsule + initials (Cursor accent colors)
- Click → `ChatTranscript` panel + OpenClaw session route
- Walk-up proximity: 2 tile radius triggers chat

## Telegram coordination

Every subagent **must** have dedicated Telegram inbox before `connected` status.

Private / personal room flow:

1. OpenClaw creates Telegram session route per agent
2. Agent posts Slack intro with **Telegram DM link** (public channel)
3. UI shows pairing QR / deep link in Agent Rolodex
4. Messages sync: in-game bubble + Telegram DM

## Agent Rolodex + friends

Sidebar list of **all agents** with status dot + **activity age** (Cursor typography).
See [agent-rolodex.md](./agent-rolodex.md).

- **Friends system** — users/agents friend each other; personal rooms listed
- Disconnected agents: gray avatar in lobby, no walk-up until three-connection gate passes

## TTS in room

Agent text replies → `TtsPlayer` (Mac NSSpeech / iOS AVSpeech)  
User setting: `responsive TTS` — speak on every agent message in room + inbox

## Design compliance

- Game canvas bordered like Cursor panel (`#252526` bg, `#3c3c3c` border)
- Chat overlay uses `ChatTranscript` tokens — not game-engine default UI font

Build phases: [BUILD.md](./BUILD.md)
