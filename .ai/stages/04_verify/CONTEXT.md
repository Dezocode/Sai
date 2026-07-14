# Stage 04 — Verify

## Purpose

Run proportionate verification and record honest, reproducible results.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 4 | `.ai/runs/<task-id>/03_implement/output/changes.md` | What changed |
| 3 | `.ai/shared/references/testing.md` | Which checks apply to which files |
| 4 | The working tree | The changed files |

## Process

1. Determine relevant checks from the testing reference: tests, formatting,
   linting, type checks, builds, migrations, security checks.
2. Run them, capturing exact commands and output.
3. Record relevant failures verbatim.
4. Record every skipped check with its reason, and environment limitations
   (e.g. missing credentials, no network).

## Outputs

- `.ai/runs/<task-id>/04_verify/output/verification.md` — commands, results,
  failures, skips, limitations.
- VERIFY report to #agentupdates (required if anything failed or was
  skipped; recommended always).

## Verification (of this stage)

**Never describe a check as passing if it was skipped, unavailable, or only
partially run.** The verification record must allow a human to re-run every
command.

## Human review gate

Failures that the agent cannot fix within the task's scope stop the pipeline
here: post BLOCKED with the failing output.

## Rollback

Return to stage 03 to fix failures; append (never rewrite) new verification
runs to `verification.md`.

## Provenance

Each check links to the files it covered and the plan requirement it
verifies.
