# PR contract — Foundry read-only Integrate planner

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Build the deterministic **read-only Integrate planner** that consumes an exact prototype snapshot + validated dependency graph and emits a complete production-promotion plan without modifying production.

## Acceptance

- [ ] Planner accepts only a manifest/graph bound to the current exact prototype HEAD; stale input fails.
- [ ] Every prototype-owned and consumed artifact/edge receives an explicit integration disposition; UNKNOWN blocks completion.
- [ ] Existing stable Sai capabilities are REUSE rather than duplicated.
- [ ] PrototypeDesign artifacts are PROMOTE, DROP or explicitly remain prototype-only; none are copied wholesale into production.
- [ ] Swift views/modules map to proposed `SaiFeatures`/package/target destinations without carrying prototype path authority.
- [ ] Go/domain behavior distinguishes already-REUSEd production behavior from prototype behavior that requires a separate production-authority change.
- [ ] OpenAPI/client/server contract changes are explicit and separately reviewable.
- [ ] REMOTE dependencies and #141 operational infrastructure are represented honestly rather than folded into production product authority.
- [ ] Planner never recommends integration by moving the entire prototype directory.
- [ ] Conflicts fail: stale source, production path collision, forbidden prototype dependency, unresolved design authority, unsupported module visibility, missing API contract or UNKNOWN classification.
- [ ] Output is deterministic machine-readable + human-readable and includes exact source SHA, graph hash, proposed transformations/paths, required checks and blockers.
- [ ] Planner is read-only: no branch creation, file write to production tree, GitHub mutation, merge/ready action or repo publication.
- [ ] Core planning remains offline-capable.
- [ ] Golden fixtures for Sai Harness and Sai Author prove stable planning; negative fixtures prove incomplete classifications cannot become ready.
- [ ] `sai-verify`/production policy remain independent authorities; planner cannot waive their failures.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready.

## Non-goals

- No production PR generation/execution yet.
- No standalone export.
- No owner-facing one-click UI.
