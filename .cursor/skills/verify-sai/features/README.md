# Sai verification map
Maintained source for every supported/observable Sai capability proved by this repository. Grouping is for reader clarity; sub-feature IDs and entry points are the contract.
## Baseline
- Git root of `Dezocode/Sai` or `monaecode/Sai`. `python3`, `bash`, `git`, `go` (≥1.16); rclone/Slack/Drive optional. Drive `::` recipes then `go run ./cmd/sai-verify doctor --evidence <receipt>`. Bind receipts to repo + BASE + exact HEAD + map/kernel/hook digest. Stub `expect=2` is stub-exit-2, not success.
## Features
- [ICM workspace](./icm-workspace.md) — layers, stages, runs, memory, schemas, policy, references.
- [Agent lifecycle](./agent-lifecycle.md) — initialize, onboard, registry, named agents, scaffolds, caps, automation.
- [Coordination reporting](./coordination-reporting.md) — agent-report, git hooks, Drive sync, merge Slack.
- [Verification gates](./verification-gates.md) — audit, hierarchy, handoff, setup, scaffold safety, shell allowlist.
- [Contracts and projects](./contracts-projects.md) — contract scaffold/review/templates and project indexes.
- [Protected CI](./protected-ci.md) — agent-audit, anti-regression, line budget.
- [Cursor and runtimes](./cursor-runtimes.md) — plugins, pstack, rules, runtime entry routers.
- [OpenClaw surfaces](./openclaw-surfaces.md) — dashboard tabs, settings, apps, design.
- [OpenClaw operations](./openclaw-ops.md) — gateway, fleet, secrets, services, smoke.
- [Foundry read-only Integrate planner](./foundry-integrate-planner.md) — slice 79 integrate planner under `prototypes/plugins/foundry/integrate-planner/`.
- [Verify Sai kernel](./verify-sai.md) — native map, Go API, hooks, preservation, proof.
- [Sai application foundation](./sai-app-foundation.md) — native Apple app, Go core, API, deployment, and CI-enforced design language.
