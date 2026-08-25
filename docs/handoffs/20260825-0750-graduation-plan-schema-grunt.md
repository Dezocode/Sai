# Handoff — graduation plan schema draft
Task-ID: 20260825-0750-graduation-plan-schema-grunt
PR: Dezocode/Sai#156 (draft, grunt-owned)
Author: grunt (ox-alpha)
## What
docs/plan-schema-draft.md: plan object (deterministic plan_id, exact-head binding), three operation types, six dispositions, fail-closed unresolved rule, idempotency/transaction/owner-confirmation/telemetry-non-authority rules.
## Why
#156 contract requires plan-bound transactional execution; this draft pins the schema shape before implementation.
## Verify
All dispositions match PRD reference graduation classifications; no direct-to-main/auto-ready language anywhere.
