# BUILD — Chat room tab

## Phase 0: Subagent protocol + Rolodex UI

1. Implement `AgentRolodex` per [agent-rolodex.md](./agent-rolodex.md) — Cursor tokens only.
2. Wire activity age from `activity-ingest` WebSocket.
3. Alfred hook: on subagent create → [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md).

## Phase 1: Agent avatars

1. `assets/agents/<agent_id>/` sprite + metadata from registry **and** `.openclaw/agents/`.
2. Loader sync on registry + subagent file changes.
3. **Disconnected** agents: gray sprite in rolodex; no lobby walk-up until connected.

## Phase 2: Room engine

1. Tilemap: `lobby-sai`, `branch/*`, `proj/*`, `personal/<agent_id>`.
2. Proximity detection → open chat panel.
3. **Friends panel** — same row component as rolodex; door link to personal rooms.
4. Filter branch/project rooms by GitHub OAuth repos.

## Phase 3: OpenClaw routing + Telegram

1. Map avatar click → `sessionId` in gateway config.
2. **Every subagent:** provision Telegram inbox; record `telegram_dm_link`.
3. Post Slack `[SAI][INTRO]` with DM link via Alfred automation.
4. Private room → Telegram handoff.

## Phase 4: agent-presence service

1. WebSocket: position, room_id, agent_id, connection_status.
2. Feed Rolodex activity age + busy/idle from ingest.

## Phase 5: iOS parity

1. SwiftUI `AgentRolodexView` — identical 28px rows, 6px status dots, 13px/11px fonts.
2. Friends list + simplified Habbo or chat sheet.

## Phase 6: Smoke

`tests/smoke/subagent-connection-gate.sh` — must PASS before org onboarding.

Coordinate [agent-telegram-registry.md](../../docs/agent-telegram-registry.md) for **every** agent and subagent.
