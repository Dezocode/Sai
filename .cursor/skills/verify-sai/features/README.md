# Sai verification map
Maintained source for every supported/observable Sai capability proved by this repository. Read this index, then the feature file. Grouping is for reader clarity; sub-feature IDs and entry points are the contract.
## Baseline preconditions
- Work from the git repo root of `Dezocode/Sai` or `monaecode/Sai`.
- `python3`, `bash`, `git`, `go` (≥1.22) on PATH. `rclone` and Slack/Drive tokens are optional.
- Run `go run ./cmd/sai-verify doctor` and require exit 0.
- Reuse existing `scripts/*` and `openclaw-dashboard/**` harnesses; do not wrap them in a second verifier.
## Driving conventions
- Start from a clean worktree unless the recipe mutates a fixture copy.
- Treat commands as literal. Capture exit code and output.
- Bind every machine result to repository + base SHA + exact HEAD SHA via `sai-verify`.
- Report unreachable live services with the attempted command and unmet prerequisite. Do not mark them verified via a different path.
## Proof and skip reporting
- Exercise the real operator/agent path (script, hook, workflow, protocol file), not an internal stub that the map does not name.
- Mutation proof includes a second read of the resulting file/queue/exit.
- Record feature ID + entry point on every artifact.
- Stubs that exit 2 by design are live-proven as stub-exit-2, not as success.
## Feature entry contract
Each file: H1, one user-visible paragraph, then `Sub-features`, `How to get to it (user POV)`, `Driving it with verify-sai`, `Gotchas`.
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
- [Verify Sai kernel](./verify-sai.md) — native map, Go API, hooks, preservation, proof.
