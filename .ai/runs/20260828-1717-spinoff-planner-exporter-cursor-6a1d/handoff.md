# Handoff — spinoff planner exporter

Restructured slice 80 under canonical path
`prototypes/plugins/foundry/spinoff-planner-exporter/`.

- Removed second root `prototypes/plugins/foundry-spinoff/`
- Removed slice 78 graph package `prototypes/plugins/foundry/graph/` (slice 78 ownership)
- Added `spinoff/graph_input.py` consumer for fixture-shaped slice 78 JSON
- Added slice 78 Output consumer (`provenance`/`manifest_id`/`nodes`/`edges`/`graph_hash`) alongside legacy fixture shape
- Pinned schema fixtures at `fixtures/foundry-graph.v1.schema.json` and `fixtures/foundry-graph-output.v1.schema.json`
- Pinned demo Output fixture at `prototypes/plugins/demo-widget/foundry.graph.output.json`
- CLI: `prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff` (mode 100755)
- Fixed icm-enforcement: aligned `prototype_map_test.go`, added `scripts/verify-foundry-spinoff`, fixed `test_spinoff.py` REPO_ROOT (`parents[5]`)
- Saul fix: bash verify driver (no new `.py` under `scripts/` for compileall); CLI executable bit

Verification command:

```bash
scripts/verify-foundry-spinoff
```
