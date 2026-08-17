# Handoff — 20260817-2002-pr69-verify-sai-cursor-cloud

PR #69 `/goal` on `verification/repo-feature-map`. Do not merge/mark ready. Do not claim 100% map coverage: parent-folder IDs still group agent files; pstack slash catalog is marketplace not Sai; `.ai/projects/mimi-dispatcher/` is missing on disk (product gap).
Kernel `cmd/sai-verify` is the only parser. Cursor agent hooks (19 events, failClosed) all call `.cursor/hooks/sai-verify.sh`. Permission events deny on map/preserve failure; others inject snapshot JSON.
Exact-HEAD: `go test -race ./...`; `go vet ./...`; `go run ./cmd/sai-verify doctor|proof`. Unreachable: live gateway (`openclaw` CLI); ingest/MCQ/session/run-all stubs; connection-gate fail-closed without registry evidence.
Maintain pass: source wave + live drive of mapped recipes (73 pass / 0 fail on named drives). Saul P1s remain Hostinger toolchain (no gcc / `go -version`); do not wait. Next: rebase #68 after merge; re-sweep IDs after any new concrete surface.
