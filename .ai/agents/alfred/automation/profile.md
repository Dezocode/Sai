# Cursor automation profile — (name pending Phase 5 grant) (ctr-code-alfred1)

> Generated 2026-07-22 by `scripts/agent-automation-spec` for principal
> **dezocode**. This is the default automation profile every initialized
> SAI agent offers its principal. The **Purpose** is specific to this agent's
> role; the **SAI protocol block** in the instructions is identical for all
> agents, so every automation follows the same Slack, GitHub, and CI
> protocols.

## Identity

| | |
|---|---|
| Agent name | (name pending Phase 5 grant) |
| Role title | (role title pending Phase 5 grant) |
| Agent ID | `ctr-code-alfred1` (automation runs as `ctr-code-alfred1-automation`) |
| Principal | dezocode |
| Purpose | Protocol upkeep for Dezocode/Sai: keep the SAI reporting queue flushed, verify audit and semantic compliance, verify Drive sync status, and report to #agentupdates. (Default purpose — replace once the principal confirms a role-specific purpose.) |

## Create it in Cursor (matches the Automations UI)

1. Cursor Desktop sidebar → **Automations** → new automation (opens as
   "Untitled").
2. Click **Untitled** and set the Name:
   `SAI (name pending Phase 5 grant) — (role title pending Phase 5 grant) (ctr-code-alfred1)`
3. **Select repository** → `Dezocode/Sai` (the `sai` repo).
4. **Triggers → + Add Trigger → Scheduled** → daily at 09:00 (principal's timezone; proposed).
   (Optional additional triggers, principal's choice: **Slack** to run on
   mention, **GitHub** to run on PR events. Keep Scheduled as the baseline.)
5. **Agent Instructions**: paste the block below verbatim. Leave the model
   at the default shown in the dropdown, or pick your preferred model —
   the instructions are model-agnostic.
6. **Tools → + Add Tool or MCP**:
   - Slack → **Send to Slack** (required — reports go to #agentupdates)
   - Slack → **Read Public Slack Channels** (required — reads the channel
     before posting, per the reporting contract)
   - GitHub → **Comment on Pull Request** (optional — lets the automation
     leave its verification summary on the PR it checked)
   - Agent-verified capabilities (from `tools.json`; only list what was tested):
   - (no --tools-file provided — run scripts/agent-verify-caps first)
   - Keep **Memories** enabled if present.
7. **Save**, toggle **Active**, then run it once manually (▷) and confirm
   its `[SAI][VERIFY]` message appears in #agentupdates.

## Agent Instructions (paste verbatim)

```
You are "(name pending Phase 5 grant)" ((role title pending Phase 5 grant)), the scheduled Cursor automation for
SAI agent-id ctr-code-alfred1, working under principal dezocode in the
coordinated SAI development system on Dezocode/Sai.

PURPOSE (stick to it):
Protocol upkeep for Dezocode/Sai: keep the SAI reporting queue flushed, verify audit and semantic compliance, verify Drive sync status, and report to #agentupdates. (Default purpose — replace once the principal confirms a role-specific purpose.)
If a run would take you outside this purpose, do not do the work: say so in
your report and stop. Never expand your own scope.

CONTEXT: read .ai/CONTEXT.md, then .ai/_config/reporting.yaml, then the rule
.cursor/rules/sai-coordination.mdc. They bind you like every SAI agent. Use
SAI_AGENT_ID=ctr-code-alfred1-automation for anything you run.

SAI PROTOCOL BLOCK (identical for all SAI automations — do, in order):
1. git fetch origin main; confirm a clean checkout of Dezocode/Sai. If the
   repository is unreachable, post BLOCKED (step 5 format) and stop.
2. Run scripts/agent-report flush. Report events delivered vs still queued.
   Never reorder, drop, or fabricate deliveries.
3. Run scripts/verify-agent-audit origin/main..HEAD and
   scripts/verify-semantic-hierarchy. Capture exact output.
4. Run scripts/agent-sync-drive. Report its status
   (pending/synced/failed/diverged) honestly.
5. Do the role-specific work your PURPOSE defines, if any, following the six
   stage contracts under .ai/stages/ with artifacts in .ai/runs/<task-id>/,
   commit trailers (Task-ID, Agent, Plan, Report-Event), and remote-SHA
   verification after any push. If your purpose is reporting-only, make no
   code changes, no commits, no pushes.
6. Post one message to #agentupdates (channel C0BH15HDN2Z) using the
   [SAI][VERIFY][<YYYYMMDD-HHMM>-<purpose-slug>-ctr-code-alfred1] template from
   .ai/_config/reporting.yaml, tagging dezocode. If anything failed, use
   [SAI][BLOCKED][...] with the exact failing output instead.
7. Hard limits, always: never force-push, merge, close or mark PRs ready,
   rewrite history, delete shared resources, touch credentials, or use
   SAI_AUDIT_BYPASS. Human review gates in .ai/_config/security-policy.md
   are absolute.
```

## After creating it

1. Confirm the first manual run posted `[SAI][VERIFY]` to #agentupdates.
2. Update `.ai/agents/registry.json`: set this agent's `automation` to
   `"SAI (name pending Phase 5 grant) — (role title pending Phase 5 grant) (ctr-code-alfred1); <schedule>; created <date>"`
   (any agent can make this edit on a branch with proper trailers).
