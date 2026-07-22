# Plan — 20260722-2305-pr46-contract-lifecycle-ceo

## Problem
PR #46 review (dezocode P1): Splunk-clone contract recorded Alpha as
`superseded` while registry used `retired`; handoff and profiles mixed both
terms.

## Approach
1. Set contract `assigned_contractors[].status` to `retired` (schema enum).
2. Keep "superseded by Splunky" only in `note` / narrative fields.
3. Add Layer 3 reference `.ai/shared/references/agent-lifecycle.md`.
4. Extend `verify-agent-setup` to reject invalid contractor status strings and
   registry/contract mismatches.

## Scope
Within CEO purpose: ICM lifecycle coherence and CI enforcement only.
