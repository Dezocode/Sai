# Foundry read-only Integrate planner
Prototype-only read-only integrate planner for Foundry slice 79. Consumes `foundry.graph.v1` and emits deterministic `foundry.integrate.plan.v1` without production mutation. UNKNOWN classification fails closed.
## Sub-features
- `foundry-integrate-package` `prototypes/plugins/foundry/integrate-planner/*` ParseGraph, ValidateGraph, Plan, golden and negative fixtures.
- `foundry-integrate-cli` `prototypes/plugins/foundry/integrate-planner/cmd/foundry-integrate-plan/*` offline CLI `--graph` `--head` optional `--out`.
- `foundry-integrate-contract` `docs/roadmap/foundry/07-integrate-planner-v1.md` slice-79 contract and classification rules.
## How to get to it (user POV)
- Read `docs/roadmap/foundry/07-integrate-planner-v1.md`, then `prototypes/plugins/foundry/integrate-planner/README.md`. Import only from other `prototypes/plugins/**` consumers, never from production `cmd/sai/**` or `internal/**`.
## Driving it with verify-sai
- **Kernel tests.** ::gotest ./cmd/sai-verify/...
- **Planner package.** ::exists prototypes/plugins/foundry/integrate-planner/planner_test.go prototypes/plugins/foundry/integrate-planner/README.md
- **Contract.** ::exists docs/roadmap/foundry/07-integrate-planner-v1.md
- **Golden plan.** ::json prototypes/plugins/foundry/integrate-planner/fixtures/harness_golden.plan.json
## Gotchas
- Classifications: REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP; UNKNOWN blocks `ready`. Never folder-move graduation. Graph must bind exact 40-char HEAD and `graph_hash`. Read-only: no production writes, branches, or GitHub mutations.
