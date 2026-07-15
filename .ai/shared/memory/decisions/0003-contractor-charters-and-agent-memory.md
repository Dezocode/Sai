# Decision 0003 — Contractor charters and per-agent memory

**Status:** accepted
**Date:** 2026-07-15
**Deciders:** dezocode, monaecode (via SAI coordinated agent system)
**Supersedes:** none

## Context

The SAI agent suite needs contractor agents (coding, design, and future types)
hired under owner-defined contracts, with a Contract Administrator role to
create contracts and review contractor work history. Multi-year contract audit
requires durable per-agent memory mirrored to Google Drive.

## Decision

1. **Contractor charters** live under `.ai/agents/_roles/contractor-*` and
   `.ai/agents/_roles/contract-administrator/`. Contractors follow full ICM
   stages plus contract compliance constraints.

2. **Two-protocol onboarding:** contractors are pointed to `.ai/ONBOARDING.md`
   (contract-driven persona and capability enrichment). Sai audits every
   contractor build against both `INITIALIZE.md` and `ONBOARDING.md`.

3. **Contracts are versioned Git artifacts** at `.ai/contracts/<contract-id>/`,
   validated by `.ai/shared/schemas/contract.schema.json`. Drive mirrors
   contracts after GitHub SHA verification — never the other way around.

4. **Per-agent memory** is canonical in Git at
   `.ai/agents/<name>/memory/`, mirrored to
   `SAI/agents/<agent-id>/memory/` on Drive. Shared memory
   (`.ai/shared/memory/`) remains for cross-agent decisions; agent memory
   holds contract-scoped audit history.

5. **Branch naming for contractors:**
   `proj/<project-slug>/<contractor-agent-id>/<task-slug>`. Multiple
   contractors on one project share `project_slug` but have unique
   `<contractor-agent-id>` segments.

6. **Contractor agent IDs** use prefix `ctr-code-*` or `ctr-design-*`.
   Registry status is `provisional` during ONBOARDING, `active` only after
   persona gate + Sai audit, `retired` when contract closes. Retired agents
   preserve `memory/` indefinitely.

7. **Slack channel creation** for project coordination requires explicit owner
   approval per security policy. Contract Admin drafts; owner approves.

## Consequences

- New scripts: `agent-contract-scaffold`, `agent-contract-pr-review`
- Extended: `agent-sync-drive`, `agent-scaffold`, `verify-semantic-hierarchy`
- New event types: `CONTRACT`, `CONTRACT_REVIEW`, `PERSONA_GATE`
- Drive layout extended with `contracts/`, `agents/<agent-id>/memory/`,
  `projects/<project-slug>/`

## References

- `.ai/ONBOARDING.md`
- `.ai/shared/schemas/contract.schema.json`
- `.ai/_config/sync-policy.md`
- Decision 0001 (ICM filesystem architecture)
- Decision 0002 (multi-runtime agent adapters)
