# Sai Apple

Native SwiftUI clients for macOS, iPhone, and iPad. `Package.swift` defines executables `SaiMac` and `SaiIOS`. They compose `SaiCanvas`/`SaiText` and silently ping `health`/`ready`. No feature UI. Xcode project and signing files are not hand-authored. `swift build --package-path apps/apple/Packages/SaiKit` then `swift build --package-path apps/apple`.

- `SaiDesignLanguage` — visual authority (`featureUIAllowed=false`; Dynamic Type via `@ScaledMetric`).
- `SaiFoundation` — `SaiConfiguration` from `SAI_ENVIRONMENT` / `SAI_API_BASE_URL`.
- `SaiAPI` — GET probes expecting 204.
- `SaiFeatures` — empty until design unlocks feature UI.

`Config/*.xcconfig`: Development → `http://127.0.0.1:8080`; Staging/Production inject the API URL. No credentials in Git.
