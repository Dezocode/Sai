# PR contract — Foundry plan-bound graduation engine

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Build the effectful **graduation engine** that executes only previously validated exact-head Integrate / Spin Off / Delete-Archive plans. It must be transactional, idempotent, auditable, least-privilege and owner-controlled. The engine cannot invent classifications or bypass normal production/repository review.

## Acceptance

- [ ] Engine accepts only validated plans bound to the exact current prototype HEAD + graph/plan hash; stale plans refuse.
- [ ] Integrate execution creates a candidate branch and normal production PR from the approved plan; never pushes directly to `main`.
- [ ] Integrate execution never auto-marks ready, auto-merges, waives CI/Saul or mutates verifier policy.
- [ ] Spin Off execution materializes the approved standalone candidate; GitHub repository creation is a separate capability requiring explicit owner authorization.
- [ ] Delete/Archive execution proves zero production dependency before removal/archive and verifies production remains green.
- [ ] Engine executes plan classifications exactly; it cannot invent PROMOTE/EXPORT/REMOTE/DROP decisions absent from the validated plan.
- [ ] Effectful operations are staged/transactional so partial failure leaves a well-defined recoverable candidate and exact failure point.
- [ ] Same plan/source idempotency key does not duplicate branches/repos/artifacts or silently diverge.
- [ ] Audit/provenance records source SHA, graph/plan hash, actor/owner authorization, output branch/repo candidate, transformation map, checks and final state.
- [ ] Credential capabilities are separated: production branch/PR writer, standalone repo creator, session telemetry and verifier authority are not interchangeable.
- [ ] Repository-creation/production-write credentials are unavailable to untrusted prototype code and ordinary Harness agents.
- [ ] All writes assert target/base/head expectations immediately before effect; changed target state fails rather than applying a stale plan.
- [ ] Harness/Crosscom may transport execution status/questions but cannot authorize execution or alter policy.
- [ ] Generated production PR and standalone candidate run their own appropriate verification; engine does not fabricate pass state.
- [ ] End-to-end fixture proves delete, integrate and spin-off paths without production backdependency.
- [ ] Failure-injection tests cover crash between stages, duplicate request, changed HEAD/base, revoked credential, GitHub 4xx/5xx, partial materialization and owner-cancel.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready.

## Non-goals

- No polished human Foundry UI yet.
- No automatic merge, ready-for-review, App Store/TestFlight/notarization.
- No hidden policy/classification inside executor.
