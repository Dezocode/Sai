# Sai Author reference shell

Non-shipping prototype plugin for slice 77 (issue #160). macOS and iOS/iPadOS
placeholders compose production `SaiDesignLanguage` only. Deleting this tree
must not break production Sai.

See `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` for the canonical lane
contract. Production `apps/apple` targets are unchanged. This package depends on
SaiKit via a relative path and is not referenced from production manifests.

## Terminal outcomes (#160)

Every prototype under `prototypes/plugins/` must support delete, integrate, or
spin-off without architectural surgery. Author is a reference shell that proves
the lane pattern mechanically:

| Outcome | Mechanical proof (this slice) |
|---------|-------------------------------|
| **Delete/archive** | `scripts/verify-author-delete-isolation.py` or `tests/delete-isolation.sh`. Production design-check and sai-verify stay green after Author removal. |
| **Integrate** | `scripts/verify-author-terminal-outcomes.py` proves Author imports only `SaiDesignLanguage` + SwiftUI and `Package.swift` lists no production app products. Graduation is plan-first (slice 79), never a folder move. |
| **Spin-off** | Same script proves no `../../Sai` checkout refs, no symlinks, relative SaiKit path only, all sources self-contained under this tree. Full export is slice 80. |

Run the combined proof:

```bash
python3 scripts/verify-author-terminal-outcomes.py
# or in-tree:
./prototypes/plugins/author/tests/terminal-outcomes.sh
```

## Build

```bash
swift build --package-path prototypes/plugins/author
(cd prototypes/plugins/author && xcodebuild -scheme SaiAuthorIOS -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO)
```

## Layout

| Path | Role |
|------|------|
| `Package.swift` | macOS 14 + iOS 17; `SaiAuthorMac` + `SaiAuthorIOS` executables |
| `Sources/SaiAuthor/` | Shared `AuthorRootView` + Editor/Settings placeholders (`SaiCanvas`, `SaiText`) |
| `SaiAuthorMac/`, `SaiAuthorIOS/` | Platform `@main` entry points |
| `tests/delete-isolation.sh` | In-tree adversarial delete proof |
| `tests/terminal-outcomes.sh` | In-tree delete + integrate + spin-off readiness proof |
