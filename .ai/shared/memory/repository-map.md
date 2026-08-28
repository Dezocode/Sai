# SAI — Repository map

> Verified 2026-08-28 against `Dezocode/Sai:main` at `b429c7cc` (prototype lane
> enforcement, PR #136). Prior: 2026-08-20 `/lauren-mode` skills; 2026-08-13
> pstack plugin install; 2026-07-14 against commit `34827e7`. Keep current when
> top-level structure changes.

| Path | Purpose |
|---|---|
| `README.md` | Product description |
| `Team.md` | Team page (currently empty) |
| `.ai/` | ICM agent workspace — see `.ai/CONTEXT.md` |
| `.ai/INITIALIZE.md` | Read-and-execute initialization protocol for new agents |
| `.ai/_config/` | Repository, reporting, sync, security policy |
| `.ai/agents/` | Role charters (`_roles/`), `registry.json`, named agent folders |
| `.ai/shared/memory/` | Durable memory (this folder) |
| `.ai/shared/schemas/` | JSON Schemas for events and stage outputs |
| `.ai/shared/references/` | Git workflow, testing, release policy, ICM CI policy, **agent-runtimes.md** |
| `CLAUDE.md` / `CODEX.md` | Layer 0 entry routers for Claude Code and Codex Desktop |
| `.ai/plugins/` | ICM index of Cursor Marketplace plugins this repo enables (not a Cursor loader) |
| `.ai/stages/` | Six ICM stage contracts |
| `.ai/runs/` | Per-task working artifacts (Layer 4) |
| `.ai/audit/` | Audit trail documentation |
| `.cursor/settings.json` | Project-scoped Cursor plugins (slash commands for cloud + local) |
| `.cursor/skills/` | Project Agent Skills (Custom Mode: `/lauren-mode`, alias `/lauren`) |
| `.cursor/rules/` | Shared Cursor operating rules (`sai-coordination.mdc`, `pstack-models.mdc`, `lauren-mode.mdc`) |
| `.githooks/` | Reporting git hooks |
| `scripts/` | agent-init, agent-scaffold, agent-verify-caps, agent-automation-spec, agent-report, agent-sync-drive, install-agent-hooks, verify-agent-audit, verify-semantic-hierarchy |
| `cmd/sai/` | Production Go server entrypoint |
| `cmd/sai-verify/` | Sai feature-map verifier kernel (CLI, Cursor hooks, CI proofs) |
| `cmd/sai-design-check/` | Sai Design Language checker (includes prototype-lane structural enforcement) |
| `prototypes/plugins/` | Canonical non-shipping prototype plugin root (verifier-owned; one-way isolation from production) |
| `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` | Enabling contract for the prototype plugin lane (PR #75) |
| `docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md` | Lane enforcement implementation contract (PR #136) |
| `.github/workflows/` | CI audit + semantic hierarchy verification |

## Remotes and fork topology

- `Dezocode/Sai` — canonical, not a fork, default branch `main`.
- `monaecode/Sai` — fork of `Dezocode/Sai`, default branch `main`.
- Feature-branch names are ephemeral. This map does not inventory remote
  branches.
