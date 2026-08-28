# Handoff: Sai Author reference shell (slice 77)

Task-ID: 20260828-1715-sai-author-shell
Agent: cursor-cloud-agent

## Done

- `prototypes/plugins/author/` macOS + iOS placeholder package using SaiDesignLanguage only.
- Delete-isolation proof (`scripts/verify-author-delete-isolation.py` + `tests/delete-isolation.sh`).
- Terminal-outcomes proof (`scripts/verify-author-terminal-outcomes.py` + `tests/terminal-outcomes.sh`) for delete + integrate-readiness + spin-off-readiness per #160.
- sai-verify `prototype-plugins.md` maps Author surface and proof recipes.
- Author README documents Foundry terminal outcomes with mechanical proof commands.

## `/goal` evidence @ HEAD (update each push)

### Author tree

| Path | Role |
|------|------|
| `Package.swift` | macOS 14 + iOS 17; `SaiAuthorMac` + `SaiAuthorIOS` executables |
| `Sources/SaiAuthor/AuthorRootView.swift` | Tab shell (Editor + Settings placeholders) |
| `Sources/SaiAuthor/EditorPlaceholder.swift` | `SaiCanvas` + `SaiText` |
| `Sources/SaiAuthor/SettingsPlaceholder.swift` | `SaiCanvas` + `SaiText` |
| `SaiAuthorMac/SaiAuthorMacApp.swift` | macOS `@main` |
| `SaiAuthorIOS/SaiAuthorIOSApp.swift` | iOS `@main` |
| `tests/delete-isolation.sh` | In-tree delete proof |
| `tests/terminal-outcomes.sh` | In-tree terminal-outcomes proof |

### Terminal outcomes (#160)

1. **Delete:** `scripts/verify-author-delete-isolation.py` — production grep clean; design-check + sai-verify pass with Author removed.
2. **Integrate-readiness:** `verify-author-terminal-outcomes.py` — Swift imports limited to `SaiDesignLanguage`/`SwiftUI`; no production app product deps in `Package.swift`.
3. **Spin-off-readiness:** same script — no `../../Sai` refs, no symlinks, relative SaiKit path, sources self-contained.

### Exact-HEAD CI

Re-bind after each push. Prior green @ `eed4dbf`:
- icm-enforcement: https://github.com/Dezocode/Sai/actions/runs/33199748465
- Sai Design Language: https://github.com/Dezocode/Sai/actions/runs/33199748544
- Anti-regression: https://github.com/Dezocode/Sai/actions/runs/33199748022

## Verify

- `python3 scripts/verify-author-terminal-outcomes.py`
- `scripts/verify-author-delete-isolation.py`
- `swift build --package-path prototypes/plugins/author`

## Next

- Await exact-HEAD CI on new push.
- Saul Product Quality (Origin/Hostinger; not agent-owned).
- Stay draft until owner merge approval.
