# PR contract — Sai Harness repo<->agent + sessions API bridge

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Connect the prototype Harness/Crosscom system to repository evidence and the #141 sessions/runtime service without making network availability or agent self-reporting into Foundry policy authority. Implement optimized **repo->agent** routing and tightly scoped **agent->repo** publishing with exact-head provenance, enrollment, idempotency and least privilege.

## Acceptance

- [ ] Treat #141 sessions-api as `REMOTE`/`REUSE` operational infrastructure, never a second verifier or required Foundry planner runtime.
- [ ] Re-resolve #141 current wire contract before implementation; do not code to stale assumptions.
- [ ] `gh` local identity is used as enrollment/identity proof; prefer a narrower scoped lane writer credential over reusing a broad long-lived GitHub token as the permanent session secret.
- [ ] Session writer, GitHub comment/status writer, verifier/flightboard publisher and graduation executor credentials are distinct capabilities.
- [ ] repo->agent adapters normalize GitHub PR/check/comment/review/session evidence into Crosscom events bound to repository, PR, Task-ID and full 40-char HEAD.
- [ ] Stale/mismatched HEAD evidence is routed as stale/mismatch, never as current work.
- [ ] GitHub polling uses caching/ETag/rate-budget controls and bounded schedules; no busy polling.
- [ ] #141 heartbeat/session publication is idempotent and server-stamped where the API contract requires it.
- [ ] Agent->repo session/status/heartbeat publishing cannot write flightboard/readiness/graduation authority.
- [ ] Optional agent->GitHub comment/status actions use explicit allowlisted doors, record actor/Task-ID/HEAD and fail closed on insufficient scope.
- [ ] No implicit merge, ready-for-review, branch rewrite, review approval or repository creation exists in this bridge.
- [ ] Repository events route to the correct persistent Harness channel; unknown/unregistered targets are parked/refused rather than invented.
- [ ] Offline operation queues safe outbound telemetry with bounded retention; authority-relevant actions never silently execute later against a changed HEAD.
- [ ] Replay/idempotency keys prevent duplicate repo effects after reconnect.
- [ ] Payload/filter rules prevent secrets/raw credentials from entering public comments or session telemetry.
- [ ] Network outage is surfaced as unavailable/degraded while local Harness/Crosscom continues functioning.
- [ ] Tests cover stale HEAD, rate limit, 401/403/422/429, duplicate delivery, reconnect, credential separation, unknown target and malicious flightboard-shaped payloads.
- [ ] Production remains independent of the Harness bridge; exact-head verification/review converges before owner-ready.

## Non-goals

- No Foundry manifest/planner/executor policy in sessions-api.
- No automatic PR merge/ready/review approval.
- No broad GitHub credential distribution to prototype agents.
