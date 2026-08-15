# Plan — architecture-review (B-SAUL-QUALITY-LOOP-001)

Contractor `ctr-code-pr62smoke`. Lease `lease-c3a003pr62q1`.
Contract `20260813-pr62-saul-smoke` v12. Work item `architecture-review`.
Do not commit. Do not push. Do not merge. Do not PASS.

## Spec

`.ai/shared/quality/saul/ARCHITECTURE.md` (read-only). Every inner-loop
invocation runs LOCAL_ARCH + IMPACT_ARCH. SYSTEM_ARCH is required before
technical convergence. 100% shard PASS without SYSTEM_ARCH is not
convergence. Architecture PASS with a missing shard is not convergence.

## Deliverables (exclusive paths)

- `.ai/shared/schemas/saul-architecture-evidence.schema.json`
- `scripts/lib/sai_auth_review_architecture.py` (≤500)
- `scripts/lib/sai_auth_review_architecture_test.py` (≤500)
- `scripts/verify-saul-architecture-quality` (chmod +x; `--self-test`
  runs the test module; comment-references the python files)

## Engine

1. LOCAL_ARCH — changed components + direct neighborhood.
2. IMPACT_ARCH — domains invalidated even when files have zero changed
   lines. Invalidated + untouched + old proof → STALE, not PASS_CURRENT.
3. SYSTEM_ARCH — assembled current-head synthesis. Broad/foundational
   impact sets SYSTEM_ARCH_REQUIRED_NOW.
4. Material FAIL appends ARCH-* blocker payloads in memory only (no live
   ledger write). Clearance requires authentic Saul architecture proof;
   Cursor/contractor/self cannot PASS.
5. Production code has no current PR/contract/branch/SHA defaults.

## Fixtures

- arch-local-impact-good
- arch-system-missing-bad
- arch-shards-missing-bad
- arch-domain-stale-bad
- arch-fail-creates-blocker-good
- arch-system-required-now-good

Denied: code-health.yaml, workflows, coverage/authenticity files,
sai_auth_review.py, blockers ledger, decisions, authorizations, quality
docs.
