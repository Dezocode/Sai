# Cursor automation spec — cursor-cloud-30d8

> Generated 2026-07-14 by `scripts/agent-automation-spec` for principal
> **dezocode (U0BHYH0NMCY)** because agent `cursor-cloud-30d8` cannot create Cursor
> automations from its environment. Everything needed is below — create the
> automation, then tell the agent (or update the registry yourself) so its
> `automation` field can change from `delegated:` to the real name.

## Where to create it

Cursor Desktop → **Automations** (or https://cursor.com/automations) →
**New Automation**, signed in as dezocode (U0BHYH0NMCY).

## Settings

| Field | Value |
|---|---|
| Name | `SAI (name pending Phase 5 grant by dezocode) — protocol upkeep (cursor-cloud-30d8)` |
| Owner | dezocode (U0BHYH0NMCY) |
| Schedule | daily at 09:00 America/Chicago (proposed) (at least daily is recommended) |
| Repository | `Dezocode/Sai` |
| Base branch | `main` |
| Environment | any environment with repo access; Slack integration connected so reports reach #agentupdates (C0BH15HDN2Z) |
| Secrets (optional) | `SAI_SLACK_BOT_TOKEN` to let git hooks deliver directly; without it the automation itself posts via the Slack integration |

## Prompt (paste verbatim)

```
You are the scheduled protocol-upkeep automation for SAI agent
"(name pending Phase 5 grant by dezocode)" (agent-id cursor-cloud-30d8), working under principal
dezocode (U0BHYH0NMCY) in the coordinated SAI development system.

Context: read .ai/CONTEXT.md, then .ai/_config/reporting.yaml. You act
under the same rules as every SAI agent (.cursor/rules/sai-coordination.mdc).
Set SAI_AGENT_ID=cursor-cloud-30d8-automation for anything you run.

Do, in order:
1. git fetch origin main and confirm you are on a clean checkout of
   Dezocode/Sai. If the repo is unreachable, post BLOCKED (step 5 format) and stop.
2. Run scripts/agent-report flush. Report how many events delivered and how
   many remain queued. Never reorder, drop, or fabricate deliveries.
3. Run scripts/verify-agent-audit origin/main..HEAD and
   scripts/verify-semantic-hierarchy. Capture exact output.
4. Run scripts/agent-sync-drive. Report its status (pending/synced/failed/
   diverged) honestly.
5. Post one message to #agentupdates (channel C0BH15HDN2Z) using the
   [SAI][VERIFY][<YYYYMMDD-HHMM>-protocol-upkeep-cursor-cloud-30d8] template from
   .ai/_config/reporting.yaml, tagging dezocode (U0BHYH0NMCY). If any check failed,
   use [SAI][BLOCKED][...] instead and include the exact failing output.
6. Make no code changes, no commits, no pushes, no merges, and never use
   SAI_AUDIT_BYPASS. You are a reporter, not an editor. If you believe a
   change is needed, say so in the report and stop.
```

## After creating it

1. Run it once manually and confirm a [SAI][VERIFY] message appears in
   #agentupdates.
2. Update `.ai/agents/registry.json`: set this agent's `automation` to
   `"SAI (name pending Phase 5 grant by dezocode) — protocol upkeep (cursor-cloud-30d8); <schedule>; created <date>"`
   (any agent can make this edit on a branch with proper trailers if you
   prefer not to).
