# Intake — codebase health gates before application code

- Task-ID: `20260813-1315-codebase-health-cursor-cloud`
- Agent: `cursor-cloud` (unnamed Cloud Agent; not in `registry.json`)
- Requester: dezocode (`U0BHYH0NMCY`)
- Source: Cursor Cloud Agent run `bc-019ffb40-0226-731b-9d22-f5f991d490ba` (mobile), prompt: `/plan how to ensure codebase health as we start to build the app for it to reliably be checked for health of code, no semantic duplicates, no orphans, no bloated files, ci integration for every health check and runtime evaluation`
- Date (UTC): 2026-08-13

## Requested outcome

A durable way to keep the repository healthy **as application code starts to land**:

1. Reliable, repeatable **code health** checks.
2. **No semantic duplicates** (same behavior/content in two places).
3. **No orphans** (unreferenced scripts, dead files).
4. **No bloated files** (oversized modules/docs).
5. **CI integration for every health check** — a check that is not in CI does not count.
6. **Runtime evaluation** — each check is proven by a self-test (known-good pass and known-bad fail), not only by running against a currently-green tree.

## Repository facts (command-backed)

| Fact | Value | Evidence |
|---|---|---|
| Toplevel | `/workspace` | `git rev-parse --show-toplevel` |
| Origin | `github.com/Dezocode/Sai` (canonical, not a fork) | `git remote -v`; `gh repo view` `isFork: false` |
| Default branch | `main` | `gh repo view` `defaultBranchRef.name` |
| Start SHA | `40efe0a0724764fc1cf3c45ed8498b5606a0f453` | `git rev-parse HEAD` |
| Start branch | `main` (clean) | `git status`: up to date with `origin/main`, nothing to commit |
| Task branch | `cursor/codebase-health-90ba` | created from `main` at `40efe0a` |

## Current health surface (verified)

- CI is a single workflow `.github/workflows/agent-audit.yml` covering ICM audit, hierarchy, handoff, agent-setup, scaffold safety, contract allowlists, JSON parse, and selected OpenClaw prototype self-tests.
- There is **no** registry that lists every check, **no** bloat/orphan/duplicate gates, and **no** meta-check that a new `scripts/verify-*` must appear in CI.
- Saul roadmap lane `observability` (semantic tracking) is `proposed`; lane `ci` is `active` with next step "Add stack checks only when the stack exists."
- Application product stack is **not** accepted (`architecture.md`; DR-20260724 bounds `openclaw-dashboard/` as prototype documentation). Largest tracked file today is 478 lines.

## Constraints

- No application stack decision yet — do not add language-specific linters, coverage tools, or npm/pip dependencies.
- Stdlib Python + existing PyYAML + bash only (AGENTS.md toolchain).
- Hard security gates in `.ai/_config/security-policy.md` do not apply (no secrets, force-push, access, or production deploy). A new decision record is an architectural change; the draft PR is the human review gate.
- Do not merge to `main`. Do not mark the PR ready.
- Stale `in_progress`/`active` runs do not claim CI, `scripts/verify-*`, or testing references.
- Exact content duplicates already exist as ICM templates (runtime README stubs, mirrored `automation/profile.md`, empty agent memory jsonl). Those families must be classified, not blindly failed.

## Acceptance criteria

- A versioned registry (`.ai/_config/code-health.yaml`) is the source of truth for every health check: active vs deferred, command, CI marker, self-test mode.
- CI fails if an **active** check is missing from `.github/workflows/agent-audit.yml`, or if a `scripts/verify-*` file is not in the registry.
- Active dispatcher checks cover **bloat**, **exact/near duplicates**, and **orphans**, with runtime `--self-test` (synthetic known-bad trees must fail; known-good must pass).
- Deferred entries exist for stack-specific unit tests, import-graph orphans, and clone detection once application source exists.
- `testing.md`, ICM CI policy, Saul roadmap semantic-tracking lane, and a decision record document the policy.

## Existing uncommitted changes

None. Working tree was clean at intake; task branch created from `main`.
