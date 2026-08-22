# Sai application foundation

Status: **foundation skeleton**. Contract for the production Sai app before feature implementation. Optimize for modularity, performance, code density, explicit authority, testability, and replaceable infrastructure.

## Non-negotiables

1. **SwiftUI at the Apple edge; Go at the core.** Swift owns presentation and Apple APIs. Go owns authoritative product/domain behavior. Swift is not a second policy engine.
2. **One design language.** Feature code selects approved choices; it does not invent visual choices.
3. **One typed product contract.** `api/openapi.yaml` is the external API boundary. Mac and iPhone must not develop different backend semantics.
4. **Thin entrypoints.** `cmd/sai/main.go`, `SaiMacApp.swift`, and `SaiIOSApp.swift` assemble systems; they do not accumulate business logic.
5. **Standard library / platform primitives first.** Add dependencies when they remove more complexity than they introduce.
6. **Dense code, not compressed code.** One authoritative implementation reused by multiple interfaces, not duplicated wrappers or state machines.
7. **Measure before distributing.** Modular monolith first. Split services only with scaling, isolation, ownership, or deployment evidence.
8. **CI is architecture.** Rules that matter are executable checks.
9. **No product feature UI while draft.** `featureUIAllowed=false` locks product Views outside `SaiDesignLanguage` and the `SaiMac`/`SaiIOS` app entry files.
10. **`sai-verify` remains independent.** Product code may be verified by it but must not share its entrypoint or become a runtime dependency.

## Topology

macOS/iPhone/iPad SwiftUI clients talk to `cmd/sai` through `SaiAPI`. Apple-only APIs stay thin adapters. `apps/apple/` holds shells, xcconfig, and `Packages/SaiKit` (`SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`, `SaiFeatures`). `cmd/sai-design-check` is design CI. Future domains live under `internal/`. Contracts: `api/openapi.yaml`, `design/`, `migrations/`, `deploy/backend/`.

Go: one root module; `cmd/*` composes; domain under `internal/`; `transport/API -> domain/service -> persistence/integration ports`; context crosses blocking boundaries; goroutine ownership is explicit. No hidden goroutines, unbounded queues, DI framework, or speculative microservices. Apple: tokens only in `SaiDesignLanguage`; views render state; no network or policy on the render path. Development talks to `127.0.0.1:8080` `/health` `/ready`. Staging/Production inject endpoints. Secrets and signing stay out of Git. Xcode project files are not hand-authored here.

`cmd/sai-design-check` owns enforcement roots. Candidate JSON cannot widen the exempt tree, relocate the feature lock, or skip JSON-to-Swift bind. Missing `SaiDesignLanguage.swift` fails closed. Token values are provisional, not final aesthetic approval.
