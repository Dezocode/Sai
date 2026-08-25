# Sai Prototype Foundry v1.1 — chronological implementation stack

This roadmap overlays the owner-provided Foundry PRD v1 onto current repository reality. It **does not replace the PRD invariants**. See [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md).

## Observed prerequisite state at roadmap creation

Re-resolve all heads before implementation; these are provenance, not permanent pins.

- PR #136 `prototype/lane-enforcement` — observed `bf6ea587bfa171086e10b1d2bb9c0224d804d9a7`. Mechanical prototype-lane authority prerequisite.
- PR #141 `specs/agent-runtime-registry` — observed `b9c53c21c9d878ba186e8f0b4c7e2ff9e22823c6`. Sessions/runtime registry, exact-head telemetry, verifier-owned flightboard, plus currently mixed Sai CLI/harness experimentation.
- PR #146 `prototype/cross-intercom-lane` — observed `74cfd78e2050d848dff058571d962deca210c4b9`. Prototype Crosscom + Sai Harness experiments: Atomic-derived persistent channels, Grokbot supervisor, `.sai` hook model, inbox/outbox, audit gateway, Telegram optional bridge.

All successor PRs remain **DRAFT** until their exact-head contract is satisfied. Any new commit resets exact-head CI/review evidence.

## Architectural placement

```text
PRODUCTION AUTHORITY
  sai-verify · Sai Design Language · Go/OpenAPI · normal production PRs
            ^
            | stable capabilities / typed APIs only
            |
PROTOTYPE LANE — prototypes/plugins/**
  Sai Harness prototype
    ├─ persistent Atomic runtime
    ├─ Grokbot supervisor
    ├─ Crosscom transport
    ├─ normalized hook suite
    ├─ local state / audit / replay
    └─ repo bridge adapters
            |
            | REMOTE / REUSE operational evidence
            v
  PR #141 sessions-api
    runtime registry · heartbeat · reconciliation · exact-head evidence
    (observability, never Foundry policy authority)

FOUNDRY
  manifest/graph -> Integrate planner -> Spin Off planner/exporter
                 -> plan-bound graduation engine -> owner UX
```

## Stream model

The Harness must optimize three independent but composable data directions without granting agent-managed merge authority:

1. **agent -> agent** — Task-ID bound Crosscom messages, targeted or group fan-out, exactly-once/at-least-once semantics explicit, ack/retry/dead-letter, bounded queues, persistent channels.
2. **repo -> agent** — GitHub PR/check/comment/session evidence normalized into read-only work/evidence events and routed to the correct Task-ID / PR / exact HEAD.
3. **agent -> repo** — explicitly authorized outputs only: session/heartbeat telemetry, comments/status/evidence through scoped doors; no implicit merge/ready/flightboard authority.

Every envelope must carry sufficient provenance to reject ambiguous attribution: schema version, event id/idempotency key, Task-ID, agent identity/runtime, repo, PR when applicable, **full 40-char HEAD** when applicable, origin, target, timestamp and payload kind.

## Hook model

The Harness owns a **prototype-local normalized hook bus**, not production `.cursor` authority. Adapters may bind Cursor/Atomic/Grokbot events into one internal event vocabulary. Production root `.cursor/hooks.json` continues to enforce `sai-verify` and cannot be silently bypassed or replaced.

The normalized suite should cover the useful lifecycle/tool surfaces already exercised in Sai: workspace/session start/end, prompt receipt, pre/post tool, tool failure, shell before/after, MCP before/after, file read/edit, subagent start/stop, compact, stop/wake, agent response/thought, and Harness tick/heartbeat. Unsupported runtime events must be declared rather than fabricated.

## Credential model

- Local `gh` identity may prove enrollment/ownership.
- Do **not** require a broad long-lived GitHub token as the permanent session writer credential when a narrower scoped lane credential can be minted/provisioned.
- Writer/session rights and verifier/flightboard rights remain mechanically separate.
- Prototype code never receives repository-creation, merge, ready-for-review, or verifier-policy credentials.

## Chronological PR sequence

### 1. `roadmap/foundry-v1-1-sai-harness` — PRD binding + architecture contract
Contract-only initialization. Attach PRD reference, freeze current prerequisites, define Sai Harness/Foundry boundaries and create the successor stack. No runtime implementation.

### 2. `prototype/sai-harness-canonical-runtime` — canonical persistent Harness prototype
Converge validated #141/#146 Harness experiments under one canonical `prototypes/plugins/sai-harness/` tree. One registered agent = one persistent Atomic-backed channel; Grokbot supervision, local journal/audit, restart/resume and deletion safety. No production runtime dependency.

### 3. `prototype/sai-harness-crosscom-transport` — Crosscom transport core
Build the typed message/envelope model and optimized agent->agent transport: Task-ID lineage, direct/group topology, ack/retry/dead-letter, backpressure, durable queue and channel delivery. No GitHub writes yet.

### 4. `prototype/sai-harness-hook-suite` — normalized hook/event bus
Adapt supported Cursor/Atomic/Grokbot hook surfaces into a typed Harness event vocabulary, including aspect decomposition/routing, without assuming nested `.cursor` configs auto-load or weakening production verifier hooks.

### 5. `prototype/sai-harness-repo-bridge` — repo<->agent + sessions API bridge
Connect the Harness to the #141 runtime/session service and GitHub evidence planes. Implement repo->agent routing and tightly scoped agent->repo publishing with exact-head, idempotency and least-privilege enrollment. #141 remains REMOTE/REUSE observability, not Foundry policy.

### 6. `prototype/sai-author-reference-shell-v2` — native product reference fixture
Retain the original PRD's native-product proof: smallest real macOS + iOS/iPadOS-capable Sai Author shell under the lane, SaiDesignLanguage-first, SaiKit reuse, build proof and zero production back-dependency. It may use the Harness for development/telemetry but must not require Harness availability to build/run its product surface.

### 7. `foundry/lifecycle-dependency-graph` — descriptive manifest + deterministic graph
Introduce the non-authoritative prototype manifest/schema and deterministic dependency graph/classification model. Use **both Sai Harness and Sai Author** as reference fixtures. Model #141 as REMOTE/REUSE/DROP as appropriate; model Atomic/tmux/GitHub/runtime dependencies explicitly. Core graph generation is offline and exact-head bound.

### 8. `foundry/integrate-planner` — read-only production promotion planning
Classify every artifact/edge and generate deterministic Integrate plans for exact prototype snapshots. No production writes. Detect stale source, conflicts, PrototypeDesign promotion, Go/OpenAPI production changes and unresolved dependencies.

### 9. `foundry/spinoff-planner-exporter` — standalone closure + materialization
Compute the complete closure, choose export strategy per dependency, materialize standalone candidates and prove independence from the source Sai checkout. Harness is a strong systems spin-off fixture; Author is the native-app fixture.

### 10. `foundry/graduation-engine` — plan-bound transactional executor
Execute only validated exact-head plans. Generate production PR candidates, standalone repo candidates, or deletion/archive operations. Idempotent, auditable, recoverable, least privilege, never direct-to-main and never auto-ready.

### 11. `foundry/owner-ux` — human Foundry controls
Expose Integrate / Spin Off / Delete-Archive with dry-run first, dependency explanations, exact-head evidence, execution progress and explicit confirmation. Sessions/flightboard are telemetry inputs only; they cannot substitute for verifier/planner authority.

## Global invariants for every successor

- [ ] One legible authority mission per PR; no opportunistic unrelated cleanup.
- [ ] Keep prototype implementation in the verifier-owned lane; any production capability gap uses a separate production-authority PR.
- [ ] Production Swift/Go/build/deploy graphs retain zero prototype dependency.
- [ ] Sai Design Language remains default for ordinary prototype UI; `PrototypeDesign/` stays narrow/non-authoritative.
- [ ] `sai-verify` remains mapping/completeness/preservation authority; no parallel verifier.
- [ ] Candidate manifests/config cannot select roots or trust boundaries.
- [ ] Full 40-character exact-head provenance at every PR/evidence/plan boundary.
- [ ] Network/session API availability is never required for core Foundry plan generation.
- [ ] Agents may report work/evidence but cannot self-award flightboard, merge readiness, graduation classification or executor authority.
- [ ] Credentials are least-privilege and separated by capability.
- [ ] Deterministic fixed-input outputs; explicit idempotency for effectful doors.
- [ ] Bounded CPU/queues/retry; no busy-polling daemon architecture.
- [ ] Deleting the reference prototype leaves production build/test green.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready; new commits reset evidence.
