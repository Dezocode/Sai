# Handoff — spinoff planner exporter

Restructured slice 80 under canonical path
`prototypes/plugins/foundry/spinoff-planner-exporter/`.

- Removed second root `prototypes/plugins/foundry-spinoff/`
- Removed slice 78 graph package `prototypes/plugins/foundry/graph/` (slice 78 ownership)
- Added `spinoff/graph_input.py` consumer for fixture-shaped slice 78 JSON
- Added slice 78 Output consumer (`provenance`/`manifest_id`/`nodes`/`edges`/`graph_hash`) alongside legacy fixture shape
- Pinned schema fixtures at `fixtures/foundry-graph.v1.schema.json` and `fixtures/foundry-graph-output.v1.schema.json`
- Pinned demo Output fixture at `prototypes/plugins/demo-widget/foundry.graph.output.json`
- CLI: `prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff`
- Fixed icm-enforcement: aligned `prototype_map_test.go`, added `scripts/verify-foundry-spinoff`, fixed `test_spinoff.py` REPO_ROOT (`parents[5]`)
- Acceptance hardening: CLI (`python -m spinoff`), PROMOTE blocker, PROVENANCE frozen-head tests; README acceptance table

## Saul P1 fixes (2026-08-28)

- Set `bin/foundry-spinoff` git mode **100755** (was 100644; Saul executable-bit check).
- Replaced `scripts/verify-foundry-spinoff.py` with bash `scripts/verify-foundry-spinoff` so `python3 -m compileall -q scripts` passes on read-only FS (no new `.py` under `scripts/`).
- Updated `prototype-plugins.md` proof recipe (`::exec`) and `prototype_map_test.go` path claim.

Verification command:

```bash
python3 -m compileall -q scripts
scripts/verify-foundry-spinoff
prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff plan
```
