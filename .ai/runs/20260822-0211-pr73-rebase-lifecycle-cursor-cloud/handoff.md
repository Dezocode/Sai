# Handoff 20260822-0211-pr73-rebase-lifecycle-cursor-cloud

START_HEAD=`7edbe3a2e95804231428f5e61bfb11c147a46073`
MERGE_HEAD=`5697d732f252c36dcc2dd88ee345a1d49fb31e03` (GitHub REST merge of `main`; local rebase blocked by hooks after `cmd/sai-verify/main.go` conflict. Auto-merge kept pathRe product roots and fail-closed mapsCmd.)
BASE=`d40cf3346f263478895607c810ce0b30ede12a1e`

Product goal unchanged. Foundation only. Draft PR 73.

P1 CODEX-UNIT-0034-0001 hang DISPROVED. `Server.Shutdown` sets inShutdown; later `Serve` returns `http.ErrServerClosed`. `TestRunCanceledBeforeListen` kept.
P2 watcher leak FIXED. `context.WithCancel` + `stop()` after `Serve` + always `<-shutErr`. Go 1.16. No go.mod change.

Next: candidate CI on this HEAD, then stop for fresh Saul. Do not merge.
