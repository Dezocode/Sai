# Prototype plugin lane

Verifier-owned non-shipping prototype-plugin lane and Foundry prototype tooling under the canonical root. Contract: `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md`.

## Sub-features

- `proto-canonical-root` `prototypes/plugins/*` exact verifier-owned prototype root.
- `proto-foundry-spinoff` `prototypes/plugins/foundry/spinoff-planner-exporter/*` slice 80 spin-off planner, materializer, and no-checkout tests.
- `proto-demo-widget` `prototypes/plugins/demo-widget/*` harness fixture graph for spin-off proof.
- `proto-spinoff-verify` `scripts/verify-foundry-spinoff.py` sai-verify proof driver for slice 80 unit tests.

## How to get to it (user POV)

- Read `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md`; place prototype code under `prototypes/plugins/<plugin>/`.

## Driving it with verify-sai

- **Spinoff tests.** ::py scripts/verify-foundry-spinoff.py
- **Design contract.** ::exec scripts/verify-semantic-hierarchy

## Gotchas

- The prototype root is verifier-owned via this map; do not relocate it. Spin-off output must not reference the source Sai checkout. GitHub repo publication stays owner-controlled and out of scope.
- Slice 80 consumes slice 78 graph JSON via pinned fixtures only (`fixtures/foundry-graph.v1.schema.json`); it does not ship a second graph engine.
