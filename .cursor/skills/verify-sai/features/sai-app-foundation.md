# Sai application foundation
Production app skeleton: native Apple clients, Go core, typed API, deployment boundary, and the Sai-specific design constitution.
## Sub-features
- `sai-app-architecture` `docs/architecture/*` authority split, modular-monolith/density/performance/deployment contract.
- `sai-backend-core` `cmd/sai/*` `internal/*` production Go boundary and future domain ownership.
- `sai-apple-native` `apps/apple/*` shared SwiftUI architecture.
- `sai-api-contract` `api/*` typed external client/server contract.
- `sai-design-language` `design/*` `cmd/sai-design-check/*` `.github/workflows/sai-design-language.yml`.
- `sai-deployment` `deploy/*` `migrations/*` reproducible deployment and migration boundaries.
## How to get to it (user POV)
- Start at `docs/architecture/SAI-APP-FOUNDATION.md`; Apple setup is `apps/apple/README.md`; design changes start at `design/SAI-DESIGN-LANGUAGE.md`.
## Driving it with verify-sai
- **Go core.** ::gotest ./cmd/sai/... ./internal/app/...
- **Design check.** ::gotest ./cmd/sai-design-check/...
- **Contracts.** ::exists api/openapi.yaml design/sai-design-language.json apps/apple/Packages/SaiKit/Package.swift
## Gotchas
- `featureUIAllowed=false` forbids import SwiftUI outside SaiDesignLanguage. Exact shells may only WindowGroup { SaiCanvas { SaiText } }. No global typealias ban. Enforcement paths are verifier-owned; missing SaiDesignLanguage.swift fails closed. OpenClaw is not the production app. `sai-verify` stays a separate executable. Product roots use `/*` globs. Proofs use `::gotest ./cmd/...`; `::exec go` is not an allowBin.
