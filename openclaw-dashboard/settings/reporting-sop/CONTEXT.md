# Settings: Reporting SOP

| Field | Value |
|---|---|
| **Deliverable** | A1 |
| **Protocol** | [docs/icm-protocol-handbook.md](../../docs/icm-protocol-handbook.md) |
| **Desktop route** | `/settings/reporting-sop` |

## Channel routing

| Agent | Principal | Channel | Delivery method |
|---|---|---|---|
| Sai (ceo) | dezocode | #agentupdates, #help-newagents | agent-report queue → Slack API |
| Mimi | monaecode | #agentupdates, #proj-* | agent-report queue → Slack API |
| Alfred (ctr-code-alfred1) | dezocode | #agentupdates (C0BH15HDN2Z), Telegram DM | agent-report queue + Telegram session |

### Rules

- **Public channels only** — never report agent runs in private channels or DMs
- Every agent run visible in dashboard must link to a `[SAI][EVENT]` in an approved public
  Slack channel **or** a queued `scripts/agent-report` JSON with channel id
- **Queue fallback:** if Slack is unavailable, events persist in `.git/agent-events/queue/`
  (FIFO, idempotent by `event_id`). Flush via `scripts/agent-report flush` when Slack
  resumes. Never fabricate delivery success
- **Token:** `SAI_SLACK_BOT_TOKEN` in `/etc/openclaw/sai.env` (0600, not in Git)

### Compliance table spec

Dashboard audit table must display:

| agent_id | last `[SAI][EVENT]` | channel | compliant (Y/N) |
|---|---|---|---|
| ceo | 2026-07-24T03:11Z | #agentupdates | Y |
| mimi | *(pending)* | #agentupdates | N |
| ctr-code-alfred1 | active this session | #agentupdates | Y |

- **Criteria:** active agent with no `[SAI][EVENT]` in >48h → non-compliant
- **Violation banner:** trigger when compliance Y/N shows N for any active agent

### Cross-references

- Reporting config: `.ai/_config/reporting.yaml`
- Agent registry: `.ai/agents/registry.json`
- ICM integration: `openclaw-dashboard/docs/sai-icm-integration.md`
- Agent-report script: `scripts/agent-report`
- Build: [BUILD.md](./BUILD.md)
