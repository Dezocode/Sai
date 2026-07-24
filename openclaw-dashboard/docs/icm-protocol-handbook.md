# `.ai` Protocol Handbook — Dashboard builders

**Audience:** Alfred and any contractor touching `openclaw-dashboard/`  
**Binding:** Same rules as `.cursor/rules/sai-coordination.mdc` + repo `.ai/CONTEXT.md`

---

## Reporting SOP (agent session runs)

Every Alfred run and every registered agent session visible in the dashboard
must map to a **public Slack report** or queued event.

### Template

```
[SAI][EVENT_TYPE][task-id]
Actor: Alfred (ctr-code-alfred1) | <other agent>
Repository: Dezocode/Sai
Branch: proj/openclaw-dashboard/ctr-code-alfred1/<slug>
Purpose: <tab or settings surface>
Result: <what changed>
Verification: <commands + PASS/FAIL>
Review gate: <next action>
```

### Channels

| Channel | ID | Use |
|---|---|---|
| `#agentupdates` | C0BH15HDN2Z | Primary — all `[SAI][EVENT]` |
| `#proj-openclaw-dashboard` | pending | Project-specific when approved |

Tag dezocode, monaecode, @sai on VERIFY/HANDOFF/CONTRACT.

Implementation surface: [settings/reporting-sop/](../settings/reporting-sop/CONTEXT.md)

---

## Run artifacts (repo `.ai/runs/`)

Required for every material change:

```
.ai/runs/<task-id>/
  metadata.json       # agent, contract_id, status, repository
  handoff.md            # >20 bytes for merge gate
  events.jsonl          # optional Slack delivery record
  02_plan/output/       # before edits
  04_verify/output/     # after tests
```

Dashboard-local notes may go in `openclaw-dashboard/.ai/runs/` as **mirrors**
only — canonical runs stay in repo `.ai/runs/`.

---

## CI verifiers (must PASS on PR branch)

```bash
scripts/verify-semantic-hierarchy
scripts/verify-agent-setup
scripts/verify-agent-audit origin/main..HEAD
scripts/verify-merge-handoff origin/main..HEAD   # before merge
scripts/agent-contract-pr-review \
  --contract-id 20260722-openclaw-dashboard-dezocode \
  --branch proj/openclaw-dashboard/ctr-code-alfred1/bootstrap
```

Product-specific:

```bash
openclaw-dashboard/scripts/verify-gateway-health.sh
openclaw-dashboard/scripts/verify-all-dependencies.sh
openclaw-dashboard/scripts/verify-agent-telegram.sh   # fail-closed A10
openclaw-dashboard/scripts/verify-ingest-latency.sh   # p99 <= 15ms
openclaw-dashboard/tests/smoke/run-all.sh
```

---

## Git discipline

- Branch: `proj/openclaw-dashboard/ctr-code-alfred1/<task-slug>`
- Commit trailers: `Task-ID`, `Agent: Alfred`, `Report-Event`
- Never force-push; never merge to `main` without fulfillment gate

---

## Auth & secrets

- GitHub OAuth app credentials → VPS env
- Composio keys → VPS env
- OpenClaw `~/.openclaw/openclaw.json` → VPS only
- Dashboard auth hub documents flows in [settings/auth/](../settings/auth/)

---

## Agent registry integration

Dashboard **tracking** and **chat-room** tabs read `.ai/agents/registry.json`.
On registry change, Alfred must:

1. Update agent presence sprites/metadata
2. Open Telegram verification task ([A10](../tabs/chat-room/CONTEXT.md))
3. Post `[SAI][CHANGE]` listing affected agents

---

## Fulfillment gate checklist

See contract `fulfillment_gate` + `organization_onboarding_gate`.
Package evidence in `docs/fulfillment-evidence.md` at A12.
