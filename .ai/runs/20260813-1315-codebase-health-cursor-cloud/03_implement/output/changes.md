# Implement — codebase health registry and CI

- Task-ID: `20260813-1315-codebase-health-cursor-cloud`
- Plan: `.ai/runs/20260813-1315-codebase-health-cursor-cloud/02_plan/output/plan.md`

## What changed

Installed decision 0005: a YAML registry is the source of truth for every
health check; CI fails if an active check is unwired; detectors for bloat,
duplicates, and orphans run locally and in GitHub Actions; `--self-test`
evaluates the detectors on synthetic good/bad trees before the live scan.

Deferred rows document app unit tests, import-graph orphans, and AST clone
detection until a stack decision exists. Existing ICM and OpenClaw CI steps
are registered so they cannot silently disappear. OpenClaw stub scripts that
exit 2 stay `deferred`.

## Per path

See the plan table. Material new files: `.ai/_config/code-health.yaml`,
`scripts/verify-code-health`, `scripts/lib/code-health.py`,
`.ai/shared/references/code-health.md`, decision `0005`,
`tests/code-health/README.md`. CI, pre-push, agent-init, and
verify-semantic-hierarchy required-files were extended so the registry cannot
be dropped without a hierarchy failure.
