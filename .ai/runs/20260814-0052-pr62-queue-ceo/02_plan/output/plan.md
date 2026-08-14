# Plan — amend Decision 0008 + orchestration rule

Exact head at plan: `bb519c2978e8e285e4f452159813452cebc7a2cb`.
Contract revision v5 already lists officer work as Decision 0008 + mdc.

## Current vs desired

- Decision 0008 still recommends empty-dest first-writer freeze in
  `saul-review.yml` (CTO-015 rejected that). Cora-per-todo / Ralph /
  no-idle-Saul exist only in contract/ledger prose (CTO-022).
- Desired: 0008 amended in place (keep 0006/0007; no 0009). Fresh Cloud
  agents inherit the hierarchy from `sai-orchestration.mdc` (`alwaysApply`).

## Files

1. `.ai/shared/memory/decisions/0008-persistent-primary-cursor-orchestrator.md`
   — replace the empty-dest paragraph; append 2026-08-14 amendment; note
   CTO-021 without claiming it is live on `main`.
2. `.cursor/rules/sai-orchestration.mdc` — per-todo Cora then contractor;
   Primary-only recursive `REASSESS BLOCKERS`; Saul pending ≠ idle;
   blocker authority restated; keep poteto / lazy-first-write / two-primary /
   wait / exit-predicate.
3. `.cursor/skills/resume-sai/SKILL.md` — three-line pickup pointer only.
4. This run directory.

Out of scope: `.ai/contracts`, `scripts/`, `.github/workflows`.

## Verification

Line counts (0008 <600; mdc ~250). JSON parse of metadata. Grep that
first-writer freeze is gone. `scripts/verify-semantic-hierarchy`. After
commit: `verify-agent-audit` and `verify-merge-handoff`. Do not PASS
blockers. Do not merge.

## Risks

`grant-pr62-queue-ceo.task_id` is still `20260813-2015-pr62-queue-ceo`.
This commit uses the parent-specified Task-ID. Mechanical grant replay
may fail until Cora/principal appends this task to the grant. Not a
self-issued grant expansion.
