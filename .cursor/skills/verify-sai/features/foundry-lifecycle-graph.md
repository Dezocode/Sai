# Foundry lifecycle dependency graph
Prototype-only lifecycle manifest parser and deterministic dependency graph for Foundry slices 78–81. Manifest grants zero security authority; UNKNOWN classification fails closed.
## Sub-features
- `foundry-graph-package` `prototypes/plugins/foundry/lifecycle-dependency-graph/graph/*` ParseManifest, ParseDeps, Build, ValidateForPlanning, ValidateHeadBinding.
- `foundry-graph-fixture` `prototypes/plugins/foundry/lifecycle-dependency-graph/synthetic-fixture/*` in-lane manifest + deps golden inputs.
- `foundry-graph-contract` `docs/roadmap/foundry/06-lifecycle-dependency-graph.md` slice-78 contract and classification rules.
## How to get to it (user POV)
- Read `docs/roadmap/foundry/06-lifecycle-dependency-graph.md`, then `prototypes/plugins/foundry/lifecycle-dependency-graph/README.md`. Import the `graph` package only from other `prototypes/plugins/**` consumers — never from production `cmd/sai/**` or `internal/**`.
## Driving it with verify-sai
- **Graph tests.** ::gotest ./prototypes/plugins/foundry/lifecycle-dependency-graph/graph/...
- **Contract.** ::exists docs/roadmap/foundry/06-lifecycle-dependency-graph.md prototypes/plugins/foundry/lifecycle-dependency-graph/README.md
- **Fixture.** ::json prototypes/plugins/foundry/lifecycle-dependency-graph/synthetic-fixture/manifest.json
## Gotchas
- Classifications: REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP only; UNKNOWN fails closed. Output binds repo, base, 40-char head, schema_version, tool_version, graph_hash. Stale plans rejected when head or graph_hash mismatch. Manifest must not carry authority fields (`permissions`, `grants`, `roles`, `capabilities`). Production must not import this package.
