# Implement — pstack project enablement

- Task-ID: `20260813-0113-pstack-plugin-install-cursor-cloud`
- Plan: `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/02_plan/output/plan.md`
- Branch: `cursor/pstack-plugin-install-10de`

## What changed and why

| Path | Why (plan section) |
|---|---|
| `.cursor/settings.json` | Project-scope marketplace enablement so `/` works in cloud and local. |
| `.ai/plugins/README.md` | ICM index of enabled Cursor plugins; states `.ai/` is not a loader. |
| `.ai/plugins/pstack/manifest.json` | Stable identity, slash-command list, observed version 0.14.0. |
| `.ai/plugins/pstack/README.md` | How to invoke from command input; cloud vs local; `/setup-pstack` home-dir caveat. |
| `.ai/shared/memory/decisions/0004-cursor-project-plugins.md` | Durable decision: settings.json is the loader; `.ai/plugins/` is the index. |
| `.ai/CONTEXT.md` | Layer 0 workspace map names `.ai/plugins/` and `.cursor/settings.json`. |
| `AGENTS.md` | Cloud Agents read this; tells them `/poteto-mode` is project-enabled. |
| `.ai/shared/references/agent-runtimes.md` | Cursor suite row points at project plugins. |
| `.ai/shared/memory/conventions.md` | How to add the next plugin without vendoring. |
| `.ai/shared/memory/architecture.md` | Agent-system architecture mentions decision 0004. |
| `.ai/shared/memory/repository-map.md` | Top-level map includes `.ai/plugins/` and `.cursor/settings.json`. |
| `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/` | ICM audit trail. |

## Not changed (intentional)

- No vendored copy of `github.com/cursor/plugins/pstack`.
- No `.cursor/rules/pstack-models.mdc` (model routing left to `/setup-pstack` / a later task).
- No `cursor-team-kit`.
- `environment.json` untouched (no plugins key).

## Diff vs claimed files

All edited paths are in `metadata.json` `claimed_files` (including
`architecture.md` and `repository-map.md`, added when Layer 3 memory needed
the same map update).
