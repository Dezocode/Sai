# Sai prototype plugins
Non-shipping SwiftUI product prototypes under the canonical plugin lane. Production must never depend on prototype modules.
## Sub-features
- `proto-lane` `prototypes/plugins/*` canonical plugin root; sai-verify maps every file under this tree.
- `proto-author` `prototypes/plugins/author/*` Sai Author reference shell (slice 77); macOS and iOS placeholders using SaiDesignLanguage.
- `proto-author-isolation` `prototypes/plugins/author/tests/delete-isolation.sh` adversarial proof that deleting the Author tree cannot break production.
## How to get to it (user POV)
- Read `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md`. Build Author with `swift build --package-path prototypes/plugins/author`.
## Driving it with verify-sai
- **Author tree.** ::exists prototypes/plugins/author/Package.swift prototypes/plugins/author/Sources/SaiAuthor/AuthorRootView.swift
- **Isolation.** ::py scripts/verify-author-delete-isolation.py
- **Production lock.** ::contains apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/SaiDesignLanguage.swift featureUIAllowed = false
## Gotchas
- Deleting `prototypes/plugins/author/` must not break production Sai. Production manifests must not reference prototype paths. `prototypes/*` is verifier-mapped; unmapped prototype files fail sai-verify completeness.
