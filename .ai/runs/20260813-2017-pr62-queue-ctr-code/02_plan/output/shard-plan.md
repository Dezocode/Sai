# Plan — sha-shard-coverage (B-SAUL-QUALITY-LOOP-001)

Contractor `ctr-code-pr62smoke`. Lease `lease-c3a003pr62q1`.
Contract v12. Slice only: SHA-bound review-unit coverage.
Do not PASS, commit, push, merge, or edit other slices.

## Current vs desired

Trusted reviewer code must derive the complete changed-unit
manifest from Git at exact `base_sha`/`head_sha`. Candidate
manifests are data, not authority. A shard is a bounded
SHA-derived review chunk, not a file bucket.

Desired: every changed path (hunk, add, delete, rename, mode,
binary, workflow, schema/config) becomes a review unit with
digests and architecture-domain memberships; units partition
into SHA-derived shards (exactly one shard each); coverage
verdicts PASS/FAIL/BLOCKED; unit states PASS_CURRENT/FAIL/
STALE_*/UNREVIEWED; only PASS_CURRENT counts; HEAD change
carries PASS only when content/context/dependency/architecture/
policy digests still match; Hostinger scratch deleted after
each completed shard.

## Files (exclusive)

- NEW `.ai/shared/schemas/saul-review-manifest.schema.json`
- NEW `.ai/shared/schemas/saul-shard-evidence.schema.json`
- NEW `scripts/lib/sai_auth_review_coverage.py` (≤500)
- NEW `scripts/lib/sai_auth_review_coverage_test.py` (≤500)
- NEW `scripts/saul-review-shards`
- NEW `scripts/verify-saul-shard-quality` (`--self-test` → test module)

Production must not hardcode PR/contract/branch/SHA.
Do not edit code-health, workflows, identity, blockers, or
`.ai/shared/quality/**`.
