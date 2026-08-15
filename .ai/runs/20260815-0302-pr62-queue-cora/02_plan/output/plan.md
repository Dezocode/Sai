# Plan — Cora Saul quality loop reuse of v12

HEAD `516893c68d8d8a77fe43e5e05fe804b3e511a25b`. Contract
`20260813-pr62-saul-smoke` v12. Lease `lease-c3a003pr62q1`.
Contractor `ctr-code-pr62smoke`. Task-ID
`20260813-2017-pr62-queue-ctr-code`.

**reuse=true. v13=false. A-013=false.** Quality-loop
executable work sits under already-granted v12
`allowed_paths`. Quality docs under `.ai/shared/quality/**`
are officer-authored read-only spec. Not authority
expanding. Not path expansion. denied_paths unchanged.

Four disjoint contractor slices (Cora does not implement):

1. **sha-shard-coverage** — `sai_auth_review_coverage`,
   `verify-saul-shard-quality`, schemas under
   `.ai/shared/schemas/**`.
2. **architecture-review** — LOCAL_ARCH / IMPACT_ARCH /
   SYSTEM_ARCH via `sai_auth_review_architecture`,
   `verify-saul-architecture-quality`.
3. **authenticity-primary-context** — attestation v2 +
   canonical authenticity validator (`verify-saul-authenticity`,
   `sai_auth_saul_check`, `saul-publish-check`);
   `sai_auth_primary_context` fail-closed
   NO_PRIMARY_CONTEXT / AMBIGUOUS_PRIMARY_CONTEXT; no
   hardcoded current PR/contract/branch/SHA in reusable
   production code; pubkey pin officer/Hostinger only.
4. **finding-ci-detectors-bloat** — finding-to-CI
   (`verify-saul-finding-regression-guards`),
   `saul-review-controller`, activate Decision-0005
   detectors with fixtures + unconditional CI
   (`saul-authenticity-proof`, `saul-sha-shard-quality`,
   `saul-architecture-quality`,
   `saul-finding-regression-guard`); compact
   `.ai/_config/code-health.yaml` (321>300) via
   split/include under `_config/**` only.

Cora writes: compact REQ-5300187244 on
`requirements/ledger.yaml` (stays ≤300); admin review YAML
`reviews/cora-saul-quality-loop-v12-reuse.yaml`; this wave
dir; standing-run handoff append. Does not write A-013, v13,
blockers/items, scripts, workflows, `_config` executable
content, authorizations, decisions, or `.cursor`. Does not
bump lease or `contract.json`. Commit uses grant Task-ID
`20260813-2016-pr62-queue-cora`. This wave does not push.

Contractor next: implement four slices under v12; append
blocker progress without PASS. Only Hostinger Codex with
unforgeable attestation may PASS.
