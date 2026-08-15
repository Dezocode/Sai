# Intake — Cora Ralph liveness-invariant, v12 reuse

Requester: parent logical Primary `pr62-primary`. Named child
Cora (`ctr-admin`). Parent physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`. This physical
runtime `bc-1cbab63c-37b2-5eed-83fb-56142afff85a`. Grant
`grant-pr62-queue-cora`. Work item
`ralph-liveness-invariant`. Contract
`20260813-pr62-saul-smoke` v12.

Exact requested outcome: reuse v12 (no A-013/v13) for a
Ralph liveness-invariant wave on existing blockers
B-RALPH-001, B-NO-IDLE-SAUL-001,
B-RALPH-BLOCKER-CI-CONVERGENCE-001. Do not create a new
Decision, new blocker ID, or second Ralph engine. Cora
records the contractor work; contractor implements.

Live HEAD after `git fetch origin cursor/codebase-health-90ba`:
`f34bc63635e088fbcd85a400bc2920263b748ab5` (matches expected).
PR https://github.com/Dezocode/Sai/pull/62 draft, MERGEABLE.
Canonical `Dezocode/Sai` default `main` `40efe0a`. Branch
`cursor/codebase-health-90ba`. Untracked preserved:
`.ai/runs/20260815-1935-pr62-queue-ctr-code/events.jsonl`.

Live `scripts/sai-resume` reconstruct on this tree:
status=RECONSTRUCTED, primary_logical_id=pr62-primary,
READY_FOR_HUMAN_REVIEW=false, continue=true,
liveness=WAITING_EXTERNAL, reassess_blockers=false,
playbook=orchestrate-waiting-external,
physical_runtime_continuity=false,
exit_predicate_satisfied=false, workers COMPLETE.
Ordinary CI green is not completion. Decision 0009 already
persisted (officer). reuse v12. No A-013/v13.
