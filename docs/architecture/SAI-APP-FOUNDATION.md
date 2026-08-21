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

```text
macOS SwiftUI ─┐
iPhone SwiftUI ├── SaiAPI ── HTTPS/WebSocket ── cmd/sai (Go)
iPad SwiftUI  ─┘                              │
                                             ├─ domain packages
Apple-only adapters                           ├─ persistence
FamilyControls / ManagedSettings              ├─ integrations
DeviceActivity / NetworkExtension             └─ events/notifications
Keychain / Push / StoreKit
```

Swift is allowed to perform OS-specific actions. It is not allowed to become a second policy engine. Example: Go decides that a policy requires an app restriction; Swift translates that decision into `ManagedSettings`.

## Repository skeleton

```text
apps/apple/
  SaiMac/                         macOS executable shell
  SaiIOS/                         iOS/iPadOS executable shell
  Config/                         Development/Staging/Production xcconfig
  Packages/SaiKit/
    Sources/SaiDesignLanguage/    tokens, primitives, adaptive UI
    Sources/SaiFoundation/        shared client foundations
    Sources/SaiAPI/               typed transport/client boundary
    Sources/SaiFeatures/          product feature composition
cmd/
  sai/                            production Go executable
  sai-design-check/               design/code-schema CI verifier
  sai-verify/                     existing independent repo verifier
internal/
  app/                            process lifecycle/composition
  future domains: api, auth, family, policy, devices, activity,
                  notifications, persistence, integrations
api/openapi.yaml                  product API contract
design/                           Sai-specific design constitution
migrations/                       ordered datastore migrations
deploy/backend/                   backend deployment contract
```

## Go architecture

Use the existing root Go module. Multiple `cmd/*` directories are separate binaries; they do not need separate modules.

`cmd/sai` should only load configuration, construct dependencies, start the application, handle shutdown, and report fatal startup errors. Domain behavior belongs under `internal/`.

Package direction is intentionally simple:

```text
transport/API -> domain/service -> persistence/integration ports
```

Do not place policy decisions in HTTP handlers, database code, or Swift clients. Avoid a framework-shaped architecture, dependency-injection framework, global mutable state, hidden goroutines, unbounded queues, and speculative microservices. Pass `context.Context` across blocking boundaries, make ownership of goroutines explicit, bound concurrency, return useful errors, and keep hot paths allocation-conscious.

Start as a modular monolith because it is denser, faster to change, easier to test, and cheaper to deploy. A package may later become a service only when there is measured need for independent scale, fault isolation, security isolation, or release cadence.

## Apple architecture

The Apple clients are native SwiftUI. `SaiMac` and `SaiIOS` are thin executable targets over shared local Swift package modules.

- `SaiDesignLanguage`: the only authority for visual tokens, primitives, component states, adaptive behavior, and motion.
- `SaiFoundation`: shared non-domain client infrastructure and environment configuration.
- `SaiAPI`: typed network models, request/response transport, streaming, and generated API surfaces when generation is introduced.
- `SaiFeatures`: screen/feature composition. It may choose approved components but must not define a competing design system or authoritative backend policy.
- Platform code inside executable targets is the escape hatch for AppKit/UIKit and Apple frameworks that cannot live portably in shared SwiftUI.

Prefer Swift concurrency (`async/await`, actors where shared mutable state requires isolation) and keep main-thread work bounded. Views render state; they should not perform network, persistence, or domain-policy work directly.

## Sai Design Language

The design language is Sai-specific, not a generic UI lint suite and not the OpenClaw prototype's design system. It is governed by:

- `design/sai-design-language.json` — machine authority.
- `design/sai-design-language.schema.json` — structural schema.
- `design/SAI-DESIGN-LANGUAGE.md` — human/agent contract.
- `cmd/sai-design-check` — deterministic verifier.
- `.github/workflows/sai-design-language.yml` — **one GitHub check named `Sai Design Language`**.

The contract owns spacing, typography, colors, borders, radii, elevation, control geometry, component variants/states, navigation, screen adaptability, breakpoints/adaptive widths, touch targets, motion, reduced motion, accessibility, layering, data visualization, media treatment, and source-code styling rules.

Feature code must not guess arbitrary padding, colors, font sizes, radii, control heights, shadows, z-index, animation durations, or breakpoints. If a new visual requirement is legitimate, change the design contract/component first, verify it, then consume it.

The initial token values are **provisional design-work values**, not final aesthetic approval. CI therefore keeps `featureUIAllowed=false` until the design phase explicitly approves the language. This prevents skeleton work from silently becoming product design.

## CI model

The design suite intentionally reports one result:

```text
Sai Design Language
  contract/schema validation
  Swift source policy
  forbidden arbitrary visual literals
  design-module boundary
  feature-UI lock while design is draft
  shared Swift package compilation
```

A later visual-fixture phase belongs behind this same check: canonical component previews, fixed macOS/iPhone/iPad viewports, accessibility states, light/dark variants if supported, and screenshot regression. Do not create a forest of independently required design checks.

General product validation should remain conceptually separate: `Sai Go`, `Sai Apple`, `Sai Verify`, and independent Saul review. Design failures are design failures; backend failures are backend failures.

## Coding schema

### Go
- One root module; purpose-specific binaries under `cmd/`.
- `cmd/*` is composition only; reusable/domain behavior lives under `internal/`.
- Standard library first; dependencies need an explicit benefit.
- Context and cancellation cross blocking boundaries.
- Concurrency is bounded and owned; no orphan/background loops without lifecycle control.
- Errors preserve cause/context; panic is not normal control flow.
- Transport, domain, and persistence concerns do not collapse into one package.

### Swift
- Shared code lives in `SaiKit`; executable targets remain thin.
- UI design values and primitives live only in `SaiDesignLanguage`.
- Feature views compose approved primitives; they do not define local design systems.
- Swift owns presentation state and Apple adapters, not canonical parental policy or authorization.
- Prefer value types, protocol boundaries where substitution is real, Swift concurrency, and explicit actor ownership.
- Avoid singleton mutable state, hidden networking in views, and duplicated API models.

### API
- `api/openapi.yaml` is the external client/server contract.
- Prefer additive/backward-compatible evolution; breaking changes require explicit version/migration handling.
- Streaming/live state must define reconnect, stale-state, retry, and version-skew behavior.

## Persistence and migrations

Persistence is behind Go package boundaries. Schema changes are ordered, reviewable migrations in `migrations/`; application startup must not perform surprising destructive migration behavior. Keep credentials out of source and Apple configuration files.

## Performance and scalability

Performance is a feature, but architecture must be driven by measurements rather than ceremony.

- Keep the Go core stateless where practical so instances can scale horizontally.
- Keep request paths bounded and cancellation-aware.
- Avoid network calls inside rendering and avoid blocking SwiftUI's main actor.
- Paginate/stream large collections rather than loading unbounded histories.
- Batch/coalesce high-frequency activity where latency requirements permit.
- Establish benchmarks and SLOs when real workloads exist; do not invent meaningless thresholds before the product exists.
- Prefer compact data models and stable APIs over layers of translation objects.
- Cache only with an explicit invalidation owner.

## Environments and deployment

Apple configuration uses `Development.xcconfig`, `Staging.xcconfig`, and `Production.xcconfig`. They may contain public endpoint/configuration values, never secrets.

Development: SwiftUI client -> localhost Go server.  
Staging: signed test client -> staging API/database.  
Production: released client -> production API/database.

Backend delivery should be reproducible: test -> build immutable artifact -> migrate safely -> deploy staging -> health/readiness -> promote production. The Go application exposes `/health` for process health and `/ready` for dependency readiness.

macOS distribution may later use the Mac App Store or Developer ID distribution. Direct distribution requires signing, hardened runtime as applicable, notarization, stapling, and a release artifact. iOS/iPadOS ships through App Store Connect/TestFlight/App Store. Signing identities and provisioning material stay outside Git.

## Testing strategy

Test at the narrowest useful layer: Go unit/package tests for domain behavior; API contract/integration tests at transport boundaries; Swift package tests for client logic; SwiftUI/component snapshot and accessibility tests for design; a small number of end-to-end journeys for cross-system confidence.

Every bug fix should prefer a regression test that demonstrates the failure before the fix. Tests should attack authority boundaries and failure modes, not only happy paths.

## Security boundaries

Server authorization is authoritative. Never trust a client to enforce parent/child authorization, policy, subscription state, or audit integrity. Store device/user secrets in Keychain on Apple platforms and in an external secret mechanism on servers. Log identifiers and outcomes, not credentials or sensitive content by default. Least privilege applies to Apple entitlements, service credentials, database roles, and CI tokens.

## Feature implementation rule

A feature PR should normally add domain behavior in Go, contract changes in OpenAPI when needed, typed client behavior in `SaiAPI`, and SwiftUI composition in `SaiFeatures`. The feature should reuse `SaiDesignLanguage` rather than creating local design primitives.

When an agent encounters an architectural or visual choice not covered here, the correct action is to amend the appropriate contract first—not make a one-off choice inside the feature.

## Density rule

Do not optimize for minimum line count. Optimize for minimum **independent semantic machinery**. A slightly larger shared implementation is preferable to five smaller implementations that can drift. New abstractions must demonstrate repeated responsibility or a hard boundary; otherwise keep the code direct.
