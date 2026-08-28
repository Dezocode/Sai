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
the lane pattern:

| Outcome | How (this slice) |
|---------|------------------|
| **Delete/archive** | Remove this directory. Run `scripts/verify-author-delete-isolation.py` or `tests/delete-isolation.sh`. Production design-check and sai-verify must stay green. |
| **Integrate** | Not executed here. Slice 79 provides a read-only integrate planner; graduation never recommends a folder move. |
| **Spin-off** | Not executed here. Slice 80 exports an independent tree with no `../../Sai` checkout refs. |

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
