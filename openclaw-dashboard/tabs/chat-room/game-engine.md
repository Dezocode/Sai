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
| `lobby-sai` | All registry agents | Full roster avatars |
| `proj-<slug>` | One project_slug | Assigned contractors only |
| `repo-dezocode-main` | Dezocode/Sai main | CEO, CTO, staff |
| `repo-monaecode-fork` | monaecode/Sai | Mimi, fork contractors |
| `private-dm` | 2 parties | User + one agent → Telegram handoff |

Generator reads `.ai/agents/registry.json` + `.ai/projects/*/branches-index.json`.

## Avatar pipeline

- `assets/agents/<agent_id>/sprite.png` (32×64 placeholder → replace in BUILD)
- Fallback: colored capsule + initials (Cursor accent colors)
- Click → `ChatTranscript` panel + OpenClaw session route
- Walk-up proximity: 2 tile radius triggers chat

## Telegram coordination

Private room creation:

1. OpenClaw creates Telegram session route
2. UI shows pairing QR / deep link
3. Messages sync: in-game bubble + Telegram DM (A10 verified inbox)

## TTS in room

Agent text replies → `TtsPlayer` (Mac NSSpeech / iOS AVSpeech)  
User setting: `responsive TTS` — speak on every agent message in room + inbox

## Design compliance

- Game canvas bordered like Cursor panel (`#252526` bg, `#3c3c3c` border)
- Chat overlay uses `ChatTranscript` tokens — not game-engine default UI font

Build phases: [BUILD.md](./BUILD.md)
