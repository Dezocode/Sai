# Verify Sai kernel
Future agents query the native pstack map through one Go API used by CLI, Cursor pre/post hooks, CI, and human proof. Protected BASE contracts cannot be deleted or rewritten in the same self-authorizing change.
## Sub-features
- `vs-skill` `.cursor/skills/verify-sai/SKILL.md` launch/doctor/drive/evidence/cleanup/helpers.
- `vs-map` `features/README.md` + feature files; no second manifest.
- `vs-parse` `cmd/sai-verify/main.go` via `go run ./cmd/sai-verify snapshot` parses/validates index links, IDs, duplicate/dead/unindexed files.
- `vs-relevant` `… relevant --path P --tool T` derives matches; tool can change the hit set.
- `vs-preserve` `… preserve` compares BASE vs HEAD sets of IDs, entry lines, and proof recipes. Only BASE `Removal-authorized:` counts. Missing trusted base fails closed. No map on BASE is bootstrap (nothing to preserve).
- `vs-proof` `… proof` prints observed PASS/FAIL/REQUIRED/UNEVALUATED/UNREACHABLE/UNPROVEN only.
- `vs-doctor` `… doctor` fail-closed map+hooks+HEAD; `--evidence` also requires whole-repo completeness proven.
- `vs-hook-pre` `.cursor/hooks.json` `preToolUse` matcher `.*` `failClosed: true` → `.cursor/hooks/sai-verify.sh` (deny on map/preserve/stale HEAD; no `permission: allow`).
- `vs-hook-post` `postToolUse` matcher `.*` recomputes from current git; `additional_context` (no queue).
- `vs-hook-stop` `stop` follow-up only while map/preserve/maintenance obligations remain.
- `vs-hook-session` `sessionStart` failClosed injects the same snapshot JSON as pre/post.
- `vs-hook-all` remaining Cursor agent events (`sessionEnd`,`postToolUseFailure`,`subagentStart/Stop`,`before/afterShellExecution`,`before/afterMCPExecution`,`beforeReadFile`,`afterFileEdit`,`beforeSubmitPrompt`,`preCompact`,`afterAgentResponse/Thought`,`workspaceOpen`) same wrapper failClosed; integrity deny; others inject snapshot JSON.
- `vs-module` `go.mod` module `github.com/Dezocode/Sai`; `go test ./...` and `go vet ./...`.
- `vs-ci` agent-audit exact candidate `head.sha` test/vet/drive/doctor; trusted anti-regression uses BASE binary after merge.
- `vs-synthetic` `cmd/sai-verify/main_test.go`: A–H future-PR (unchanged, additive, delete, proof/entry replace, candidate Removal-authorized, missing base, stale HEAD, self-weakening, worktree).
## How to get to it (user POV)
- Cold: `go run ./cmd/sai-verify snapshot|proof|relevant --path <file> --tool Read`. Agent loop: `.cursor/hooks.json`. CI: agent-audit + post-merge BASE preserve. Maintain: `/maintain-verification-skill` on this folder.
## Driving it with verify-sai
Preconditions: Go 1.16+; repo root.
- **Doctor.** `go run ./cmd/sai-verify doctor`; exit 0 when map+hooks hold.
- **Snapshot.** `go run ./cmd/sai-verify snapshot`; JSON `map_valid`, `head` matches `git rev-parse HEAD`.
- **Hook pre.** `printf '%s' '{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}' | go run ./cmd/sai-verify hook`; exit 0; `additional_context` has `map_valid`; no `permission` key.
- **Hook post.** same with `postToolUse` and `tool_output`; stdout has `additional_context`.
- **Preserve.** `go run ./cmd/sai-verify preserve`; exit 0 (bootstrap if BASE has no map).
- **Session hook.** `printf '%s' '{"hook_event_name":"sessionStart"}' | go run ./cmd/sai-verify hook`; `additional_context` has `map_valid`.
- **Shell hook.** `printf '%s' '{"hook_event_name":"beforeShellExecution","command":"true"}' | go run ./cmd/sai-verify hook`; exit 0; no `permission` key.
- **Module.** `test -f go.mod && grep -q github.com/Dezocode/Sai go.mod`
- **Tests.** `go test -race ./...`; `go vet ./...`
- **Proof.** `go run ./cmd/sai-verify proof`
## Gotchas
- Recompute from repo+HEAD; conversation memory is not proof. Success hooks omit `permission` so they cannot override an adjacent deny. Matcher `.*` required; empty matcher fails hooks_ok.
- Protected delete/rewrite fails preserve once BASE has the kernel. HEAD `Removal-authorized:` is ignored.
