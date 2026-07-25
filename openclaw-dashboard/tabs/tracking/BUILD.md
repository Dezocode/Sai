# BUILD — Tracking tab

## Phase 0: Design system bootstrap

1. Generate CSS vars from `design/tokens.json` into `apps/desktop/src/design-system/tokens.css`
2. Implement `AppShell`, `TabBar`, `LiveGraph` before tab-specific logic
3. Run `tests/smoke/design-tokens.sh`

## Phase 1: Ingest service (`services/activity-ingest/`)

1. Create WebSocket endpoint `/activity/stream` on VPS (port behind reverse proxy).
2. Define event schema: `{ ts_ms, source, agent_id?, repo?, channel?, event_type, payload }`.
3. Implement host admin CLI emitter binary/script — **authoritative low-latency source**.
4. Add Slack ingest (OpenClaw Slack channel or Events API relay).
5. Add GitHub App webhook handler for both repos.
6. Poll registry + `.ai/runs/*` for agent stage transitions.

**Verify:** `verify-ingest-latency.sh --slo-ms 15` PASS on VPS.

## Phase 2: Desktop UI (`apps/desktop/src/tabs/tracking/`)

1. WebSocket client with reconnect + backfill buffer.
2. lightweight-charts: multi-series (agents, github, slack, automations).
3. Millisecond axis where CLI-sourced; aggregate external APIs with label.
4. Stock-ticker style header: events/sec, last latency, p99 badge.

## Phase 3: Reporting SOP linkage

1. Parse `[SAI][EVENT]` posts into ingest (settings/reporting-sop).
2. Dashboard row links to Slack thread permalink.

## Phase 4: Smoke

Add `tests/smoke/tracking.sh` — connect WS, emit 1000 CLI events, assert p99.

## Coordination notes

- Do **not** block UI on slow external APIs — CLI stream must meet 15ms alone.
- Coordinate with `tabs/github/` on shared GitHub webhook secret (VPS env).
