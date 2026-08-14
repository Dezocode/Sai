# Intake — Cora A-010 / v10 for PR #62

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`, acting for dezocode
(U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) via grant-pr62-queue-cora.

Exact requested outcome: ingest principal P0 comment 5289020312
(Dezocode, 2026-08-14T03:21:41Z, append-only, ~10453 bytes). This
is NOT a Saul consume. Do not run
`scripts/consume-saul-contract-review`. Write A-010 → v10 by hand
in the A-009/v9 style. Reuse `ctr-code-pr62smoke` and
`lease-c3a003pr62q1`. Do not expand allowed_paths. denied_paths
unchanged. Bump lease revision to v10. Keep lease.task_id
`20260813-2017-pr62-queue-ctr-code`. Set `cora_admin_complete: true`
on v10 (administration complete for this wave, not technical PASS).
Commit trailers MUST use original grant Task-ID
`20260813-2016-pr62-queue-cora`. Do not implement scripts. Do not
PASS. Do not merge. Do not write blockers items (contractor). Do
not write decisions or `.cursor` (officer/Sai). Do not write
`.ai/authorizations`.

## Repository facts (command-backed)

- Repository: Dezocode/Sai (origin fetch/push).
- Default branch: main (`40efe0a` at intake; origin/main has
  `.github/workflows/agent-audit.yml` only — no trusted
  `pull_request_target` file).
- Working branch: `cursor/codebase-health-90ba`.
- HEAD: `c51c9cf221a8f4682e2c9e2287bd06d550c6c44e`.
- Latest qualifying Saul on this HEAD: run 31764010391,
  REQUEST_CHANGES. CTO-025 still BLOCKED_EXTERNAL ("human must
  land trusted workflow on main first"). CTO-026 uncleared.
  CTO-027: icm-enforcement SUCCESS on c51c9cf after Saul snapshot
  is not technical PASS.
- Assumed identity: ctr-admin under grant-pr62-queue-cora.
- Do not rework IMPLEMENTED_AWAITING_SAUL items.

## Constraints

- Cora writes contract/lease/run artifacts only.
- Reuse contractor + lease. No path expansion. denied_paths
  unchanged (`.ai/agents/saul/**`, `.ai/shared/memory/decisions/**`,
  `.ai/authorizations/**`).
- Principal now requires overnight convergence: package trusted-
  workflow activation into THIS PR's human merge rather than an
  intermediate bootstrap PR.
- Cora authorizes CTO-025 merge-activation design; Cora does not
  self-PASS CTO-025. Saul may AMEND CTO-025 / classify
  CONDITIONAL_PASS_ON_HUMAN_MERGE; Cora/contractor must not emit
  that as clearance.
- Keep CTO-026 uncleared. Keep CTO-015..021, 024, 028, 029
  IMPLEMENTED_AWAITING_SAUL.
- YAML files must stay ≤300 lines.

## Acceptance (this Cora slice)

A-010 and v10 exist; contract.json current_revision is v10; lease
reused and bound to v10; REQ-5289020312 appended; cora_admin_complete
true; implements false; do_not_merge true; technical_pass false;
no technical PASS claimed; CTO-025 not PASSED.
