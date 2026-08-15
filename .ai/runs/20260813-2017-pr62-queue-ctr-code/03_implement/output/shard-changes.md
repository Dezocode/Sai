# Implement — sha-shard-coverage

Trusted Git-derived review-unit manifest + SHA-bound shard
partition + coverage evaluator. Candidate evidence is data.

- NEW `scripts/lib/sai_auth_review_coverage.py` (466)
- NEW `scripts/lib/sai_auth_review_coverage_test.py` (313)
- NEW `scripts/saul-review-shards` / `scripts/verify-saul-shard-quality`
- NEW schemas `saul-review-manifest` / `saul-shard-evidence`

Units cover hunk/add/delete/rename/mode/binary plus workflow
and schema/config kinds. Every unit is in exactly one shard.
PASS_CURRENT only counts; synthetic and codex_not_invoked FAIL.
HEAD change → STALE_* unless digests still match. Scratch
deleted after each completed shard.

Did not edit code-health, workflows, identity, blockers, quality
docs, or other slices. Did not PASS. Did not commit/push/merge.
