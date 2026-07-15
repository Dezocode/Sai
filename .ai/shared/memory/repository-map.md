# SAI — Repository map

> Verified 2026-07-14 against commit `34827e7` on `Dezocode/Sai:main`.
> Keep current when top-level structure changes.

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
| `.ai/stages/` | Six ICM stage contracts |
| `.ai/runs/` | Per-task working artifacts (Layer 4) |
| `.ai/audit/` | Audit trail documentation |
| `.cursor/rules/` | Shared Cursor operating rules |
| `.githooks/` | Reporting git hooks |
| `scripts/` | agent-init, agent-scaffold, agent-verify-caps, agent-automation-spec, agent-report, agent-sync-drive, install-agent-hooks, verify-agent-audit, verify-semantic-hierarchy |
| `.github/workflows/` | CI audit + semantic hierarchy verification |

## Remotes and fork topology

- `Dezocode/Sai` — canonical, not a fork, default branch `main`.
- `monaecode/Sai` — fork of `Dezocode/Sai`, default branch `main`.
- Existing remote branches at time of writing: `main`,
  `cursor/cloud-env-setup-532b`, `cursor/sai-agent-framework-30d8`.
