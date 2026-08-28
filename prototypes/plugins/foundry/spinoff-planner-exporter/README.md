# Foundry spin-off planner and exporter

Slice 80 prototype tooling: deterministic spin-off planner and candidate
materializer. Consumes slice 78 Foundry graph JSON via pinned fixtures; does
not ship a graph engine.

## Usage

```bash
prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff plan \
  prototypes/plugins/demo-widget/foundry.graph.json

prototypes/plugins/foundry/spinoff-planner-exporter/bin/foundry-spinoff materialize \
  prototypes/plugins/demo-widget/foundry.graph.json /tmp/demo-widget-candidate
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  prototypes/plugins/foundry/spinoff-planner-exporter/tests/test_spinoff.py
```
