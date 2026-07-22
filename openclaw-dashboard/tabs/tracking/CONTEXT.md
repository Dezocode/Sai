# Tab: Tracking — live activity meter

| Field | Value |
|---|---|
| **Deliverable** | A3 |
| **Contract research** | [§4](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#4-tracking-tab-live-activity-meter) |
| **Services** | `services/activity-ingest/` |
| **Desktop route** | `/tracking` |

## Owner requirement (dezocode)

Stock-market-style **live graph** at millisecond resolution for:

- All agents in `.ai/agents/registry.json`
- All automations (OpenClaw cron, Cursor automations metadata)
- GitHub agent activity on **Dezocode/Sai** and **monaecode/Sai**
- Slack workspace activity (public channels, agent posts)
- OpenClaw Gateway sessions

**Hard SLO:** host admin CLI → tab render **p99 ≤ 15ms** (see `scripts/verify-ingest-latency.sh`).

## Tech stack

| Layer | Choice |
|---|---|
| Ingest | Node/Bun service on VPS, WebSocket server |
| Storage | SQLite + WAL (start); optional TimescaleDB |
| UI chart | lightweight-charts (TradingView-style) |
| Desktop | React panel in `apps/desktop/src/tabs/tracking/` |

## Dependencies

- **Requires:** A0 host health, A1 reporting SOP ingest, activity-ingest service
- **Feeds:** none (leaf UI for monitoring)
- **Blocks:** A8 github tab (shares ingest pipeline)

## ICM runs

One task-id per phase: ingest backend, desktop UI, Slack/GitHub connectors.
Post `[SAI][PLAN]` before each.

## Verification

- [ ] Synthetic events visible on graph < 15ms p99
- [ ] Registry agent activity appears when `[SAI][EVENT]` posted
- [ ] GitHub webhook test populates CI bucket
- [ ] UI legend documents source resolution honestly

Build steps: [BUILD.md](./BUILD.md)
