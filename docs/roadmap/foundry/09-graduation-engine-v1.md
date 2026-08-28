# PR contract — Foundry plan-bound graduation engine

Slice 81 head: foundry/graduation-engine. Issue #160.

## Mission

Execute only validated exact-head Integrate / Spin Off / Delete-Archive plans.

## Acceptance

- Validated plans bound to exact prototype HEAD + graph_hash; stale plans refuse.
- Integrate creates draft production PR candidate; never pushes to main.
- Spinoff materializes standalone candidate with PROVENANCE.json.
- Delete/archive proves zero production dependency before removal.
- Idempotent journal and audit provenance per operation.
- E2E tests cover integrate, spinoff, delete, stale HEAD, idempotency, dependency block.
