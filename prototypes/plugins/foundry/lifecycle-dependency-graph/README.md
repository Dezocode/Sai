# Foundry lifecycle dependency graph (slice 78)

Prototype-scoped manifest + deterministic dependency graph for Sai Foundry.

- `graph/` — Go package: `ParseManifest`, `ParseDeps`, `Build`, canonical `graph_hash`.
- `synthetic-fixture/` — offline fixture with all six classifications.

Run tests:

```bash
go test ./prototypes/plugins/foundry/lifecycle-dependency-graph/graph/...
```

Production code must not import this package.
