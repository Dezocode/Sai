# Foundry owner UX
Human owner workflow for prototype graduation: Integrate into Sai, Spin Off as App, and Delete / Archive — dry-run first, explicit confirmation, no UI policy authority.
## Sub-features
- `foundry-owner-shell` `prototypes/plugins/foundry/owner-ux/*` SwiftUI owner surface composing SaiDesignLanguage primitives only.
- `foundry-dry-run-first` dry-run plan before any effectful Integrate / Spin Off / Archive execution.
- `foundry-engine-stub` `FoundryGraduationEngine` protocol + `FoundryGraduationEngineStub` for tests only.
- `foundry-engine-bridge` `FoundryEngineBridge` invokes `go run ./prototypes/plugins/foundry/graduation-engine/cmd/graduate` from #164; falls back to stub when engine absent.
- `foundry-plan-template` `FoundryPlanTemplate` builds engine-compatible plan JSON mapped to UI `FoundryPlan` for any `prototypes/plugins/*` path.
- `foundry-manifest-loader` `FoundryPrototypeManifest` reads `prototype.manifest.json` graduation flags per plugin.
- `foundry-harness-fixture` `FoundryHarnessFixture` wires owner model/view for harness dry-run + confirm paths.
- `foundry-roadmap` `docs/roadmap/foundry/*` PR contracts and acceptance checklists for owner UX slices.
## How to get to it (user POV)
- Read `docs/roadmap/foundry/10-owner-ux-v1.md` and open `prototypes/plugins/foundry/owner-ux/` for the owner shell.
- Use `FoundryHarnessFixture.makeOwnerView(prototypePath:head:)` for any canonical plugin path.
## Driving it with verify-sai
- **Design lane.** ::gotest ./cmd/sai-design-check/...
- **Roadmap contract.** ::exists docs/roadmap/foundry/10-owner-ux-v1.md
- **Prototype manifest.** ::exists prototypes/plugins/foundry/owner-ux/prototype.manifest.json prototypes/plugins/foundry/owner-ux/Package.swift
## Gotchas
- Production `featureUIAllowed=false` remains global; prototype lane exemption is verifier-owned (see `prototype-plugins` feature map) and fail-closed. Owner UI uses `SaiCanvas`/`SaiText` only; no raw visual literals in `Sources/`.
- Graduation engine (#164) is CLI-only; owner UX consumes it via `FoundryEngineBridge`, never reimplements the engine.
- UNKNOWN disposition strings fail closed in `FoundryPlanTemplate.uiPlan`.
- Graduation to production requires a normal PR; the owner UI cannot direct-push `main`, auto-merge, or self-approve. Telemetry from Harness/#141 is display-only, not policy authority.
- Prototype promotion is PR-only; file moves alone do not graduate code to production roots.
