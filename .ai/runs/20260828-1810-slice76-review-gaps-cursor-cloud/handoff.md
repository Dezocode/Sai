# Handoff: slice 76 review-gap fixes

## What changed

- Workflow paths include `internal/**`, `cmd/sai/**`, and `go.mod` so production-only lane violations cannot skip `sai-design-check`.
- Go import paths decode with `strconv.Unquote` (unicode-escape bypass closed).
- Versioned `Package@swift-*.swift` manifests are scanned.
- `resolvesInto` relative branch matches absolute `prototypes/` tree judgment.
- `go.work` `use(` / `replace(` without space opens blocks.

## Tests

`TestGoImportUnicodeEscapeFails`, `TestVersionedPackageManifestLaneFails`, `TestGoWorkUseWithoutSpaceIntoLaneFails`, `TestResolvesIntoRelativePrototypesTree`; workflow trigger test extended.

## Verify

CI on new HEAD; `go test ./cmd/sai-design-check/...` and `go test ./cmd/sai-verify/ -run Prototype`.
