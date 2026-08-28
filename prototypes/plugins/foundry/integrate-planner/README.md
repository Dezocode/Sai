# Foundry Integrate Planner (slice 79)

Read-only production promotion planner for the SAI Prototype Foundry.

## Scope

- **PRD slice:** 79 (`foundry/integrate-planner`)
- **Consumes:** `foundry.graph.v1` dependency graphs from slice 78 (lifecycle graph)
- **Produces:** `foundry.integrate.plan.v1` deterministic integrate plans
- **Does not:** mutate production, create branches, or execute promotion

## Classifications

| Classification | Integrate action |
|---|---|
| `REUSE` | Reference existing production capability |
| `PROMOTE` | Propose specific production path under `apps/SaiFeatures/`, `design/`, `internal/`, or `api/` |
| `EXPORT` | Blocker — wrong graduation path for integrate |
| `REMOTE` | Document remote boundary |
| `PROMOTE_SHARED` | Blocker until shared capability exists |
| `DROP` | No integration action |
| `UNKNOWN` | Blocker — `ready=false` |

Folder-move graduation (`prototypes/plugins/<id>` root) is never recommended.

Cross-lane `prototypes/plugins/<other>` dependencies via `REUSE` or `PROMOTE` edges are forbidden.

`prototype-only` or `private` module visibility on `PROMOTE` nodes blocks integrate.

## CLI

```bash
go run ./prototypes/plugins/foundry/integrate-planner/cmd/foundry-integrate-plan \
  --graph fixtures/harness_golden.graph.json \
  --head 1111111111111111111111111111111111111111
```

Optional `--out plan.json` writes the plan for test harnesses. Exit code 3 when `ready=false`.

## Tests

```bash
go test ./prototypes/plugins/foundry/integrate-planner/...
```

Golden fixtures cover Sai Harness and Sai Author. Negative fixtures cover `UNKNOWN`, stale HEAD, production path conflicts, forbidden prototype dependencies, unresolved design authority, folder-move graduation, unsupported module visibility, `EXPORT`, `PROMOTE_SHARED`, and cross-lane `REUSE` paths.

## Roadmap

See `docs/roadmap/foundry/07-integrate-planner-v1.md`.
