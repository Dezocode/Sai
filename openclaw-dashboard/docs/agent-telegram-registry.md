# Agent Telegram + connection registry (A10)

**Protocol:** [subagent-onboarding-protocol.md](./subagent-onboarding-protocol.md)

Every OpenClaw subagent (Alfred-created, user-created, registry) must have:

1. **Telegram inbox** — verified pairing  
2. **Slack intro** — public post with Telegram DM link  
3. **Habbo presence** — avatar in room(s) or documented BLOCKED  

## Master table

| agent_id | display_name | telegram_dm_link | pairing_status | slack_intro_permalink | habbo_presence | habbo_rooms | activity_age_source | connected |
|---|---|---|---|---|---|---|---|---|
| ctr-code-alfred1 | Alfred | pending | — | — | pending | lobby-sai,personal/ctr-code-alfred1 | ingest | no |
| config-expert | config-expert | pending | — | — | pending | personal/config-expert | ingest | no |
| research-coordinator | research-coordinator | pending | — | — | pending | personal/research-coordinator | ingest | no |

### Column rules

- **connected** = `yes` only when all three gates pass (see protocol)
- **telegram_dm_link** — required before `connected=yes`
- **slack_intro_permalink** — link to `[SAI][INTRO]` post in #agentupdates
- **habbo_rooms** — comma-separated room ids; must include `personal/<agent_id>`
- **activity_age_source** — always `ingest` (activity-ingest service)

## User-created subagents

Dashboard writes new rows via Alfred API on VPS. Same columns required.

## Verification

```bash
openclaw-dashboard/scripts/verify-agent-telegram.sh
openclaw-dashboard/tests/smoke/subagent-connection-gate.sh
```

100% coverage: every `registry.json` agent + every row in `.openclaw/agents/*.md` subagent file.
