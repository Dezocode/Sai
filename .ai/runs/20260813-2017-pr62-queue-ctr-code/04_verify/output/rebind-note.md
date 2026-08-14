# Verify note — HEAD task_id aliasing

Self-tests in `scripts/lib/sai_auth_rebind_test.py` (wired from
`scripts/verify-agent-authorization --self-test`):

- grant HEAD task_id alias (same id/principal) PASS
- HEAD grant different principal FAIL
- HEAD grant must not expand commit-time paths FAIL
- lease HEAD task_id/`task_ids` alias PASS
- lease `task_ids[]` without `task_id` PASS; mismatch FAIL
- HEAD lease must not expand commit-time `allowed_paths` FAIL
- HEAD lease different agent FAIL
- contractor self-PASS REJECT

`origin/main..HEAD` may still fail until officer/contractor HEAD rebind is
present. This contractor did not PASS blockers or merge.
