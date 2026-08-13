# 0005 — Registry-driven codebase health gates

- Date: 2026-08-13
- Task-ID: 20260813-1427-pr62-exec-context-ceo
  (original landing: 20260813-1315-codebase-health-cursor-cloud)
- Status: accepted
- Approver: dezocode (requested `/plan` for codebase health, no semantic
  duplicates, no orphans, no bloated files, CI for every check, and runtime
  evaluation, 2026-08-13)

## Decision

Enforce codebase health through a versioned **check registry**
(`.ai/_config/code-health.yaml`) plus `scripts/verify-code-health`:

1. Every health check is either `active` (wired in CI, has a self-test) or
   `deferred` (named trigger; not yet a gate).
2. A meta-check fails unless each **active** check's `command` is an
   **unconditional** `run:` invocation in a `ci.coverage_jobs` job
   (default `icm-enforcement`) of `.github/workflows/agent-audit.yml`
   (token-prefix match, longest command wins). Mentions in `grep`,
   comments, `test -f`, `echo`, or `chmod` do not count. Job- or
   step-level `if:` (including `merge-handoff-slack`, main-push only)
   does not count. A root `scripts/verify-*` file must be registered.
3. Active dispatcher scans cover **bloat** (line/byte limits), **duplicates**
   (exact hash and line-shingle near-copies), and **orphans** (unreferenced
   scripts). Duplicate-family exemptions are YAML `duplicates.families`
   patterns, not hardcoded names.
4. `self_test` is an enum: `synthetic`, `live-pass`, or `none`. Class
   `health-detector` requires `synthetic` plus named positive and negative
   fixtures that `--self-test` actually executes. `live-pass` means this
   tree currently passes; it is **not** a negative evaluation of the
   checker.
5. Runtime evaluation (`--self-test`) must run in CI before the live scan.
6. Language-specific lint, coverage, import-graph orphans, and AST clone
   detection stay **deferred** until an accepted application stack decision
   exists. Line-shingle Jaccard is not semantic clone detection.

## Context

dezocode asked how to keep the tree healthy as the parent app starts to
land. Today CI is a hardcoded script list. Nothing measured file size,
duplication, or unreferenced scripts. Saul's semantic-tracking lane was
`proposed` pending a module/interface inventory schema. The repository still
has no accepted product stack (DR-20260724).

## Alternatives considered

- **Wait for a stack, then add ESLint/ruff/jscpd only** — rejected; ICM
  scripts and Markdown can already rot, and a hardcoded CI list will miss
  new checks.
- **Vendor jscpd or Semgrep now** — rejected; no package manifests, and
  clone tools need application source. Line-shingle Jaccard covers
  Markdown/shell until a stack lands.
- **Policy docs without CI** — rejected; the request was CI for every check.

## Rationale

A registry is a **health-check inventory**, not Saul's module/interface
semantic-tracking schema. The meta-check makes "every active check is
executed in CI on every push/PR" true only if it inspects unconditional
`run:` invocations in `icm-enforcement`, not raw workflow text and not
conditional jobs. Synthetic fixtures prove dispatcher detectors fail on
bad input; `live-pass` does not.

## Consequences

- New `scripts/verify-*` at repo root must be added to the registry **and**
  `agent-audit.yml` (or marked `deferred` with `activate_when`).
- ICM template families (per-agent runtime README stubs, mirrored
  `automation/profile.md`, empty memory jsonl) are not treated as defects.
- Thresholds and allowlists live in the YAML; raising a limit requires a
  reviewed commit with a reason.
- Forks inherit the workflow by SHA sync per `icm-ci-policy.md`.
- Saul roadmap: **Code-health inventory** is `active`; **Semantic tracking**
  stays `proposed` until module/interface/AST/import analysis exists.

## Amendment (2026-08-13, PR #62 CTO REQUEST CHANGES)

Executable `run:` matching replaced substring `ci_marker` search. Self-test
modes are validated as an enum with required fixtures for `health-detector`.
Duplicate families are YAML patterns. Duplicate PASS is emitted only when
that detector recorded zero failures.

## Amendment (2026-08-13, PR #62 CTO re-review — execution context)

Coverage binds to `ci.coverage_jobs` (default `icm-enforcement`). A `run:`
under job- or step-level `if:` does not satisfy an active check. Fixture
`ci-coverage-conditional-job` (command only in a main-only job) and
`ci-coverage-step-if` must fail.

## Provenance (2026-08-13, registered agent Sai / `ceo`)

This decision and the Saul roadmap lane split (Code-health inventory
`active`; Semantic tracking `proposed`) are re-affirmed by registered
agent Sai (`ceo`) on PR #62. The original 20260813-1315 landing used
unregistered `cursor-cloud` / `cursoragent` trailers. This amendment is
the registered-agent re-execution Saul required. Lane statuses are
unchanged.

## Supersedes

Nothing. Complements 0001 (ICM CI). Does **not** activate the Semantic
tracking roadmap lane.
