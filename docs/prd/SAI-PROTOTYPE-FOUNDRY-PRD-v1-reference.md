# Sai Prototype Foundry — PRD v1 implementation reference

Source artifact: **`Sai_Prototype_Foundry_PRD(1).pdf`**, 23 pages, Version 1.0, 22 Aug 2026. This repository document is the implementation-facing attachment used by the stacked Foundry PRs. It preserves the source PRD's requirements and terminology while acknowledging that repository PR numbers have moved since the PDF was authored. The original owner-provided PDF remains the source artifact; this file must not be used to silently weaken it.

## North-star

Every prototype must remain structurally capable of one of three terminal outcomes without architectural surgery:

1. **Delete / archive** — production remains unaffected.
2. **Integrate** — validated behavior is promoted through the correct production authorities and a normal production PR.
3. **Spin Off** — exact prototype source plus the allowed dependency closure is materialized into an independently buildable repository/application.

**Production Sai must never become dependent on prototype code.**

## Core authority invariants

- Canonical non-shipping prototype root is verifier-owned and exact: `prototypes/plugins/`.
- Production Swift, Go, package manifests, build graphs, deployment definitions and future shipping formats may not directly or transitively depend on `prototypes/**`.
- Prototype code may consume stable production Sai capabilities: `SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`, generated API types, OpenAPI-backed services, and mechanically allowed stable production Go packages/functions.
- Prototype work may not edit, fork, shadow or replace stable production Go behavior merely for prototype convenience. Genuine production changes use a separate production-authority PR.
- Prototype manifests are descriptive and never security authority. They cannot choose exemption roots, trusted dependency boundaries, design authority or verifier policy.
- Production remains buildable/testable with the prototype tree removed; deletion safety is a standing invariant.
- Integrate and Spin Off are plan-first and fail closed on unresolved dependency classifications.
- `sai-verify` remains the prototype mapping/completeness authority. There is no parallel prototype verifier.
- Every pushed commit creates a new exact-head review boundary. Authority-changing transitions remain exact-head, fail-closed, reviewable, auditable and owner-controlled.

## Design-language inheritance

Prototype UI should look and behave like a future Sai feature unless discovery proves otherwise. Existing Sai Design Language tokens/components/roles/adaptive rules/accessibility/motion/control states are the default dependency.

`PrototypeDesign/` is a narrow plugin-local discovery escape hatch only:

- ordinary prototype code remains subject to governed visual-value policy;
- `PrototypeDesign` is not production authority;
- shipping Sai targets may not import it;
- surviving primitives graduate deliberately through normal production design review;
- near-prefix, relocated, symlinked or candidate-selected paths do not gain authority.

## Go / OpenAPI model

- Prototype Go may reuse stable exported production Go when package visibility permits.
- Production Go never depends on prototype Go.
- Prototype SwiftUI should normally reach authoritative product/domain behavior through SaiAPI/OpenAPI rather than inventing a second domain model.
- Prototype-only helpers may exist in the lane but cannot enter production binary/module graphs.
- If a prototype discovers a genuine production capability gap, record it and open a separate production-authority PR; then reuse the merged stable capability.

## Lifecycle states

`DRAFT -> VALIDATED -> INTEGRATION_PLANNED | SPINOFF_PLANNED -> GRADUATING -> INTEGRATED | SPUN_OFF`, with `ARCHIVED` and `DELETED` terminal maintenance outcomes.

No lifecycle state itself grants production authority.

## Graduation classifications

- **REUSE** — stable Sai capability consumed as-is.
- **PROMOTE** — prototype-owned behavior/design that should become production Sai authority through a reviewed production change.
- **EXPORT** — prototype-owned or explicitly portable source materialized into standalone output.
- **REMOTE** — capability remains owned by Sai and is consumed through a typed API/service boundary.
- **PROMOTE_SHARED** — block until a needed production capability is deliberately moved into a portable shared authority.
- **DROP** — exclude obsolete/experimental functionality.

Unresolved/UNKNOWN classifications block planning/execution.

## Dependency graph and provenance

The Foundry must deterministically enumerate and classify prototype-owned and consumed dependencies, including:

- Swift package/target dependencies, local source paths, resources and generated-code inputs;
- prototype Go imports/modules and reachable production packages;
- OpenAPI/schema/generated client dependencies and runtime service boundaries;
- SaiDesignLanguage and PrototypeDesign dependencies;
- external tools/runtimes/services needed to build or run the prototype.

Graph/plan artifacts bind to repository, base, **exact prototype HEAD**, schema/tool version and canonical graph hash. Stale plans fail.

## Integrate

Integrate is controlled promotion, not folder movement. A read-only planner first classifies every artifact and emits deterministic machine + human plans. It identifies production Swift/package changes, design promotion, Go/domain authority changes, API changes, REUSE/REMOTE dependencies and blockers. The eventual executor creates a normal production branch/PR; it never pushes directly to `main`, auto-marks ready or bypasses production gates.

## Spin Off

Spin Off freezes an exact prototype snapshot, computes the complete transitive closure and assigns an export strategy to every node. Output contains only the prototype and required allowed dependencies, with deterministic path/import rewrites and provenance.

Standalone proof requires:

- no path back to the source Sai checkout;
- all dependencies materialized, shared, remote or otherwise declared;
- required native app/backend targets build independently;
- any REMOTE Sai service boundary is explicit;
- `PROVENANCE` records source Sai commit, prototype commit, exported files, transformations and dependency dispositions.

GitHub repository publication, signing, TestFlight/App Store and notarization remain separate owner-authorized boundaries if needed.

## Graduation engine

The engine executes only a previously validated plan bound to the exact prototype HEAD. It is transactional, idempotent, auditable and owner-controlled. Candidate prototype code cannot alter executor policy or gain repository-creation/merge authority. Partial failure must leave a well-defined recoverable state.

## Foundry UX

Human-facing controls expose **Integrate into Sai**, **Spin Off as App**, and **Delete / Archive**. First click is dry-run/preview. The UI explains dependency dispositions/blockers, shows proposed diffs/standalone trees, requires explicit confirmation for authority-changing execution, exposes exact source HEAD + plan + verification evidence, and never fabricates completion.

## Verification / adversarial baseline

At minimum preserve/prove:

- production SwiftUI outside authority fails;
- SwiftUI inside canonical prototype plugin passes;
- near-prefix/traversal/symlink/candidate-root spoofing fails;
- ordinary prototype governed visual literals fail while SaiDesignLanguage reuse passes;
- canonical plugin-local `PrototypeDesign` experiments pass while out-of-lane variants fail;
- production Apple/Go -> prototype dependency fails;
- prototype Go -> approved stable production Go passes;
- prototype-driven protected production Go edits fail;
- production builds/tests remain valid without prototype dependencies;
- prototype surfaces are mapped/proved by `sai-verify`; broken/unmapped surfaces fail;
- existing Sai Design Language CI covers prototype changes;
- stale integration/spin-off plans fail;
- standalone output cannot reference the source checkout;
- generated production integration cannot retain `prototypes/**` back-dependencies;
- deletion fails if a production dependency exists.

## Performance / modularity constraints

- Reuse existing `cmd/sai-design-check` and `cmd/sai-verify`; do not create a third policy engine.
- Checks remain bounded/linear over relevant files + dependency edges.
- No production runtime dependency exists solely to support Foundry/prototype tooling.
- Prototype-only dependencies do not inflate production binary/module graphs.
- Core plan generation does **not require network access**; GitHub publication is a separate explicit action.
- Fixed source SHA + tool version produces deterministic graph/plan output.
- Prefer Sai's existing modular boundaries; do not prematurely create generic plugin marketplaces/runtimes/microservices.
- Each PR has one legible authority mission and respects repository governance/line-budget constraints.

## Success definition

The Foundry is mechanically established when the lane, real reference prototypes, lifecycle/dependency graph, read-only Integrate and Spin Off planners/exporter, and plan-bound graduation engine all exist with end-to-end proofs. Human-facing Foundry UX comes after the trusted mechanics.

Success metrics include zero production back-dependency edges, complete prototype mapping, deletion safety, complete artifact classification, independent spin-off builds, reproducible plans, owner-controlled authority changes, and exact-head review quality.

## Current-repository implementation overlay

The original PRD used then-future PR numbers and Sai Author as its first reference fixture. Current repository reality adds two already-active systems that the implementation sequence must incorporate without changing the north-star:

- **PR #141**: repo-owned sessions/runtime infrastructure — runtime registry, heartbeats, GitHub reconciliation, exact-head binding, verifier-owned flight-board publication. This is operational/observability infrastructure and may be a `REMOTE`/`REUSE` dependency; it is not a second Foundry verifier or product-domain authority.
- **PR #146**: prototype Crosscom/Sai Harness work — persistent Atomic/Grokbot execution, `.sai` hook model, channel topology, Crosscom skill, inbox/outbox and owner observation. These capabilities should converge into a canonical **Sai Harness prototype** rather than leak into production authority.

The stacked roadmap beginning with `roadmap/foundry-v1-1-sai-harness` treats **Sai Harness as the first systems reference prototype** and retains **Sai Author as the native product reference prototype** before the generic planners/executor are considered proven.
