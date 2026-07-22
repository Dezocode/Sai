# OpenClaw SAI Dashboard

**Contract:** `20260722-openclaw-dashboard-dezocode`  
**Agent:** Alfred (`ctr-code-alfred1`) — The OpenClaw Administrator  
**Branch:** `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap`

## Start (binding order)

1. [first-message-to-openclaw.md](../.ai/contracts/20260722-openclaw-dashboard-dezocode/first-message-to-openclaw.md) — paste on VPS OpenClaw
2. [CONTEXT.md](./CONTEXT.md) — product Layer 0
3. [ICM-HANDBOOK.md](./ICM-HANDBOOK.md) — master build handbook
4. [docs/icm-protocol-handbook.md](./docs/icm-protocol-handbook.md) — repo `.ai` protocol

## Scaffold layout (one folder per tab / settings page)

Each folder contains **CONTEXT.md** (requirements) + **BUILD.md** (how to build).

### Tabs

| Folder | Surface |
|---|---|
| [tabs/tracking/](./tabs/tracking/CONTEXT.md) | Live stock-market activity meter (15ms SLO) |
| [tabs/second-brain/](./tabs/second-brain/CONTEXT.md) | Obsidian-class vault + graph |
| [tabs/research/](./tabs/research/CONTEXT.md) | Research sessions + MCP |
| [tabs/chat-room/](./tabs/chat-room/CONTEXT.md) | Habbo 2D + Telegram PM |
| [tabs/github/](./tabs/github/CONTEXT.md) | Branch + CI failure rates |
| [tabs/config/](./tabs/config/CONTEXT.md) | OpenClaw config mirror |

### Settings

| Folder | Surface |
|---|---|
| [settings/auth/](./settings/auth/CONTEXT.md) | Auth hub (100% reachable) |
| [settings/host-health/](./settings/host-health/CONTEXT.md) | VPS + Gateway health |
| [settings/reporting-sop/](./settings/reporting-sop/CONTEXT.md) | Agent Slack reporting SOP |
| [settings/models/](./settings/models/CONTEXT.md) | Model / Telegram config |

### Apps & services

| Path | Role |
|---|---|
| [apps/desktop/](./apps/desktop/CONTEXT.md) | Mac client |
| [apps/ios-whisper/](./apps/ios-whisper/CONTEXT.md) | iPhone Whisper |
| [services/](./services/) | VPS backends (ingest, MCP, watch) |
| [integrations/composio/](./integrations/composio/README.md) | Composio toolkits |

Contract research: [research-integration-methods.md](../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md)

**Design (all tabs):** [design/DESIGN-LANGUAGE.md](./design/DESIGN-LANGUAGE.md) — unified Cursor + Activity Monitor + Robinhood; Chat tab full-screen immersive.

**Reviews:** [PR45-REVIEW-TRACKER.md](../.ai/contracts/20260722-openclaw-dashboard-dezocode/PR45-REVIEW-TRACKER.md) | [LAYERED-LOAD-ORDER.md](./docs/LAYERED-LOAD-ORDER.md)
