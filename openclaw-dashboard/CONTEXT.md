# OpenClaw SAI Dashboard — Layer 0 (product ICM)

You are inside the **OpenClaw SAI Dashboard** product tree (`openclaw-dashboard/`),
contract **`20260722-openclaw-dashboard-dezocode`**, agent **Alfred**
(`ctr-code-alfred1`).

This product implements ICM locally: each **tab** and **settings page** is a
folder with `CONTEXT.md` (what/why) and `BUILD.md` (how). The repo-wide SAI
Layer 0 remains `.ai/CONTEXT.md`.

## Governed scope

| Scope | Path |
|---|---|
| Canonical repo | `Dezocode/Sai` |
| Fork | `monaecode/Sai` (sync by SHA) |
| Product root | `openclaw-dashboard/` |
| Bootstrap branch | `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap` |
| Contract | `.ai/contracts/20260722-openclaw-dashboard-dezocode/` |
| Master handbook | [ICM-HANDBOOK.md](./ICM-HANDBOOK.md) |
| Protocol deep-dive | [docs/icm-protocol-handbook.md](./docs/icm-protocol-handbook.md) |

## Runtime

**OpenClaw-primary** on Hostinger VPS (`openclaw-gateway-vps`). Not Cursor-primary.
Entry: repo `OPENCLAW.md` → Alfred first message in contract.

## Design system (unified Cursor + Obsidian)

All tabs share one language: [design/DESIGN-LANGUAGE.md](./design/DESIGN-LANGUAGE.md)

- Tokens: [design/tokens.json](./design/tokens.json)
- Mac: Tauri 2 + React | iOS: SwiftUI + WhisperFlow + TTS
- Habbo chat: [tabs/chat-room/game-engine.md](./tabs/chat-room/game-engine.md)
- Smoke gates: [tests/smoke/all-gates.sh](./tests/smoke/all-gates.sh)

## Tab map (each folder = one dashboard surface)

| Folder | UI surface | Deliverable |
|---|---|---|
| [tabs/tracking/](./tabs/tracking/CONTEXT.md) | Live stock-market activity meter | A3 |
| [tabs/second-brain/](./tabs/second-brain/CONTEXT.md) | Obsidian-class vault + graph | A4 |
| [tabs/research/](./tabs/research/CONTEXT.md) | Research sessions + MCP gateway | A5 |
| [tabs/chat-room/](./tabs/chat-room/CONTEXT.md) | Habbo-style 2D agents + Telegram PM | A6 |
| [tabs/github/](./tabs/github/CONTEXT.md) | Branch + CI dashboard | A8 |
| [tabs/config/](./tabs/config/CONTEXT.md) | OpenClaw config mirror | A7 |

## Settings map

| Folder | UI surface | Deliverable |
|---|---|---|
| [settings/auth/](./settings/auth/CONTEXT.md) | Auth hub (GitHub, Composio, OAuth) | A11 |
| [settings/host-health/](./settings/host-health/CONTEXT.md) | VPS + Gateway health | A0 |
| [settings/reporting-sop/](./settings/reporting-sop/CONTEXT.md) | Agent session Slack SOP | A1 |
| [settings/models/](./settings/models/CONTEXT.md) | LLM / channel model config | A7 |

## Apps (cross-tab shells)

| Folder | Platform | Deliverable |
|---|---|---|
| [apps/desktop/](./apps/desktop/CONTEXT.md) | Mac desktop client | A9 |
| [apps/ios-whisper/](./apps/ios-whisper/CONTEXT.md) | iPhone Whisper companion | A9 |

## Hard gates (dezocode)

- **100% production** smoke — zero blocking errors on approved flows
- **p99 ≤ 15ms** host CLI → dashboard tab (`scripts/verify-ingest-latency.sh`)
- **ICM + Sai** verification before merge to `main`

## Load order (Alfred bootstrap)

1. Contract `first-message-to-openclaw.md`
2. This file → `ICM-HANDBOOK.md`
3. Tab/settings `CONTEXT.md` for the surface you are building
4. Matching `BUILD.md` before implementation
5. `.ai/runs/<task-id>/` for every executed stage (repo-wide ICM)
