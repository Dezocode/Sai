# Remediation queue

Durable claimable transitions for this contract. A repeated eval of the
same `(task, revision, head, reviewer, findings_digest)` is a cheap NOOP.
See `.ai/shared/schemas/remediation-item.schema.json` and comment 5285843795.
