# Handoff: Foundry slice 78 lifecycle dependency graph

Implemented prototype-scoped lifecycle manifest parser and deterministic dependency graph under `prototypes/plugins/foundry/lifecycle-dependency-graph/`.

## Delivered

- verify-sai map for `prototypes/plugins/foundry/*` and contract doc
- `graph` package with ParseManifest, ParseDeps, Build, ValidateForPlanning, ValidateHeadBinding, ValidateGraphHashBinding
- synthetic fixture + golden/adversarial tests
- sai-verify `pathRe` extended for `prototypes/`

## Verification

- `go test ./prototypes/plugins/foundry/lifecycle-dependency-graph/graph/...`
- `go test ./cmd/sai-verify/...`

Draft PR targets `main`; references #160 slice 78.
