# Handoff — slice 78 PR #167 rewrite

Rewrote `foundry/lifecycle-dependency-graph` to independent slice 78 only:
`prototypes/plugins/foundry/lifecycle-dependency-graph/` (+483 lines).

Graph API: ParseManifest, ParseDeps, Build, ValidateForPlanning,
ValidateHeadBinding, ValidateGraphHashBinding. Classifications REUSE/PROMOTE/
EXPORT/REMOTE/PROMOTE_SHARED/DROP; UNKNOWN fail-closed.

## Verification
- `go test ./prototypes/plugins/foundry/lifecycle-dependency-graph/graph/...`
- PR line budget: 483 additions (under 1200)

## Next
- Owner review when CI green. Stay draft. Siblings 79–81 consume graph schema.
