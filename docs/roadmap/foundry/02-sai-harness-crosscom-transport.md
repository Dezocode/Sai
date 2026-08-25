# PR contract — Sai Harness Crosscom transport core

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Build the typed, persistent Crosscom transport **inside the Sai Harness prototype** for optimized agent->agent communication. Define one canonical event/envelope model, direct/group topology, Task-ID lineage, ack/retry/dead-letter and bounded queue/backpressure semantics. Keep GitHub/session-API effects out of this PR so the transport can be tested locally and deterministically.

## Acceptance

- [ ] Every message has a schema version, event id/idempotency key, Task-ID, source agent/runtime, target agent/group, timestamp, kind and payload.
- [ ] Repo/PR/full 40-char HEAD fields are present when the message is bound to repository work; absence is explicit for non-repo chatter.
- [ ] Direct agent->agent delivery has deterministic target resolution and cannot silently fan out.
- [ ] Group/fleet delivery has explicit membership snapshots and records which recipients were attempted/acked/failed.
- [ ] One Task-ID defines one cross-runtime work lineage; identity changes/restarts do not mint unrelated task lineages.
- [ ] Durable queue survives Harness restart without duplicate logical delivery.
- [ ] Ack semantics are explicit (at-most-once vs at-least-once by message kind); effectful actions require idempotency protection.
- [ ] Retry uses bounded attempts/backoff and deterministic dead-letter state.
- [ ] Backpressure is bounded by count/bytes/age; overload refuses or sheds according to named policy instead of unbounded disk/memory growth.
- [ ] Ordering guarantees are documented and tested; no global ordering promise is invented when only per-target/per-task ordering exists.
- [ ] Crosscom can carry work requests, evidence pointers, status, questions/answers and owner-steer events without treating any of them as verifier/flightboard authority.
- [ ] Agent self-reported completion/readiness remains evidence input only.
- [ ] Transport exposes read-only inspection/replay for owner/debugging without replaying side effects.
- [ ] Message payloads have size limits and safe serialization; malformed/oversized input fails closed.
- [ ] Local transport works with #141/session API completely offline.
- [ ] No production code depends on the transport; deletion safety remains green.
- [ ] Adversarial tests cover duplicate event ids, replay, wrong Task-ID, unknown target, group membership churn, queue full, malformed payload, dead target and restart recovery.
- [ ] Exact-head verification/review converges before owner-ready.

## Non-goals

- No normalized Cursor/Atomic hook capture yet.
- No GitHub/session API bridge or repository writes yet.
- No Foundry graduation classification/plan generation.
