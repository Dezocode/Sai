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

Slice 78 `foundry.graph.output.json` shape is also accepted (see
`prototypes/plugins/demo-widget/foundry.graph.output.json`).

## Acceptance (slice 80)

| Criterion | Evidence |
|-----------|----------|
| Canonical root `prototypes/plugins/` only | Product path is `prototypes/plugins/foundry/spinoff-planner-exporter/`; `foundry-spinoff/` absent from branch |
| Consumes slice 78 graph; no graph engine fork | `spinoff/graph_input.py` reads fixture-shaped graphs; pinned schemas under `fixtures/` |
| Read-only export plan; no folder-move graduation | `planner.py` builds plans; `materializer.py` copies to candidate tree; no git push or main writes |
| Independent tree; no Sai checkout refs | `audit.py` + `test_no_forbidden_refs` + `test_cli_plan_and_materialize` |
| UNKNOWN/PROMOTE fail closed | `test_unknown_blocks`, `test_promote_blocks` |

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  prototypes/plugins/foundry/spinoff-planner-exporter/tests/test_spinoff.py
```

Or via sai-verify proof driver:

```bash
python3 scripts/verify-foundry-spinoff.py
```
