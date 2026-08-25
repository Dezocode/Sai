# Graduation plan schema — draft (v0)

Plan-bound executor contract: the engine executes ONLY a validated plan bound
to the exact prototype HEAD. Deterministic fixed inputs → fixed plan; stale
plans fail. This draft precedes the schema commit; it is descriptive, not authority.

## Plan object
```
plan_id            deterministic hash of (schema_version, repo, base, prototype_head, graph_hash, operations)
schema_version     integer; engine refuses mismatch
repo               origin URL
base               full 40-char base commit
prototype_head     full 40-char exact prototype HEAD
graph_hash         canonical dependency-graph hash (from #153)
generated_at       UTC timestamp (not part of plan_id determinism)
operations         ordered list, see below
recovery           checkpoint/rollback points per operation
```

## Operations
- `integrate` — promote prototype behavior through the correct production authority via a normal production branch/PR. Never direct-to-main, never auto-ready.
- `spinoff` — materialize standalone repo candidate per #155 exporter closure; PROVENANCE record required.
- `delete-archive` — remove/archive prototype; production build/test must stay green.

## Dependency dispositions (per node, from #153 graph)
`REUSE | PROMOTE | EXPORT | REMOTE | PROMOTE_SHARED | DROP`
- Any `unresolved`/`UNKNOWN` classification → plan generation FAILS CLOSED. No partial plans.

## Execution rules
- Idempotency: every effectful operation carries an idempotency key; re-execution of a completed key is a no-op returning the prior result.
- Transactional: partial failure leaves a well-defined recoverable state at the nearest checkpoint; journal per operation.
- Authority: candidate code cannot alter executor policy; engine holds no repository-creation/merge credentials beyond the scoped door for the single authorized operation.
- Owner confirmation: required for every authority-changing operation; confirmation binds to plan_id + prototype_head.
- Telemetry (#141 sessions API) is input only — it can never substitute for verifier/planner authority, and network absence never blocks plan generation (offline-capable).
