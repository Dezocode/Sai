---
name: verify-sai
description: Prove Sai ICM coordination, CLI verifiers, CI, hooks, and OpenClaw prototype surfaces via existing harnesses and the Go sai-verify kernel. Use for /verify-sai, cold feature/proof queries, or before claiming a PR preserves the protected map.
---
# Verify Sai
Sai has no product UI server. The observable app is the ICM workspace, Bash verifiers, git hooks, GitHub Actions, Cursor hooks, and the OpenClaw dashboard scaffold. This skill drives those real entry points. The native map under `features/` is canonical. `cmd/sai-verify` is the only machine parser.
## Launch
No long-lived process. `go test ./...`; `go run ./cmd/sai-verify doctor` (map+hooks). Completeness: `drive` then `doctor --evidence`. Teardown: none.
## Drive
Prefer existing harnesses. Driving bullets are `::` recipes parsed as data (`exec.CommandContext` argv, never `bash -lc`). Query context first: `go run ./cmd/sai-verify relevant --path <path> --tool <Tool>`. Cold agents: `go run ./cmd/sai-verify snapshot` (JSON) or `proof` (human). Every Cursor agent hook (`sessionStart` through `workspaceOpen`, including shell/MCP/read/edit/subagent) injects FEATURE CONTEXT or fail-closed deny. Cloud skips sessionStart/End, MCP, and workspaceOpen. Never invent a second feature list.
## Evidence
Proofs are command + exit + stdout/stderr, plus a second read of stored state for mutations. Record feature ID and entry point. Artifacts: `.ai/runs/<task-id>/04_verify/output/` (survive cleanup). Unreachable live paths must name the concrete prerequisite. Delete only temp dirs a drive created. Never kill by process name. Never delete evidence.
## Helpers
- `go run ./cmd/sai-verify snapshot|proof|doctor|relevant|preserve|hook|drive`; wrapper `.cursor/hooks/sai-verify.sh` (worktree-safe)
