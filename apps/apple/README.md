# Sai Apple

Native SwiftUI clients for macOS, iPhone, and iPad.

`SaiMac/` and `SaiIOS/` are executable shells. They compose `SaiCanvas`/`SaiText` from `SaiDesignLanguage` and silently ping `health`/`ready` via `SaiHTTPClient`. No feature UI.

Shared implementation lives in the local `Packages/SaiKit` package:

- `SaiDesignLanguage` — all visual and adaptive decisions (`featureUIAllowed=false`).
- `SaiFoundation` — `SaiConfiguration` from `SAI_ENVIRONMENT` / `SAI_API_BASE_URL` (env, then Info.plist).
- `SaiAPI` — GET probes expecting 204.
- `SaiFeatures` — empty namespace until design unlocks feature UI.

Apple-only frameworks stay in thin platform adapters near the executable target when they cannot be shared.

The intended Xcode workspace/project should reference these sources rather than duplicate them. Project-file generation is deliberately not hand-authored in this skeleton.

## Environments

`Config/*.xcconfig` defines public environment configuration only:

- Development -> `http://127.0.0.1:8080` (`INFOPLIST_KEY_SAI_*`)
- Staging/Production -> environment key only; API URL is supplied by release config

Never place credentials in xcconfig or Git.

## Delivery

macOS: test -> archive -> sign -> notarize/staple for direct distribution or submit through App Store Connect.
iOS/iPadOS: test -> archive -> App Store Connect -> TestFlight -> App Store.

Before feature UI begins, the Sai Design Language must leave `foundation-draft` and set `featureUIAllowed=true`.
