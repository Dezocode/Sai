# Verify — sha-shard-coverage

Commands actually run (working tree, not committed):

- `python3 -m json.tool` on both new schemas → OK
- `bash -n scripts/saul-review-shards` → 0
- `bash -n scripts/verify-saul-shard-quality` → 0
- `python3 -m py_compile` coverage + test → 0
- production hardcode scan (contract/branch/lease/PR) → none
- `python3 scripts/lib/sai_auth_review_coverage_test.py` → exit 0
- `scripts/verify-saul-shard-quality --self-test` → exit 0

Fixtures executed (11):

- shard-manifest-complete-good
- shard-missing-unit-bad
- shard-duplicate-covering-omission-bad
- shard-wrong-content-digest-bad
- shard-stale-head-bad
- shard-wrong-base-digest-bad
- shard-synthetic-bad
- shard-codex-not-invoked-bad
- shard-binary-omitted-bad
- shard-rename-delete-omitted-bad
- shard-scratch-removed-good

Line counts: coverage.py 466; test.py 313; wrappers 7/11.
B-SAUL-QUALITY-LOOP-001 remains open (do not PASS).
Did not commit, push, or merge.
