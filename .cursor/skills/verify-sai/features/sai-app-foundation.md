# Sai application foundation
Production app skeleton: native Apple clients, Go core, typed API, deployment boundary, and the Sai-specific design constitution.
## Sub-features
- `sai-app-architecture` `docs/architecture/SAI-APP-FOUNDATION.md` authority split, modular-monolith/density/performance/deployment contract.
- `sai-backend-core` `cmd/sai/main.go` + `internal/{app,README.md}` production Go boundary and future domain ownership.
- `sai-apple-native` `apps/apple/{README.md,SaiMac/,SaiIOS/,Config/,Packages/SaiKit/}` shared SwiftUI architecture.
- `sai-api-contract` `api/openapi.yaml` typed external client/server contract.
- `sai-design-language` `design/{SAI-DESIGN-LANGUAGE.md,sai-design-language.json,sai-design-language.schema.json}` + `cmd/sai-design-check/` + `.github/workflows/sai-design-language.yml`.
- `sai-deployment` `deploy/backend/README.md` + `migrations/README.md` reproducible deployment and migration boundaries.
## How to get to it (user POV)
- Start at `docs/architecture/SAI-APP-FOUNDATION.md`; Apple setup is `apps/apple/README.md`; design changes start at `design/SAI-DESIGN-LANGUAGE.md`.
## Driving it with verify-sai
- **Go skeleton.** ::exec go test ./cmd/sai/... ./internal/app/...
- **Design tests.** ::exec go test ./cmd/sai-design-check/...
- **Design contract.** ::exec go run ./cmd/sai-design-check
- **Contracts.** ::exists api/openapi.yaml design/sai-design-language.json apps/apple/Packages/SaiKit/Package.swift
## Gotchas
- `featureUIAllowed=false` intentionally blocks feature views until design approval. OpenClaw remains a prototype surface and is not the production app architecture. `sai-verify` remains a separate executable.
