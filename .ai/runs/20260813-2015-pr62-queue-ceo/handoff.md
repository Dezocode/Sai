# Handoff — Sai (repo-native orchestration / comment 5287013791)

Logical primary: `pr62-primary`.
Physical runtime: `bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`.
State: `.ai/runs/20260813-2015-pr62-queue-ceo/coordinator-state.json`.

## What landed (governance)

- `.cursor/rules/sai-orchestration.mdc` (alwaysApply): fresh Cloud
  runtime is the standing coordinator; ordinary "Implement X" is enough.
- `.ai/CONTEXT.md` and `sai-coordination.mdc` no longer send every
  unbound Cloud agent into `INITIALIZE.md` / `agent-init`.
- `.ai/agents/cora/AGENT.md` documents automatic `SAI_CUE` admission.
- Decision 0006 amendment: primary orchestrator, waiting nonterminal,
  candidate HEAD is not the trusted reviewer.
- Requirement ledger:
  `.ai/contracts/20260813-pr62-saul-smoke/requirements/ledger.yaml`.

## Continuity (honest)

- `physical_runtime_continuity` after WAITING_EXTERNAL: **false**
  (GitHub cannot silently resume this Cloud conversation; a follow-up
  prompt or a new agent with session-pickup is required).
- Logical pickup: `coordinator-state.json`.
Fresh-unknown Cloud smoke (a second bcId with an ordinary prompt):
**not executed from this session** (would require launching another
Cloud agent). In-process first-write cue is proven by
`sai_auth_cue_test` (unknown → CORA_ADMISSION; existing assignment →
RESUME_CONTRACTOR; worktree unchanged).

Async research worker `bc-1d9153f1-10fb-51b3-aa19-7a31549b175e` was
spawned read-only for Cursor wake/pstack; mutating workers were not
given this worktree (one agent per tree).

## Exit

READY_FOR_HUMAN_REVIEW: **no**. Needs real Saul APPROVE + Sai APPROVE +
CI green on the exact new SHA. Do not merge. Do not mark ready.
