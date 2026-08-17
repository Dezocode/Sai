# Verify Sai kernel
Future agents query the native pstack map through one Go API used by CLI, Cursor pre/post hooks, CI, and human proof. Protected BASE IDs cannot be deleted in the same self-authorizing change.
## Sub-features
- `vs-skill` `.cursor/skills/verify-sai/SKILL.md` launch/doctor/drive/evidence/cleanup/helpers.
- `vs-map` `features/README.md` + feature files; no second manifest.
- `vs-parse` `go run ./cmd/sai-verify snapshot` parses/validates index links, IDs, duplicate/dead/unindexed files.
- `vs-relevant` `… relevant --path P --tool T` derives matches; not stored as canonical state.
- `vs-preserve` `… preserve --base DIR --head DIR` BASE feature/sub-feature IDs must remain unless BASE already lists `Removal-authorized:`.
- `vs-proof` `… proof` human report from the same snapshot as JSON.
- `vs-doctor` `… doctor` fail-closed map+hooks+HEAD.
- `vs-hook-pre` `.cursor/hooks.json` `preToolUse` matcher `.*` `failClosed: true` → `.cursor/hooks/sai-verify.sh`
- `vs-hook-post` `postToolUse` matcher `.*` recomputes from current git; `additional_context` (no queue).
- `vs-hook-stop` `stop` follow-up only while map/preserve/maintenance obligations remain.
- `vs-ci` agent-audit exact-HEAD Go test/vet/doctor; trusted anti-regression uses BASE binary after merge.
- `vs-synthetic` Go tests: unchanged capability, added capability, protected delete fail, stale HEAD reject, cold snapshot.
## How to get to it (user POV)
- Cold: `go run ./cmd/sai-verify snapshot` or `proof` or `relevant --path <file> --tool Read`
- Agent loop: automatic via `.cursor/hooks.json`
- CI: agent-audit + (post-merge) trusted anti-regression preserve
- Maintain map: `/maintain-verification-skill` on `.cursor/skills/verify-sai/`
## Driving it with verify-sai
Preconditions: Go 1.16+; repo root.
- **Doctor.** `go run ./cmd/sai-verify doctor`; exit 0.
- **Snapshot.** `go run ./cmd/sai-verify snapshot`; JSON `ok`, `head` matches `git rev-parse HEAD`.
- **Hook pre.** `printf '%s' '{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}' | go run ./cmd/sai-verify hook`; `permission` allow; context names `icm-workspace` or `verify-sai`.
- **Hook post.** same with `postToolUse` and `tool_output`; stdout has `additional_context`.
- **Preserve self.** `go run ./cmd/sai-verify preserve --base . --head .`; exit 0.
- **Tests.** `go test -race ./...`; `go vet ./...`
- **Proof.** `go run ./cmd/sai-verify proof`
## Gotchas
- Conversation memory is not a proof source; recompute from repo+HEAD each invocation.
- Deleting a feature file and its index row in one PR fails preserve once BASE has the kernel.
- `Removal-authorized: id` must already exist on BASE before HEAD may drop that id.
- Hook matcher must stay `.*` (or equivalently complete); narrowing is a required-hook failure.
