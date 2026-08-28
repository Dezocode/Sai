# Sai prototype plugin lane

Status: **merged enabling contract**. PR #75 established the architectural permission and authority boundaries for a non-shipping prototype-plugin lane; PR #136 subsequently made those boundaries mechanical on `main`.

## Goal

Monaecode must be able to build real SwiftUI product prototypes under one canonical non-shipping root while production Sai remains protected. The canonical verifier-owned path is `prototypes/plugins/<plugin>/`. Sai Author is the first intended reference prototype.

## Prototype design rule

Design discovery is intentionally free inside a canonical prototype plugin. Prototype code may use arbitrary SwiftUI composition, visual values, layout, typography, interaction, motion, and plugin-local experimental primitives without satisfying production Sai Design Language literal/component restrictions.

`SaiDesignLanguage` is **optional preferred reuse when useful**, not prototype compliance and not a prerequisite for exploration. `PrototypeDesign/` may be used as an organizational convention but is not an exemption, security, or authority boundary.

Prototype-local design is discovery evidence only. It does not become production design authority merely because it exists.

## Authority and isolation boundaries

1. Production `SaiDesignLanguage`, `SaiFeatures`, `SaiMac`, and `SaiIOS` authority remains intact; `featureUIAllowed=false` is not globally widened for prototypes.
2. The canonical prototype root is verifier-owned and fail-closed. Candidate JSON, plugin metadata, symlinks, traversal, normalization, near-prefix names, or alternate roots cannot widen the exemption.
3. Production Swift, Go, package manifests, module/workspace graphs, and shipping targets must never depend on `prototypes/**`.
4. Prototypes may reuse stable Sai capabilities, including production Swift libraries and mechanically visible stable Go packages, but prototype-scoped work may not modify protected production Go merely for convenience. Genuine production capability gaps require separate production-authority work.
5. Go/OpenAPI remain authoritative for production domain/backend behavior. Prototype mocks/helpers cannot become a second production authority.
6. `sai-verify` owns prototype mapping/completeness; no parallel prototype verifier or candidate-selected authority is introduced.

## Graduation rule

Prototype code or design never graduates by folder/file move alone. During Integrate, surviving behavior is explicitly reconciled as **REUSE**, **PROMOTE**, feature-local production composition, or **DROP**, then enters production through a normal production PR and production verification.

## Successor product work

The next product-facing layer is the smallest runnable/buildable Sai Author reference prototype under `prototypes/plugins/author/`, proving macOS and iOS/iPadOS builds and deletion isolation. Full editor workflows, persistence, collaboration, marketplace/downloadable-code runtime, final plugin platform, graduation execution, and Foundry UX remain separate follow-on work.
