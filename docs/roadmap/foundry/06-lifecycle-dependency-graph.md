# Foundry lifecycle + dependency graph (slice 78)

Parent: [#160](https://github.com/Dezocode/Sai/issues/160)

## Acceptance

- Descriptive manifest (`schema_version` 1) with zero security authority; forbidden authority fields fail closed.
- Deterministic dependency graph from `deps.json` with classifications REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP.
- UNKNOWN or unclassified nodes/edges block planning (`ValidateForPlanning`).
- Canonical graph hash binds repo, base, 40-char HEAD, schema/tool version.
- Golden fixture proves deterministic output and adversarial cases (stale HEAD, UNKNOWN, reorder).

## Graph API (siblings 79–81)

- `ParseManifest`, `ParseDeps`, `Build`, `ValidateForPlanning`, `ValidateHeadBinding`, `ValidateGraphHashBinding`
- Output binds `repo`, `base`, 40-char `head`, `schema_version`, `tool_version`, `graph_hash`
- Production must not import `prototypes/plugins/foundry/lifecycle-dependency-graph/graph`

## Non-goals

- Integrate/spin-off planners, graduation engine, Author UI, or production imports of `prototypes/**`.
