# PR contract — Foundry Spin Off planner + standalone exporter

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Build the read-only Spin Off planner plus deterministic local/repository-candidate materializer. Freeze an exact prototype snapshot, compute the complete closure, classify every dependency, materialize only the allowed standalone tree, rewrite paths/modules deterministically, and prove it builds without the source Sai checkout.

## Acceptance

- [ ] Freeze repository/base/full exact prototype HEAD and dependency graph/hash before planning/materialization.
- [ ] Compute complete transitive code/config/schema/generated/runtime dependency closure.
- [ ] Every dependency receives an explicit export strategy: REUSE_SHARED, EXPORT_COPY, REMOTE, PROMOTE_SHARED or DROP; UNKNOWN/unsafe blocks export.
- [ ] Go `internal` dependencies are never assumed importable cross-repo; choose relocation/materialization, REMOTE or PROMOTE_SHARED explicitly.
- [ ] Spin Off reads production Sai; it never edits production merely to make export easier.
- [ ] Materialized tree contains only prototype + required allowed dependencies, not the whole Sai repo.
- [ ] Path/module/import/package rewrites are deterministic, reviewable and recorded in provenance.
- [ ] No `../../Sai`, implicit workspace link, local checkout assumption or undeclared environment dependency survives.
- [ ] REMOTE Sai services are explicit in config/contracts and standalone output does not falsely claim backend independence.
- [ ] Sai Harness fixture proves a systems/runtime spin-off shape including Atomic/Grokbot/Crosscom dependencies and optional #141 REMOTE/DROP treatment.
- [ ] Sai Author fixture proves native macOS + iOS/iPadOS-capable standalone graph.
- [ ] Exported backend/module code builds/tests independently where applicable.
- [ ] Native macOS build succeeds for the reference standalone app; iOS Simulator build succeeds and iPadOS capability remains valid where applicable.
- [ ] Independent proof runs with the source Sai checkout absent/hidden.
- [ ] `PROVENANCE` records source Sai commit, prototype commit, graph/plan hash, exported files, classifications, rewrites and tool version.
- [ ] Materialization is deterministic/idempotent for the same source+plan; rerun does not silently diverge.
- [ ] Actual GitHub repo publication is **not automatic in this PR** and remains a later owner-authorized executor boundary.
- [ ] Negative fixtures prove stale plan, unknown dependency, source-checkout link, illegal Go internal import, missing remote contract and path escape fail closed.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready.

## Non-goals

- No automatic GitHub repository creation.
- No App Store/TestFlight/notarization credentials.
- No production integration execution.
- No owner-facing one-click UX.
