# 0005 — Registry-driven codebase health gates

- Date: 2026-08-13
- Task-ID: 20260813-1315-codebase-health-cursor-cloud
- Status: accepted
- Approver: dezocode (requested `/plan` for codebase health, no semantic
  duplicates, no orphans, no bloated files, CI for every check, and runtime
  evaluation, 2026-08-13)

## Decision

Enforce codebase health through a versioned **check registry**
(`.ai/_config/code-health.yaml`) plus `scripts/verify-code-health`:

1. Every health check is either `active` (wired in CI, has a self-test) or
   `deferred` (named trigger; not yet a gate).
2. A meta-check fails if an active check's `ci_marker` is missing from
   `.github/workflows/agent-audit.yml`, or if a root `scripts/verify-*` file
   is not registered.
3. Active dispatcher scans cover **bloat** (line/byte limits), **duplicates**
   (exact hash and line-shingle near-copies), and **orphans** (unreferenced
   scripts).
4. Runtime evaluation (`--self-test`) must run in CI before the live scan.
5. Language-specific lint, coverage, import-graph orphans, and AST clone
   detection stay **deferred** until an accepted application stack decision
   exists.

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

A registry is the inventory Saul's lane asked for, and it works before a
stack exists. The meta-check is what makes "every health check is in CI"
true as agents add verifiers. Self-tests prove detectors fail on bad input,
not only that the current tree is green.

## Consequences

- New `scripts/verify-*` at repo root must be added to the registry **and**
  `agent-audit.yml` (or marked `deferred` with `activate_when`).
- ICM template families (per-agent runtime README stubs, mirrored
  `automation/profile.md`, empty memory jsonl) are not treated as defects.
- Thresholds and allowlists live in the YAML; raising a limit requires a
  reviewed commit with a reason.
- Forks inherit the workflow by SHA sync per `icm-ci-policy.md`.

## Supersedes

Nothing. Complements 0001 (ICM CI) and Saul roadmap lane `observability`.
