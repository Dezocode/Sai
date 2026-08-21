# Verify Sai kernel
Future agents query the native pstack map through one Go API used by CLI, Cursor pre/post hooks, CI, and human proof. Protected BASE contracts cannot be deleted or rewritten in the same self-authorizing change.
## Sub-features
- `vs-skill` `.cursor/skills/verify-sai/SKILL.md` launch/doctor/drive/evidence/cleanup/helpers.
- `vs-map` `features/README.md` + feature files; no second manifest.
- `vs-parse` `cmd/sai-verify/main.go` via `go run ./cmd/sai-verify snapshot` parses/validates index links, IDs, duplicate/dead/unindexed files.
- `vs-relevant` `… relevant --path P --tool T` returns title/why/subfeatures/entry_points/proofs/gotchas/paths; tool can change the hit set.
- `vs-preserve` `… preserve` compares BASE vs HEAD sets of IDs, entry lines, and proof recipes. Only BASE `Removal-authorized:` counts. Missing trusted base fails closed. No map on BASE is bootstrap (nothing to preserve).
- `vs-proof` `… proof` prints observed PASS/FAIL/REQUIRED/UNEVALUATED/UNREACHABLE/UNPROVEN only.
- `vs-doctor` `… doctor` fail-closed map+hooks+HEAD; `--evidence` requires a value and proven completeness; receipts fail closed unless repo, BASE, HEAD, and map_hash all match.
- `vs-hook-pre` `.cursor/hooks.json` `preToolUse` matcher `.*` `failClosed: true` → `.cursor/hooks/sai-verify.sh` (deny on map/preserve/stale HEAD/unbound evidence; FEATURE CONTEXT; no `permission: allow`; wrapper builds BASE kernel only).
- `vs-hook-post` `postToolUse` matcher `.*` recomputes from current git; `additional_context` (no queue).
- `vs-hook-stop` `stop` follow-up only while map/preserve/maintenance obligations remain.
- `vs-hook-session` `sessionStart` failClosed injects FEATURE CONTEXT (Desktop/CLI; Cloud does not fire sessionStart).
- `vs-hook-all` remaining Cursor agent events (`sessionEnd`,`postToolUseFailure`,`subagentStart/Stop`,`before/afterShellExecution`,`before/afterMCPExecution`,`beforeReadFile`,`afterFileEdit`,`beforeSubmitPrompt`,`preCompact`,`afterAgentResponse/Thought`,`workspaceOpen`) same wrapper failClosed; integrity deny; others inject FEATURE CONTEXT. Cloud skips sessionStart/End, MCP, workspaceOpen. Tab `beforeTabFileRead`/`afterTabFileEdit` not registered (IDE Tab, not agent tools).
- `vs-module` `go.mod` module `github.com/Dezocode/Sai`; `go test ./...` and `go vet ./...`.
- `vs-ci` agent-audit exact candidate `head.sha` test/vet/drive/doctor; trusted anti-regression uses BASE binary after merge.
- `vs-synthetic` `cmd/sai-verify/main_test.go`: A–H future-PR plus #68 consumer (cold relevant title/why/gotchas, pre/post FEATURE CONTEXT, tool Read vs Shell vs MCP).
## How to get to it (user POV)
- `/verify-sai` (`.cursor/skills/verify-sai/SKILL.md`). Cold: `go run ./cmd/sai-verify snapshot|proof|doctor|drive|preserve|hook|relevant --path <file> --tool Read`. Agent loop: `.cursor/hooks.json`. CI: agent-audit + post-merge BASE preserve. Maintain: `/maintain-verification-skill` on this folder.
## Driving it with verify-sai
- **Doctor.** ::sai doctor
- **Hooks.** ::json .cursor/hooks.json
- **Module.** ::contains go.mod github.com/Dezocode/Sai
- **Tests.** ::gotest -race ./... timeout=180
- **Vet.** ::govet ./...
- **Proof.** ::sai proof
## Gotchas
- Recompute from repo+HEAD; conversation memory is not proof. Success hooks omit `permission` so they cannot override an adjacent deny. Matcher `.*` required; empty matcher fails hooks_ok. Cloud Agents do not run sessionStart/End, before/afterMCPExecution, or workspaceOpen; Desktop/CLI do. Protected delete/rewrite fails preserve once BASE has the kernel. HEAD `Removal-authorized:` is ignored. Completeness is every tracked file except `.ai/runs/` and bytecode (`__pycache__`/`node_modules`/`.pyc`); map Paths claim `.ai/*` `.cursor/*` `.github/*` `.githooks/*` `scripts/*` `openclaw-dashboard/*` `cmd/*`. `map_hash` walks those mapped roots plus protected `cmd` `.cursor/hooks` `.github/policy` `.github/workflows` `go.mod`, so a dirty verifier, registry, stage, or skill cannot keep a prior receipt bound. Completeness sweep matches git paths exactly, by `{a,b}` expansion, or by a `/*` tree glob's directory prefix, never by a truncated brace or substring. `scripts/agent-report` recipes require `read=`/`has=` and a new queued file after exec. Stale-hook recovery is exactly `go run ./cmd/sai-verify drive` or `proof` with no extra flags; drive writes `--evidence` only under HEAD, gitdir, `os.TempDir()`, `/tmp/`, or `RUNNER_TEMP`. The Go kernel denies mutations when evidence is unbound. Receipts fail closed unless `repo`, BASE, HEAD, and `map_hash` are present and match and the current unmapped set is empty. Flags that take a value error when the value is missing. Local hook runs a BASE-built kernel when BASE has `cmd/sai-verify` and does not compile candidate Go during bootstrap (bootstrap injects context and does not deny; otherwise the introducing PR cannot land). Policy rejects `func init(`, `plugin.Open`, and aliased `syscall`/`os/exec` imports in non-test kernel sources. `proof` prints every `/goal` field and writes `sai-verify-proof.json` beside `--evidence`; CI uploads both as exact-HEAD artifacts.
