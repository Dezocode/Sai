# Plan — registry-driven codebase health with CI + runtime evaluation

- Task-ID: `20260813-1315-codebase-health-cursor-cloud`
- Intake: `.ai/runs/20260813-1315-codebase-health-cursor-cloud/01_intake/output/intake.md`
- Decision to create: `0005-codebase-health-registry`
- Memory read: `architecture.md`, `conventions.md`, `known-issues.md`, decisions `0001`, `0004`, `DR-20260724`, Saul `roadmap.json`

## Current behavior

Health is a **fixed list of scripts hardcoded in one GitHub Actions job**. Adding a check requires remembering to edit the workflow, `agent-init`, `verify-semantic-hierarchy` required-files, `testing.md`, and `icm-ci-policy.md`. Nothing measures file bloat, unreferenced scripts, or duplicated content. Nothing proves a checker actually fails on bad input.

## Desired behavior

1. **Registry is law.** `.ai/_config/code-health.yaml` lists every health check. Status is `active` (must run in CI + have a self-test) or `deferred` (documented trigger; not yet wired).
2. **Meta-check (`ci-coverage`)** fails CI when:
   - an `active` check's `ci_marker` is absent from `agent-audit.yml`
   - a `scripts/verify-*` path is not registered
3. **Bloat** fails when a tracked file exceeds line/byte limits by extension (allowlist with reason).
4. **Duplicates** fail on unexpected exact copies and high line-shingle Jaccard overlap (semantic near-copies). Known ICM families are classified, not failed: empty placeholders, per-agent runtime README stubs, mirrored `automation/profile.md`.
5. **Orphans** fail when a script under configured roots is never mentioned by another tracked file (excluding `.ai/runs/`).
6. **Runtime evaluation:** `scripts/verify-code-health --self-test` builds temporary known-good and known-bad trees and asserts pass/fail. CI runs self-test **before** live scans.
7. **Deferred, not fake:** app unit tests, import-graph orphans, and token-clone detection stay `deferred` until a stack decision record exists. Prototype `openclaw-dashboard/` smoke/self-tests already in CI are **registered** so they cannot silently disappear.

## Why this shape

- Saul's `observability` lane asked for a module/interface inventory schema; a check **registry** is that schema for health, and it works before a stack exists.
- DR-20260724: do not treat dashboard Markdown as accepted app stack. Health gates apply to the whole tree; stack linters wait.
- A meta-check is the only way "CI for every health check" stays true as agents add scripts.

## File changes

| Path | Change | Why |
|---|---|---|
| `.ai/_config/code-health.yaml` | New registry + thresholds + families | Single source of truth |
| `.ai/shared/references/code-health.md` | Human policy | Agents extend checks without inventing process |
| `.ai/shared/memory/decisions/0005-codebase-health-registry.md` | New DR | Architectural convention |
| `scripts/verify-code-health` | Dispatcher | Stable CI/local entry |
| `scripts/lib/code-health.py` | Implementation (stdlib + PyYAML) | Bloat/dup/orphan/ci-coverage/self-test |
| `tests/code-health/README.md` | How to run evaluation | Runtime-eval contract |
| `.github/workflows/agent-audit.yml` | chmod + self-test + live `verify-code-health`; grep marker | Every active check stays wired |
| `.githooks/pre-push` | Run live `verify-code-health` on `main` | Local complement to CI |
| `scripts/verify-semantic-hierarchy` | Require new files | Hierarchy cannot drop the registry |
| `scripts/agent-init` | CI grep includes `verify-code-health` | Init agrees with CI |
| `.ai/shared/references/testing.md` | Health commands | Stage 04 contract |
| `.ai/shared/references/icm-ci-policy.md` | Document new job steps | Fork parity |
| `architecture.md`, `conventions.md`, `repository-map.md` | Point at the registry | Durable memory |
| `.ai/agents/saul/roadmap.md` + `roadmap.json` | Semantic-tracking lane → active | CTO lane this implements |
| `.ai/runs/20260813-1315-codebase-health-cursor-cloud/` | Run artifacts | ICM audit trail |

## Out of scope

- Choosing the parent-app stack or adding ESLint/ruff/jscpd/coverage.
- Refactoring existing 400+ line files (thresholds sit above today's max of 478).
- Deduplicating intentional ICM template families.
- Merging this PR or marking it ready.

## Verification

- `python3 -m json.tool` on new/edited JSON
- YAML parse of `code-health.yaml` and `roadmap.json`
- `bash -n scripts/verify-code-health`
- `scripts/verify-code-health --self-test` (runtime evaluation)
- `scripts/verify-code-health` (live repo must pass)
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit` / `scripts/verify-merge-handoff` on the new range
- Disclose: GitHub Actions green is confirmed only after push

## Risks and rollback

- Near-duplicate Jaccard can false-positive on generated capability JSON; exclude `tools.json` / `hooks.json` and keep threshold high (0.95). Tune if self-test or live scan fails.
- Orphan heuristic is string mention, not a call graph — a script named only in a commit message is not a reference; a mention in docs counts. Acceptable until stack import graphs exist.
- Rollback: close the unmerged PR. No production impact.

## Review gates

No hard gates from `.ai/_config/security-policy.md`. New decision record + Saul roadmap edit: draft PR is the co-founder review gate. PLAN report posted before implementation. Do not merge.
