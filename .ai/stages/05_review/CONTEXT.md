# Stage 05 — Review

## Purpose

Inspect the complete change as a reviewer would, before anything is
published.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 4 | Full diff (`git diff <base>...HEAD`) | Every changed line |
| 4 | `.ai/runs/<task-id>/02_plan/output/plan.md` | What was promised |
| 4 | `.ai/runs/<task-id>/04_verify/output/verification.md` | What was proven |
| 4 | Other active runs' `metadata.json` | Declared file ownership |

## Process

Check, explicitly and in writing:

1. The full diff — every hunk is intended and justified.
2. Changed file list matches the claimed files (or exceptions are justified).
3. No accidental generated files, secrets, credentials, `.env`, large
   binaries, or machine-specific paths.
4. Tests and documentation updated with behavior changes.
5. Commit boundaries: each commit is one logical change with required
   trailers.
6. Compatibility impact on the fork pair and existing branches.
7. Durable memory (`.ai/shared/memory/`) updated accurately, or untouched.
8. No conflicts with other runs' declared file ownership.

## Outputs

- `.ai/runs/<task-id>/05_review/output/review.md` — findings per checklist
  item, and the disposition (proceed / return to stage 03 / block).

## Verification

`review.md` addresses all eight checklist items; none is marked "assumed".

## Human review gate

This stage feeds the human gate: the PR opened in stage 06 is where
co-founders review. Anything matching a hard gate in
`.ai/_config/security-policy.md` must be flagged in `review.md` and must not
proceed without explicit approval.

## Rollback

Return to stage 03 with the findings; append a new review section after
fixes.

## Provenance

`review.md` names the diff range (SHAs) it reviewed.
