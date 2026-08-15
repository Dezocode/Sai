# SAI product-quality system

This directory is the stable Layer-3 specification for SAI product quality. It **extends Decision 0005**; it is not a second quality framework.

Machine policy remains in `.ai/_config/code-health.yaml`. Executable detectors and trusted reviewer implementation remain under `scripts/` and `scripts/lib/`. Schemas remain under `.ai/shared/schemas/`. This directory defines the durable semantics those executables must enforce.

## Control model

The Cursor Primary runtime executes the Ralph outer loop. Every integrated contractor completion creates a new exact candidate HEAD and triggers Saul's Hostinger/Codex inner quality loop. Saul reviews SHA-bound shards plus the architecture affected by that exact state and publishes current evidence to the single GitHub Check `Saul / Product Quality`.

Blocking shard or architecture findings enter the canonical blocker ledger immediately and feed Ralph. The loop continues until exact-head technical convergence, Sai governance approval of the same state, and `READY_FOR_HUMAN_REVIEW`.

## Layout

- `saul/SHARDS.md` — canonical meaning and proof contract for SHA-bound review shards.
- `saul/ARCHITECTURE.md` — incremental + system architecture review requirements.
- `saul/FINDING_TO_CI.md` — per-finding regression-guard promotion into Decision-0005 CI.
- `heuristics/README.md` — bounded heuristic CI rules when an invariant is not cheaply decidable.

Documentation is not completion. PR #62 remains blocked until the executable reviewer/controller, coverage validator, architecture invalidation, GitHub Check publication, finding-to-CI path, fixtures, and readiness integration are implemented and passed by real Saul.
