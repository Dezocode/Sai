# Agent Rolodex — chat tab sidebar

**Component:** `AgentRolodex` (see [design/components.md](../../design/components.md))  
**Protocol:** [subagent-onboarding-protocol.md](../../docs/subagent-onboarding-protocol.md)

## Purpose

Single scrollable list of **every** agent in `.ai/agents/registry.json` plus
user-created OpenClaw subagents — with live status and **activity age**.

## Layout (Cursor style — desktop & iOS)

```
┌─ Agent Rolodex ──────────────┐
│ 🔍 [Search agents...]        │  ← CursorInput 28px
├──────────────────────────────┤
│ ● Alfred          2m    📱 🚪│  ← row 28px + 4px pad
│ ● config-expert   1h    📱 🚪│
│ ○ research-coord  3d    📱 — │  ← disconnected gray dot
│ ...                          │
└──────────────────────────────┘
```

| Element | Token |
|---|---|
| Row height | 28px (`spacing.unit * 7`) |
| Name | 13px medium `text.primary` |
| Activity age | 11px mono `text.secondary` |
| Status dot | 6px — green `#89d185` connected, gray `#6e6e6e` off, amber `#cca700` busy |
| Icons | 16px — Telegram 📱, room door 🚪 (use SF Symbol on iOS) |

## Data model

```typescript
interface RolodexEntry {
  agent_id: string;
  display_name: string;
  connection_status: 'connected' | 'disconnected' | 'blocked';
  activity_age_ms: number;       // from activity-ingest
  telegram_dm_link: string;
  slack_intro_permalink?: string;
  habbo_room_ids: string[];
  personal_room_id: string;    // personal/<agent_id>
  friends_count: number;
}
```

## Interactions

| Action | Result |
|---|---|
| Click row | Select agent; show detail panel |
| Click 📱 | Open Telegram DM (external or in-app if paired) |
| Click 🚪 | Jump Habbo canvas to agent's personal or primary room |
| Click **Add friend** | Cursor secondary button — adds to user's friends list |
| Right-click / long-press | Invite to private room → Telegram handoff |

## Friends panel (sub-view)

- Lists agents user has friended
- Tiny status + activity age on each row (same typography)
- **Friends** tab uses identical row component — no alternate styling

## Sync sources

- Registry poll (60s)
- activity-ingest WebSocket (activity age realtime)
- presence service (room location)
- Alfred subagent webhook on create/update

Build: [BUILD.md](./BUILD.md) Phase 3
