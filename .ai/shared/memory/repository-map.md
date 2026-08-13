# SAI — Repository map

> Verified 2026-08-13 against the codebase-health branch (decision 0005
> registry + `scripts/verify-code-health`). Prior: pstack plugin index;
> 2026-07-14 against `34827e7` on `Dezocode/Sai:main`.
> Keep current when top-level structure changes.

| Path | Purpose |
|---|---|
| `README.md` | Product description |
| `Team.md` | Team page (currently empty) |
| `.ai/` | ICM agent workspace — see `.ai/CONTEXT.md` |
| `.ai/INITIALIZE.md` | Read-and-execute initialization protocol for new agents |
| `.ai/_config/` | Repository, reporting, sync, security, **code-health.yaml**, **authorization.yaml** |
| `.ai/requests/` | Task authorization intake (`request.yaml` per task-id) |
| `.ai/shared/schemas/` | JSON Schemas for events, contracts, authorization, reviews |
| `.ai/agents/` | Role charters (`_roles/`), `registry.json`, named agent folders |
| `.ai/shared/memory/` | Durable memory (this folder) |
| `.ai/shared/references/` | Git workflow, testing, release policy, ICM CI policy, **code-health.md**, **agent-runtimes.md** |
| `CLAUDE.md` / `CODEX.md` | Layer 0 entry routers for Claude Code and Codex Desktop |
| `.ai/plugins/` | ICM index of Cursor Marketplace plugins this repo enables (not a Cursor loader) |
| `.ai/stages/` | Six ICM stage contracts |
| `.ai/runs/` | Per-task working artifacts (Layer 4) |
| `.ai/audit/` | Audit trail documentation |
| `.cursor/settings.json` | Project-scoped Cursor plugins (slash commands for cloud + local) |
| `.cursor/rules/` | Shared Cursor operating rules |
| `.githooks/` | Reporting git hooks |
| `scripts/` | agent-init, sai-authorize-task, sai-assume-agent, sai-release-agent, verify-agent-authorization, verify-contract-authorization, invoke-saul-review, consume-saul-contract-review, verify-code-health, … |
| `tests/authorization/` | Lifecycle e2e for decision 0006 |
| `.github/workflows/` | `agent-audit.yml` (ICM + authorization replay); `saul-review.yml` (Codex/Saul) |
| `tests/code-health/` | Runtime-evaluation contract for health detectors (fixtures built in `/tmp`) |

## Remotes and fork topology

- `Dezocode/Sai` — canonical, not a fork, default branch `main`.
- `monaecode/Sai` — fork of `Dezocode/Sai`, default branch `main`.
- Existing remote branches at time of writing: `main`,
  `cursor/cloud-env-setup-532b`, `cursor/sai-agent-framework-30d8`.
