# Saul SHA-bound review shards

## Canonical term

A **shard** is a bounded review chunk derived from the exact Git SHA state Saul is reviewing. It is **not** an arbitrary file bucket, worker bucket, or long-lived partition.

Every shard must bind at minimum:

- repository;
- `base_sha`;
- `head_sha`;
- exact diff/chunk range or non-text object identity;
- chunk/content digest;
- semantic-context digest;
- relevant dependency/interface digest;
- relevant architecture-context/domain digest;
- quality-policy version/digest; and
- deterministic shard identifier derived from those inputs.

For text changes, shards originate from exact diff hunks/chunks and include the bounded semantic context required for review. Deletes, renames, mode changes, generated files, binary changes, and other non-hunk changes require explicit review units and cannot disappear from coverage.

## Trigger

Every contractor result accepted and integrated by the Primary establishes a new exact HEAD and triggers an incremental Saul review. Trusted reviewer code recomputes the expected current manifest from Git; candidate-produced manifests are not authoritative.

Prior PASS evidence may carry forward only when content, semantic context, relevant dependencies/interfaces, architecture context, requirements, and policy remain equivalent. Otherwise it is `STALE` and must be reviewed again.

## Verdicts

Authoritative shard verdicts are `PASS`, `FAIL`, or `BLOCKED`. A qualifying PASS requires every unit in the shard to be explicitly adjudicated by real Hostinger Codex. Unknown/skipped/missing/duplicate units cannot contribute to technical convergence.

A `FAIL` immediately creates a canonical technical blocker but does not stop review of other still-valid shards. Defect discovery and Ralph remediation may proceed concurrently.

## Coverage

Technical convergence requires exact equality between the trusted expected unit set and current passed coverage: 100% current coverage, zero missing, zero duplicate, zero stale, zero failed, correct base/head/diff digests, real Codex invocation, and non-synthetic evidence.

Detailed shard scratch is bounded on Hostinger. After validation, durable detail is published/offloaded to GitHub, compact digests/state are retained, and local completed shard scratch is deleted.
