# Handoff — contractor (Saul 31756720206 remediations)

Contract v4, lease `lease-c3a003pr62q1`.

Ingested qualifying Saul REQUEST_CHANGES (comment 5287885648):
CTO-015, CTO-016, CTO-017, CTO-018.

- Removed candidate empty-dest freeze from `saul-review.yml` (CTO-015).
- Hermetic `invoke-saul-review --self-test` (CTO-017).
- Quoted blocker ledger YAML and parse it in self-test (CTO-018).
- Did not technically PASS any blocker.

## 2026-08-14 HEAD task_id union (scripts only)

`matching_grant` / `lease_task_id_bound` keep commit-time paths and also
union HEAD/working-tree `task_id`/`task_ids` for the same grant/lease id
and principal/agent. Leases honor `task_ids[]`. Self-PASS still rejected.
Do not merge. `self_pass: false`. Range replay may still fail until Cora/Sai
HEAD rebind is visible to the verifier; this commit does not edit grants or
leases.
