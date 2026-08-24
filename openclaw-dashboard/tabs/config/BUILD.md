# BUILD — Config tab

## Phase 1: config-expert subagent

1. Create `openclaw-dashboard/.openclaw/agents/config-expert.md`.
2. Persona: OpenClaw configuration specialist; cites docs.openclaw.ai.
3. Register in Gateway agents map.

## Phase 2: Config API on VPS

1. Read endpoint: sanitized config (secrets redacted).
2. Write endpoint: validate JSON5 → write `openclaw.json` → reload gateway.
3. Require cofounder role OR config-expert session approval token.

## Phase 3: Desktop mirror UI

1. Sections: channels, models, agents, skills, cron.
2. Diff view before apply.
3. Chat panel to invoke config-expert inline.

## Phase 4: Telegram model wiring

1. Link to `settings/models/` for provider selection.
2. Test message button (uses OpenClaw Telegram channel).
