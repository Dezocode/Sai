# Live smoke — `/resume-sai`, named Cora, watchdog, two-primary, external wake

Recorded 2026-08-13 on physical `bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`.
Predicate false; program continues. Do not treat this file as Saul/Sai APPROVE.

## `/resume-sai` (fresh Task turn)

Worker physical: `bc-de3dcd6c-44ca-571a-affd-420ecbe21b01`
Instruction: only follow `.cursor/skills/resume-sai/SKILL.md`.

Reconstructed: logical `pr62-primary`, PR 62, head `2ac83a1`, contract v3,
ledger includes REQ-5287297355, Saul BLOCKED TRUSTED_REVIEWER_UNAVAILABLE
on that head, liveness ACTIVE, continue true, playbook
`poteto-continue-frontier`, did not re-implement.

## Named Cora

Worker: name Cora, agent_id `ctr-admin`, physical `bc-2faed256-1063-58a3-9d65-8d8f8e52d574`.
Reused contractor `ctr-code-pr62smoke`. No new identity. Parent authority
does not transfer. Did not implement.

## Watchdog (no model)

Synthetic: healthy NOOP, complete → SUBAGENT_COMPLETE, stale → STALE_WORKER.
Live: Cora COMPLETE queued; contractor RUNNING healthy NOOP; `model_invoked: false`.

## Two-primary cap

Synthetic: two primaries + third → park. RI/stacked admit. Dezocode override admits.

## External return

physical_resume_supported: true (prompt required)
silent_github_wake_supported: false
mechanism: POST /v1/agents/{id}/runs or SDK Agent.resume+send
api_key_present: false
this_bcId: bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc
probe: GET api.cursor.com/v1/agents → 401 Invalid User API Key
logical_pickup_required: true
wake probe worker: bc-cba5edfb-e6ef-59bd-bff6-850b0fd7bcdc
