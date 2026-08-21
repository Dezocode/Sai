# Sai Apple

Native SwiftUI clients for macOS, iPhone, and iPad.

`SaiMac/` and `SaiIOS/` are executable shells. Shared implementation lives in the local `Packages/SaiKit` package:

- `SaiDesignLanguage` — all visual and adaptive decisions.
- `SaiFoundation` — shared client infrastructure/environment.
- `SaiAPI` — typed API and streaming boundary to Go.
- `SaiFeatures` — feature/screen composition only.

Apple-only frameworks stay in thin platform adapters near the executable target when they cannot be shared. Examples include FamilyControls, ManagedSettings, DeviceActivity, NetworkExtension, Keychain, push registration, StoreKit, App Intents, and AppKit/UIKit escape hatches.

The intended Xcode workspace/project should reference these sources rather than duplicate them. Project-file generation is deliberately not hand-authored in this skeleton; create it in Xcode when signing identities, bundle identifiers, entitlements, minimum OS versions, and target capabilities are selected.

## Environments

`Config/*.xcconfig` defines public environment configuration only:

- Development -> local Go backend
- Staging -> staging Sai backend
- Production -> production Sai backend

Never place credentials in xcconfig or Git.

## Delivery

macOS: test -> archive -> sign -> notarize/staple for direct distribution or submit through App Store Connect.  
iOS/iPadOS: test -> archive -> App Store Connect -> TestFlight -> App Store.

Before feature UI begins, the Sai Design Language must leave `foundation-draft` and set `featureUIAllowed=true`.
