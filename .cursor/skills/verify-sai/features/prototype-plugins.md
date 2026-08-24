# Prototype plugin lane enforcement
Verifier-owned non-shipping prototype-plugin lane: canonical root, SwiftUI exemption, Sai-first design inheritance, one-way dependency isolation, and CI coverage. Contract: `docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md` (PR #76); parent contract `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` (PR #75).
## Sub-features
- `proto-canonical-root` `prototypes/plugins/*` exact verifier-owned prototype root; near-prefix/traversal/candidate relocation attempts fail closed in `cmd/sai-design-check`.
- `proto-swiftui-exemption` `prototypes/plugins/*` SwiftUI import permitted inside the canonical root only when `featureUIAllowed=false`; production lock unchanged elsewhere.
- `proto-design-experiment-scope` `prototypes/plugins/*/PrototypeDesign/*` plugin-local experimental visual values; raw literals outside this scope still fail.
- `proto-dependency-isolation` `cmd/sai-design-check/*` every production `Package.swift` (walk-discovered) and all production Go may not reference/import the prototype tree; prototype Go may reuse stable production packages but not modify protected production behavior.
- `proto-ci-trigger` `.github/workflows/sai-design-language.yml` prototype changes trigger the single Sai Design Language check.
## How to get to it (user POV)
- Read `docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md`; place future prototype code under `prototypes/plugins/<plugin>/`; experimental visuals go in that plugin's `PrototypeDesign/`.
## Driving it with verify-sai
- **Lane policy tests.** ::gotest ./cmd/sai-design-check/...
- **Whole kernel race.** ::gotest ./cmd/sai-verify/...
- **Design contract live.** ::exec scripts/verify-semantic-hierarchy
## Gotchas
- The prototype root is owned by verifier code, never by `design/sai-design-language.json`, plugin metadata, env vars, or build settings; candidate keys naming other roots are ignored and pinned `codePolicy` paths still fail closed. `prototypes/plugin/`, `prototypes/plugins-evil/`, `prototype/plugins/`, traversal, absolute forms, and symlink escape do not satisfy the canonical-root test. Nested `PrototypeDesign/` directories are allowed exactly like nested SaiDesignLanguage dirs. Manifest gate: walk-discovered `Package.swift` files (prototypes/.git/.build/.swiftpm pruned) fail on lane-resolving paths or non-literal values; unreadable trees fail closed. The verifier's own source mentioning prototype import paths is string data, not an import declaration, so it never self-triggers the gate.
