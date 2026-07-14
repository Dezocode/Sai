# Stage 02 — Plan

## Purpose

Turn the intake record into a scoped, reviewable plan before any file in the
repository is materially edited.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 4 | `.ai/runs/<task-id>/01_intake/output/intake.md` | The intake record |
| 3 | `.ai/shared/memory/architecture.md` | Confirmed architecture |
| 3 | `.ai/shared/memory/conventions.md` | Conventions the plan must follow |
| 3 | `.ai/shared/memory/known-issues.md` | Pitfalls to plan around |
| 3 | `.ai/shared/memory/decisions/` | Decision records that constrain the design |

Load only the memory files relevant to the task's area.

## Process

Write a plan covering:

1. Current behavior and desired behavior.
2. Proposed file changes (paths, nature of change).
3. Justification for each material change.
4. Tests/verification to run (from `.ai/shared/references/testing.md`).
5. Risks and rollback strategy.
6. Files claimed for editing — also record these in `metadata.json` so other
   agents can detect conflicts.
7. Human review gates that apply.

Describe technical scope and risk only. **Never estimate work in days or
weeks.**

## Outputs

- For substantial tasks: `.ai/runs/<task-id>/02_plan/output/plan.md`.
  Trivial tasks may fold the plan into the INTAKE/PLAN Slack report instead.
- PLAN report posted to #agentupdates before edits begin.
- Updated `metadata.json` with claimed files.

## Verification

Every file the plan proposes to change is either unclaimed by other active
runs or explicitly coordinated; the plan names its review gates.

## Human review gate

Required before implementation when the plan involves any hard gate from
`.ai/_config/security-policy.md`, architectural change (new decision record),
or cross-repository pushes. Otherwise the PLAN report is the gate — proceed
unless a co-founder objects.

## Rollback

Abandon by marking `metadata.json` status `abandoned` and posting HANDOFF.

## Provenance

The plan cites the intake record, the decision records it relies on, and the
memory entries it read.
