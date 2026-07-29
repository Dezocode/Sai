# SAI ICM integration — Alfred A1

Dashboard enforces repo-wide ICM.

## Registry and reporting

- **Registry**: `.ai/agents/registry.json` — one entry per initialized agent
- **Reporting config**: `.ai/_config/reporting.yaml` — template, channels, event types, queue dirs
- **Slack workspace**: `sai-qbz5908.slack.com`
- **Primary channel**: `#agentupdates` (C0BH15HDN2Z)
- **Settings UI**: [settings/reporting-sop/](../settings/reporting-sop/CONTEXT.md)

## Agent-report queue (Slack delivery pipeline)

All `[SAI][EVENT]` posts go through `scripts/agent-report`:

| Mechanism | Detail |
|---|---|
| **Script** | `scripts/agent-report emit <EVENT_TYPE> [options]` |
| **Token** | `SAI_SLACK_BOT_TOKEN` in environment (never in Git) |
| **Channel** | `#agentupdates` (C0BH15HDN2Z) — configurable via `$SAI_SLACK_CHANNEL` |
| **Queue** | `.git/agent-events/queue/` — FIFO, idempotent by `event_id` |
| **Sent** | `.git/agent-events/sent/` — after successful Slack delivery |
| **Retry** | `scripts/agent-report flush` redelivers oldest first; stops on first failure |
| **Offline** | Events persist in queue when Slack unavailable; delivered on next `flush` |
| **Redaction** | Secrets redacted before any write (see `redact()` in script) |

### SOP

1. Every agent run visible in dashboard must link to a `[SAI][EVENT]` in `#agentupdates` **or** a queued `scripts/agent-report` JSON with channel id C0BH15HDN2Z.
2. Emit before edits (`[SAI][PLAN]`), after changes (`[SAI][CHANGE]`), on verification (`[SAI][VERIFY]`), and at every ICM stage (INTAKE, PLAN, CHANGE, VERIFY, BLOCKED, HANDOFF).
3. Use `--no-deliver` to batch events, then `flush` once all queued.
4. Never fabricate delivery: `flush` stops at first failure and reports the Slack API error.

## Both repos

Alfred bridges `Dezocode/Sai` (canonical) and `monaecode/Sai` (fork):

- **Ingest:** `[SAI][EVENT]` posts from both repos are valid feed sources for the Tracking tab (A3).
- **CI status:** branch/CI data fetched from GitHub for both repos (A8).
- **Sync:** commits on `monaecode/Sai` verified by SHA against canonical (contract § sync protocol).

## Agent registry mapping

| Agent | Principal | Slack channel | event type |
|---|---|---|---|
| Sai (ceo) | dezocode | #agentupdates, #help-newagents | INTAKE, VERIFY, HANDOFF, CONTRACT |
| Mimi | monaecode | #agentupdates, #proj-* | INTAKE, PLAN, CHANGE, VERIFY |
| Alfred (ctr-code-alfred1) | dezocode | #agentupdates, Telegram DM | all ICM stages |

Alfred posts `[SAI][INTAKE]` on bootstrap and `[SAI][PLAN]` before each tab BUILD phase.
