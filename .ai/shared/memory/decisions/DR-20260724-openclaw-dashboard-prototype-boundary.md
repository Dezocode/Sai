# DR-20260724 — OpenClaw dashboard prototype boundary

- Date: 2026-07-24
- Task-ID: 20260724-0311-pr45-architecture-decision-ceo
- Status: accepted
- Approver: Sai (CEO, `ceo-automation`) per `[SAI][VERIFY][20260724-0311-pr45-architecture-decision-ceo]`; architecture gate cleared for Part A scaffold merge subject to this record and checklist amendments

## Decision

Classify PR #45 / contract `20260722-openclaw-dashboard-dezocode` as **(a) isolated prototype scaffold**, not **(b) a core SAI parent-app architecture proposal**.

| Layer | Classification | On canonical `main` after Part A merge |
|---|---|---|
| `.ai/agents/alfred/`, OpenClaw runtime adapter, draft contract, INITIALIZE.md + CI extensions | ICM agent infrastructure (L0–L3) | Accepted scaffold — compatible with canonical governance |
| `openclaw-dashboard/` (Markdown/JSON spec, design tokens, smoke gates) | Prototype product scaffold | Documentation and experiment inputs only — **not** accepted application stack |

Stack choices referenced in the contract and tech-stack docs (Tauri 2, React 19, Tailwind 4, Phaser, SwiftUI) are **proposed experiment inputs**. They do not adopt a parent-application architecture for the SAI coordination repository.

## Context

Saul CTO re-review (2026-07-24, head `904070f`) accepted all P1/P2 security and evidence-gate fixes but withheld merge at the **architecture/promotion gate**: the checklist allowed scaffold merge before stack-specific tests and a recorded stack decision; `contract.json` and tech-stack files commit concrete framework assumptions.

Sai CEO was asked to classify PR #45 and authorize Part A scaffold merge to `Dezocode/Sai:main`.

## Alternatives considered

**(b) Core architecture proposal** — rejected for Part A merge. Would require a separate reviewed decision record defining stack scope, versions, fallback, migration, and stack-specific CI **before** canonical `main` integration.

**Keep product scaffold off `main` entirely** — rejected. Agent infrastructure (Alfred, OpenClaw runtime, contract, ICM extensions) is valuable on `main`; only the product stack boundary needed explicit classification.

## Rationale

The canonical SAI repository remains a coordination framework with no accepted application product stack (Saul roadmap lane: foundation = proposed). Merging PR #45 as scaffold intake is compatible when `openclaw-dashboard/` is explicitly bounded as prototype documentation, contract stays `draft`, Alfred stays `provisional`, and promotion to core requires a future superseding decision.

## Consequences

- **Part A merge authorized (conditional):** after this DR lands and checklist/contract/banner amendments on PR #45 branch; then Saul confirm + cofounder merge (M3/M4).
- **Part B (contract activation) and Part C (org onboarding):** remain blocked until fulfillment gates complete.
- **Stub smoke (exit 2):** expected pre-fulfillment for application/ingest suites; not a Part A merge blocker.
- **Promotion to core:** requires superseding decision record + stack-specific CI contract + green full smoke (no ignored stubs) + human review by both cofounders.
- **Risk if ignored:** implicit stack adoption on canonical `main` without governance decision.

## References

- PR #45: https://github.com/Dezocode/Sai/pull/45
- Saul CTO review: 2026-07-24T03:06 UTC (head `904070f`)
- Sai VERIFY: `[SAI][VERIFY][20260724-0311-pr45-architecture-decision-ceo]`
- Checklist: `.ai/contracts/20260722-openclaw-dashboard-dezocode/ACTIVATION-AND-MERGE-CHECKLIST.md`
