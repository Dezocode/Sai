# Handoff — spinoff planner exporter

Restructured slice 80 under canonical path
`prototypes/plugins/foundry/spinoff-planner-exporter/`.

- Removed second root `prototypes/plugins/foundry-spinoff/`
- Removed slice 78 graph package `prototypes/plugins/foundry/graph/` (slice 78 ownership)
- Added `spinoff/graph_input.py` consumer for fixture-shaped slice 78 JSON
- Pinned schema fixture at `fixtures/foundry-graph.v1.schema.json`
- CLI: `prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff`
- Fixed icm-enforcement: aligned `prototype_map_test.go` with slice-80 map paths; added `scripts/verify-foundry-spinoff.py` for valid sai-verify `::py` proof recipe

Verification command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  prototypes/plugins/foundry/spinoff-planner-exporter/tests/test_spinoff.py
```

Or via sai-verify driver:

```bash
python3 scripts/verify-foundry-spinoff.py
```
