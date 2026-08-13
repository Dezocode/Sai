# Plan — PR #62 remediation queue (Sai)

Exact head at intake: `d113fa0bf75b43491c25723f57cf9dec1e6196de`.
Controlling comment: 5285843795.

## Why Sai was looping

Cursor automation "Sai" retriggered the full CEO protocol on every PR
event, including unchanged Saul REQUEST_CHANGES. That is observation, not
a state-machine step. Cora/contractor were not claiming remediation.

## Do

1. Sai: tracked officer grants, close bootstrap at d113fa0, Decision 0006
   amendment, cheap automation step 0, human grant to keep 0007.
2. Cora: consume run 31736391403, v3 path expansion (human-approved),
   stale v2 lease, queue items, v3 contractor lease.
3. Contractor: dispatch script, CTO-009/010/011 code, trusted Saul
   launcher, tests, CI wiring.

Do not merge. Do not mark ready. Do not revert 0007.
