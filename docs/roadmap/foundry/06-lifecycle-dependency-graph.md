# PR contract — Foundry lifecycle + deterministic dependency graph

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Introduce the non-authoritative prototype manifest/schema, lifecycle model and deterministic dependency graph/classification engine required by the Foundry. Use **Sai Harness** and **Sai Author** as the first two real fixtures so the model proves both systems-runtime and native-product dependency shapes before any planner/executor exists.

## Acceptance

- [ ] Small versioned descriptive prototype manifest exists for identity, platforms, entry points, modules, capabilities, API contracts, external/runtime dependencies and supported graduation paths.
- [ ] Manifest grants **zero security authority** and cannot choose prototype roots, design authority, trusted bases, verifier policy or executor credentials.
- [ ] Schema rejects unknown authority-changing fields rather than silently ignoring them.
- [ ] Lifecycle states model DRAFT, VALIDATED, INTEGRATION_PLANNED, SPINOFF_PLANNED, GRADUATING, INTEGRATED, SPUN_OFF, ARCHIVED and DELETED without granting authority merely by state transition.
- [ ] Deterministic graph enumerates Swift/package/resources/generated inputs, Go imports/modules, OpenAPI/schema/client inputs, SaiDesignLanguage/PrototypeDesign, runtime tools/services and external dependencies.
- [ ] Every node/edge gets an explicit classification: REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP or unresolved/UNKNOWN.
- [ ] UNKNOWN/unresolved blocks planning.
- [ ] Graph/manifest output binds to repo, base, exact full 40-char prototype HEAD, schema/tool version and canonical graph hash.
- [ ] Same source SHA + tool version yields byte/canonical-equivalent graph output.
- [ ] Core graph generation is offline-capable; network/session API availability is not required.
- [ ] Sai Harness fixture models Atomic/tmux/Grokbot/Crosscom/hook/runtime dependencies explicitly and classifies #141 sessions-api as REMOTE/REUSE/DROP as appropriate rather than silently copying it.
- [ ] Sai Author fixture models native package/SaiKit/design/API dependencies and platform build graph.
- [ ] Go `internal`/visibility constraints are represented so future spin-off cannot assume illegal cross-repo imports.
- [ ] Path normalization/realpath checks occur before classification so symlink/traversal tricks cannot alter graph authority.
- [ ] No Integrate, Spin Off, repo creation or production mutation occurs in this PR.
- [ ] `sai-verify` maps/proves manifest/schema/graph capability while remaining the authority for canonical prototype boundaries.
- [ ] Golden/adversarial fixtures cover stale HEAD, unknown class, candidate-root spoofing, hidden transitive dependency, remote service, Go internal, deleted file and deterministic reorder cases.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready.

## Non-goals

- No production promotion planning yet.
- No standalone materialization yet.
- No effectful graduation engine or UX.
