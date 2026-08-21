# Sai application foundation

Status: **foundation skeleton**. This is the architectural contract for building the production Sai app. It establishes boundaries before feature implementation so agents compose a coherent product instead of inventing architecture or design per task.

## Non-negotiable objectives

Sai must scale in users, devices, features, contributors, and agent-driven development without scaling accidental complexity at the same rate. Optimize for **modularity, performance, code density, explicit authority, testability, and replaceable infrastructure**.

1. **SwiftUI at the Apple edge; Go at the core.** Swift owns presentation and Apple APIs. Go owns authoritative product/domain behavior.
2. **One design language.** Feature code selects approved design choices; it does not create new visual choices.
3. **One typed product contract.** `api/openapi.yaml` is the external API boundary; Mac and iPhone must not develop different backend semantics.
4. **Thin entrypoints.** `cmd/sai/main.go`, `SaiMacApp.swift`, and `SaiIOSApp.swift` assemble systems; they do not accumulate business logic.
5. **Standard library / platform primitives first.** Add dependencies when they remove more complexity than they introduce.
6. **Dense code, not compressed code.** Prefer one authoritative implementation reused by multiple interfaces over duplicated wrappers, policies, or state machines.
7. **Measure before distributing.** Start as a modular monolith. Split services only when scaling, isolation, ownership, or deployment evidence justifies it.
8. **CI is architecture.** Rules that matter must become executable checks rather than prose agents can forget.
9. **No product feature UI while the design contract is draft.** `design/sai-design-language.json` starts with `featureUIAllowed=false`; design work comes first.
10. **`sai-verify` remains independent.** Product code may be verified by it but must not share its entrypoint or make verification a runtime dependency.

## System topology

macOS/iPhone/iPad SwiftUI clients talk to `cmd/sai` through `SaiAPI`. Swift may call Apple APIs (FamilyControls, ManagedSettings, DeviceActivity, NetworkExtension, Keychain, Push, StoreKit). It is not a second policy engine. Go decides policy; Swift translates it.

## Repository skeleton

`apps/apple/` holds `SaiMac`/`SaiIOS` shells, xcconfig, and `Packages/SaiKit` (`SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`, `SaiFeatures`). `cmd/sai` is the production Go binary; `cmd/sai-design-check` is the design CI verifier; `cmd/sai-verify` stays independent. `internal/app` is process lifecycle. Future domains stay under `internal/`. Contracts live in `api/openapi.yaml`, `design/`, `migrations/`, and `deploy/backend/`.

## Go architecture

Use the existing root Go module. Multiple `cmd/*` directories are separate binaries; they do not need separate modules.

`cmd/sai` should only load configuration, construct dependencies, start the application, handle shutdown, and report fatal startup errors. Domain behavior belongs under `internal/`.

Package direction: `transport/API -> domain/service -> persistence/integration ports`.

Do not place policy decisions in HTTP handlers, database code, or Swift clients. Avoid a framework-shaped architecture, dependency-injection framework, global mutable state, hidden goroutines, unbounded queues, and speculative microservices. Pass `context.Context` across blocking boundaries, make ownership of goroutines explicit, bound concurrency, return useful errors, and keep hot paths allocation-conscious.

Start as a modular monolith. A package may later become a service only when there is measured need for independent scale, fault isolation, security isolation, or release cadence.

## Apple architecture

The Apple clients are native SwiftUI. `SaiMac` and `SaiIOS` are thin executable targets over shared local Swift package modules.

- `SaiDesignLanguage`: the only authority for visual tokens, primitives, component states, adaptive behavior, and motion. Runtime values are mechanically compared to `design/sai-design-language.json` by `cmd/sai-design-check`.
- `SaiFoundation`: shared non-domain client infrastructure and environment configuration.
- `SaiAPI`: typed network models, request/response transport, streaming, and generated API surfaces when generation is introduced.
- `SaiFeatures`: screen/feature composition. It may choose approved components but must not define a competing design system or authoritative backend policy.
- Platform code inside executable targets is the escape hatch for AppKit/UIKit and Apple frameworks that cannot live portably in shared SwiftUI.

Prefer Swift concurrency and keep main-thread work bounded. Views render state; they should not perform network, persistence, or domain-policy work directly.

## Sai Design Language

The design language is Sai-specific, not a generic UI lint suite and not the OpenClaw prototype's design system. It is governed by:

- `design/sai-design-language.json` - machine authority. `cmd/sai-design-check` compares `SaiDesignLanguage.swift` runtime tokens (`featureUIAllowed`, canvas, textPrimary, spacingLg, title2) to this file.
- `design/sai-design-language.schema.json` - structural schema.
- `design/SAI-DESIGN-LANGUAGE.md` - human/agent contract.
- `cmd/sai-design-check` - deterministic verifier (schema, Swift/JSON bind, source policy, feature-UI lock).
- `.github/workflows/sai-design-language.yml` - **one GitHub check named `Sai Design Language`**.

Feature code must not guess arbitrary padding, colors, font sizes, radii, control heights, shadows, z-index, animation durations, or breakpoints. If a new visual requirement is legitimate, change the design contract/component first, verify it, then consume it.

The initial token values are **provisional design-work values**, not final aesthetic approval. CI therefore keeps `featureUIAllowed=false` until the design phase explicitly approves the language.

## CI model

One result named `Sai Design Language` covers contract/schema validation, JSON-to-Swift token bind, Swift source policy, forbidden literals, design-module boundary, feature-UI lock while draft, and shared Swift package compilation. Later visual fixtures belong behind this same check. Product validation stays conceptually separate (`Sai Go`, `Sai Apple`, `Sai Verify`, Saul).

## Coding schema

Go: one root module; `cmd/*` is composition; domain lives under `internal/`; standard library first; context crosses blocking boundaries; concurrency is bounded and owned; errors preserve cause; transport/domain/persistence stay distinct.

Swift: shared code in `SaiKit`; UI tokens only in `SaiDesignLanguage`; feature views compose approved primitives; Swift owns presentation and Apple adapters, not canonical policy; prefer value types and Swift concurrency.

API: `api/openapi.yaml` is the external contract. Prefer additive evolution. Streaming must define reconnect, stale-state, retry, and version-skew behavior.

## Persistence, performance, environments

Persistence is behind Go package boundaries. Schema changes are ordered migrations in `migrations/`. Keep credentials out of source.

Keep the Go core stateless where practical. Keep request paths bounded and cancellation-aware. Avoid network calls inside rendering. Paginate/stream large collections. Cache only with an explicit invalidation owner.

Apple configuration uses Development/Staging/Production xcconfig for public endpoints, never secrets. Development talks to localhost Go. The Go application exposes `/health` and `/ready`. Signing material stays outside Git.

## Testing, security, density

Test at the narrowest useful layer. Every bug fix should prefer a regression test that demonstrates the failure before the fix.

Server authorization is authoritative. Never trust a client to enforce parent/child authorization. Store secrets in Keychain on Apple and an external secret mechanism on servers.

A feature PR should add domain behavior in Go, OpenAPI when needed, typed client behavior in `SaiAPI`, and SwiftUI composition in `SaiFeatures`, reusing `SaiDesignLanguage`.

Do not optimize for minimum line count. Optimize for minimum independent semantic machinery.
