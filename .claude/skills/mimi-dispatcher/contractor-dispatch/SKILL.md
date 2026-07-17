---
name: contractor-dispatch
description: >-
  Dispatch a contractor agent against a Cora-issued contract: validate the
  contract on disk, prepare branch/worktree/run scaffolding, and produce the
  contractor's onboarding handoff. Use for "@mimi dispatch <contractor>" or
  "digest contract <id>" requests.
---

# Contractor dispatch

## Preconditions (all must hold before any dispatch)

1. Contract exists in git at `.ai/contracts/<contract-id>/` with
   `contract.json` + `contract.md`. Chat text is **not** a contract.
   Missing contract → route the owner to **Cora** (`ctr-admin`); never
   hand-scaffold one.
2. Contractor is in `.ai/agents/registry.json`. Provisional contractors may
   receive a dispatch *drill* (routing + digestion) but perform no product
   work and are never flipped `active` by you — that takes Sai VERIFY.
3. Contract `status` is `active` and its gates (e.g. a fulfillment gate on
   a prerequisite contract) are satisfied — check, don't assume.

## Dispatch procedure

1. Create task-id `YYYYMMDD-HHMM-<slug>-mimi` (UTC) and run folder with
   `metadata.json` including `file_claims` for everything the dispatch
   touches; check claims against other active runs' `metadata.json` —
   overlap → `[SAI][CONFLICT]`, stop.
2. Queue `[SAI][PLAN]` describing: contractor, contract-id, target branch
   (`proj/<project>/<ctr-id>/<slug>` for contractors), worktree location
   (isolated, outside Drive-synced paths), and Slack channel protocol.
3. Produce the onboarding handoff: point the contractor at the contract's
   `onboarding-prompt.md`; do not paraphrase contract terms — link them.
4. Record the dispatch in `.ai/runs/<task-id>/03_implement/output/` and
   queue `[SAI][HANDOFF]` tagging the contract admin (Cora) and Sai.

## Hard limits

No merging, no force-push, no registry activation, no channel creation,
no secrets anywhere. monaecode overrides Sai; conflicts are posted, not
resolved silently.
