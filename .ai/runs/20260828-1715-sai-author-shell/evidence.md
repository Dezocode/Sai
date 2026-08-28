# Evidence: slice 77 Author shell @ `f3072453`

Task-ID: 20260828-1715-sai-author-shell
Agent: cursor-cloud-agent
HEAD: `f3072453af86400f09bff67fae1fbe319d55f3fc`

## Author tree (`prototypes/plugins/author/` only)

| Path | Role |
|------|------|
| `Package.swift` | macOS 14 + iOS 17 package; `SaiAuthorMac` + `SaiAuthorIOS` executables |
| `Sources/SaiAuthor/AuthorRootView.swift` | Tab shell (Editor + Settings placeholders) |
| `Sources/SaiAuthor/EditorPlaceholder.swift` | `SaiCanvas` + `SaiText` via SaiDesignLanguage |
| `Sources/SaiAuthor/SettingsPlaceholder.swift` | `SaiCanvas` + `SaiText` via SaiDesignLanguage |
| `SaiAuthorMac/SaiAuthorMacApp.swift` | macOS `@main` entry |
| `SaiAuthorIOS/SaiAuthorIOSApp.swift` | iOS `@main` entry |
| `tests/delete-isolation.sh` | In-tree adversarial script (author-local) |
| `README.md` | Build instructions; no production manifest refs |

Dependency: `SaiDesignLanguage` from `apps/apple/Packages/SaiKit` via relative path only. Production `apps/apple` manifests do not reference this package.

## Delete-isolation proof

1. **No production refs:** `grep -R prototypes/plugins` over `apps/apple`, `cmd/sai`, `internal` must be empty.
2. **Adversarial delete:** move `prototypes/plugins/author/` aside, then:
   - `go run ./cmd/sai-design-check` PASS
   - `go test ./cmd/sai-verify/...` PASS
3. **Restore** author tree after proof.

Canonical runners:
- `scripts/verify-author-delete-isolation.py` (sai-verify `::py` recipe in `prototype-plugins.md`)
- `prototypes/plugins/author/tests/delete-isolation.sh` (in-tree duplicate; wrapper `scripts/verify-author-delete-isolation`)

Executed inside icm-enforcement step 16 "Verify sai-verify kernel and native map" @ `f3072453`.

## Verifier mapping (production Go, verify-only)

- `cmd/sai-verify/main.go` `pathRe` includes `prototypes` root.
- `.cursor/skills/verify-sai/features/prototype-plugins.md` maps lane + Author + isolation recipes.
- `cmd/sai-design-check` `isPrototypeLane()` fail-closed exemption for `prototypes/plugins/` only.
- `featureUIAllowed = false` unchanged in `SaiDesignLanguage.swift`.

Boundary tests @ HEAD:
- `TestPrototypeLaneAllowsSwiftUI` — SwiftUI allowed in-lane when production locked
- `TestNearPrefixCannotBecomePrototypeLane` — `prototypes/plugins-evil/` cannot bypass lock

## Exact-HEAD CI (all SUCCESS @ `f3072453`)

- icm-enforcement: https://github.com/Dezocode/Sai/actions/runs/33197869944
- Sai Design Language (Swift compile incl. Author shells): https://github.com/Dezocode/Sai/actions/runs/33197869921
- Anti-regression: https://github.com/Dezocode/Sai/actions/runs/33197866765
- PR line budget: https://github.com/Dezocode/Sai/actions/runs/33197866863
- Feature maps Pages: https://github.com/Dezocode/Sai/actions/runs/33197869923

## Out of scope (unchanged)

PiS AI (#158), full editor, lifecycle/integrate/spin-off engines, merge to main.
