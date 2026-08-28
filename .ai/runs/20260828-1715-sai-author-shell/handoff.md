# Handoff: Sai Author reference shell (slice 77)

Task-ID: 20260828-1715-sai-author-shell
HEAD: `f3072453af86400f09bff67fae1fbe319d55f3fc` (code); evidence mint commit follows.

## Done

- Added `prototypes/plugins/author/` macOS + iOS placeholder package using SaiDesignLanguage.
- Mapped `prototypes/*` in sai-verify feature map and path parser.
- Added delete-isolation proof (`scripts/verify-author-delete-isolation.py` + in-tree `tests/delete-isolation.sh`).
- Restored full `cmd/sai-verify/main.go`; reverted forbidden `allowBin` widening.
- Fixed ICM `metadata.json` required fields (`repository`, `status`).
- Added verifier-owned `prototypes/plugins/` exemption in `cmd/sai-design-check`.

## `/goal` evidence (Author shell under `prototypes/plugins/author/` only)

### Author tree

| Path | Role |
|------|------|
| `Package.swift` | macOS 14 + iOS 17; `SaiAuthorMac` + `SaiAuthorIOS` executables |
| `Sources/SaiAuthor/AuthorRootView.swift` | Tab shell (Editor + Settings placeholders) |
| `Sources/SaiAuthor/EditorPlaceholder.swift` | `SaiCanvas` + `SaiText` |
| `Sources/SaiAuthor/SettingsPlaceholder.swift` | `SaiCanvas` + `SaiText` |
| `SaiAuthorMac/SaiAuthorMacApp.swift` | macOS `@main` |
| `SaiAuthorIOS/SaiAuthorIOSApp.swift` | iOS `@main` |
| `tests/delete-isolation.sh` | In-tree adversarial delete proof |

Depends on `SaiDesignLanguage` via relative SaiKit path only. Production manifests do not reference this package.

### Delete-isolation proof

1. `grep -R prototypes/plugins` over `apps/apple`, `cmd/sai`, `internal` must be empty.
2. Move `prototypes/plugins/author/` aside; run `go run ./cmd/sai-design-check` and `go test ./cmd/sai-verify/...`; both PASS.
3. Restore author tree.

Runners: `scripts/verify-author-delete-isolation.py` (`::py` in `prototype-plugins.md`); in-tree `tests/delete-isolation.sh`.

Executed in icm-enforcement step 16 @ `f3072453`.

### Verifier mapping (verify-only production Go)

- `cmd/sai-verify/main.go` `pathRe` includes `prototypes`.
- `prototype-plugins.md` feature map with `::exists`, `::py`, `::contains featureUIAllowed = false`.
- `cmd/sai-design-check` `isPrototypeLane()` for `prototypes/plugins/` only.
- Tests: `TestPrototypeLaneAllowsSwiftUI`, `TestNearPrefixCannotBecomePrototypeLane`.

### Exact-HEAD CI @ `f3072453`

- icm-enforcement: https://github.com/Dezocode/Sai/actions/runs/33197869944
- Sai Design Language: https://github.com/Dezocode/Sai/actions/runs/33197869921
- Anti-regression, PR line budget, Feature maps Pages: all SUCCESS (11/11 checks).

## Verify

- `scripts/verify-author-delete-isolation.py`
- `swift build --package-path prototypes/plugins/author` (macOS CI)
- `go test ./cmd/sai-design-check/... -run PrototypeLane`

## Next

- Saul Product Quality on HEAD (Origin runs in parallel).
- Stay draft until owner merge approval.
