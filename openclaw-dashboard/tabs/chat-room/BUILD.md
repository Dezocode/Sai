# BUILD — Chat room tab

## Phase 1: Agent avatars

1. `assets/agents/<agent_id>/` sprite + metadata from registry.
2. Loader sync on registry.json change (webhook or poll).

## Phase 2: Room engine

1. Tilemap lobby + project-themed rooms.
2. Proximity detection → open chat panel.
3. Filter rooms by GitHub OAuth repos user can access.

## Phase 3: OpenClaw routing

1. Map avatar click → `sessionId` in gateway config.
2. Private room creates isolated session + Telegram handoff doc in UI.

## Phase 4: agent-presence service

1. WebSocket: position, room_id, agent_id.
2. Optional: show live status from tracking ingest.

## Phase 5: Telegram PM flow

1. Document pairing in UI when user enters private room.
2. Use OpenClaw `channels.telegram` — not duplicate bot outside Gateway.

Coordinate [A10](../../docs/agent-telegram-registry.md) for every registry agent.
