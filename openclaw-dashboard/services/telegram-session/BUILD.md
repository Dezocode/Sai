# BUILD — telegram-session service

## Phase 1: Session store

1. Implement `session_state.json` read/write per [session-memory.md](../../../.ai/agents/alfred/runtimes/openclaw/telegram/session-memory.md)
2. Rolling `context_summary.md` regenerator on VERIFY/HANDOFF

## Phase 2: Contract sender reporter

1. Load `contract.json` → `contract_sender.slack_id` → resolve Telegram chat via pairing
2. Template renderer for INTAKE/PLAN/CHANGE/VERIFY/HANDOFF/BLOCKED (BEHAVIORS.md B2)
3. 60s SLA timer; queue retry on Telegram API failure

## Phase 3: Slack mirror

1. After Telegram send success → emit `[SAI][EVENT][task-id]` to #agentupdates
2. Record `last_slack_mirror_at` in session state

## Phase 4: Fleet provisioner

1. Alfred hook on subagent create → copy telegram template to agent folder
2. Register fleet row for `fleet-coherence-gate.sh`

## Phase 5: Smoke

```bash
openclaw-dashboard/tests/smoke/telegram-session-reporting.sh
openclaw-dashboard/tests/smoke/fleet-coherence-gate.sh
```

Evidence: contract sender confirms test INTAKE + HANDOFF received on Telegram.
