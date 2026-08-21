# Sai Apple

Native SwiftUI clients for macOS, iPhone, and iPad.

`apps/apple/Package.swift` is the SwiftPM graph for executable targets `SaiMac` and `SaiIOS`. They compose `SaiCanvas`/`SaiText` and silently ping `health`/`ready`. No feature UI. Xcode project and signing files are not hand-authored here. Build with `swift build --package-path apps/apple/Packages/SaiKit` then `swift build --package-path apps/apple`.

Shared `Packages/SaiKit` modules:

- `SaiDesignLanguage` — visual authority (`featureUIAllowed=false`).
- `SaiFoundation` — `SaiConfiguration` from `SAI_ENVIRONMENT` / `SAI_API_BASE_URL` (env, then Info.plist).
- `SaiAPI` — GET probes expecting 204.
- `SaiFeatures` — empty namespace until design unlocks feature UI.

Apple-only frameworks stay in thin platform adapters near the executable target when they cannot be shared.

## Environments

`Config/*.xcconfig` defines public environment configuration only:

- Development -> `http://127.0.0.1:8080` (`INFOPLIST_KEY_SAI_*`)
- Staging/Production -> environment key only; API URL is supplied by release config

Never place credentials in xcconfig or Git.

## Delivery

macOS: test -> archive -> sign -> notarize/staple for direct distribution or submit through App Store Connect.
iOS/iPadOS: test -> archive -> App Store Connect -> TestFlight -> App Store.

Before feature UI begins, the Sai Design Language must leave `foundation-draft` and set `featureUIAllowed=true`.
