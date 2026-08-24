# Stage 03 — Implement

## Purpose

Execute the approved plan as the smallest coherent change, in an isolated
branch and worktree, keeping every intermediate artifact inspectable.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 4 | `.ai/runs/<task-id>/02_plan/output/plan.md` | The approved plan |
| 3 | `.ai/shared/references/git-workflow.md` | Branch/worktree/commit rules |
| 3 | `.ai/shared/memory/conventions.md` | Coding and workflow conventions |
| 4 | The working tree | Files claimed in the plan |

## Process

1. Create or use the task-specific branch; use a local worktree **outside
   Google Drive** or any cloud-synced directory. Post a WORKTREE report on
   creation.
2. Make the smallest coherent change that satisfies the plan.
3. Preserve unrelated modifications already in the tree.
4. Keep generated files reproducible (commit the generator and inputs, not
   opaque artifacts).
5. Update tests and documentation together with behavior changes.
6. Update durable memory (`.ai/shared/memory/`) only when knowledge will
   remain useful. Never put guesses into durable memory; label uncertainty
   or verify it first.
7. Post a concise CHANGE report before committing.

## Outputs

- Edited working tree matching the plan.
- `.ai/runs/<task-id>/03_implement/output/changes.md` — what was changed and
  why, per file or component.
- CHANGE report to #agentupdates at meaningful checkpoints.

## Verification

Deferred to stage 04, but the implementer must confirm the diff touches only
claimed files (or record and justify the exception in `changes.md`).

## Human review gate

Stop mid-implementation and post BLOCKED/CONFLICT if: another agent claims
overlapping files, the plan proves wrong in a way that changes scope, or a
hard security gate is encountered.

## Rollback

`git restore`/`git checkout` the branch away without merging; record the
abandonment in `changes.md` and post HANDOFF.

## Provenance

`changes.md` links every material change to the plan section that justified
it.
