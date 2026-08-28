# Handoff — restore sai-verify main.go

Restored full `cmd/sai-verify/main.go` from commit `9b0ca68dc300e1b47670abe5c5119fae1ed15e9f`, replacing the truncated tip at `212c916`.

Edits applied:
- `pathRe`: added `prototypes|` after `openclaw-dashboard|` (before `cmd|`)
- `recipe.err()` gotest case: added `!strings.HasPrefix(a, "./prototypes/") &&` after the `./cmd/` check

Next safe action: run `go test ./cmd/sai-verify/...` on branch tip and confirm CI agent-audit passes.
