# Duplication: git() helper in both Go CLIs

Issue: https://github.com/Dezocode/Sai/issues/181

## Problem

Both Go CLIs carry their own copy of the same security-relevant git
helper — byte-identical except the parameter name:

- `cmd/sai-verify/main.go:629` — `func git(dir string, args ...string) string`
- `cmd/sai-design-check/main.go:620` — `func git(root string, args ...string) string`

Both run `git -c safe.directory=* -C <dir>` and return trimmed stdout
(`""` on any failure).

## Impact

The `safe.directory=*` invocation is a security-relevant detail
duplicated in two CLIs. A hardening change (e.g. dropping the wildcard,
or switching to fail-closed error handling) must hit both copies or
protection silently differs between the two tools. The comment in the
`sai-design-check` copy ("gates needing fail-closed errors call exec
directly") documents a convention that only exists as a comment — a
shared helper is the place to enforce it.

## Recommended consolidation

Move to the existing shared package `internal/app` as an exported
helper (e.g. `app.Git(dir string, args ...string) string`); both CLIs
use it. This fits the team's ongoing shared-Go-code consolidation
direction.

## Steering prompt (agent-executable)

> In Dezocode/Sai, deduplicate the `git()` helper per
> https://github.com/Dezocode/Sai/issues/181. (1) Add an exported
> helper to the existing shared package `internal/app` — e.g.
> `func Git(dir string, args ...string) string` — with the exact
> current semantics: `git -c safe.directory=* -C <dir>`, trimmed
> stdout, `""` on any failure. (2) Replace the private copies at
> `cmd/sai-verify/main.go:629` and `cmd/sai-design-check/main.go:620`
> with calls to the shared helper; keep the
> `sai-design-check` comment about fail-closed gates by moving that
> convention into the shared helper's doc comment. (3) `go build ./...`
> and run the affected CLI tests. Do not change behavior — only where
> the code lives. Open a PR; do not merge it yourself.
