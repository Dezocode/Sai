# Implement — CTO-024 SHA-bound pins (revert HEAD-union)

- Removed `matching_grant` / `lease_task_id_bound` HEAD and working-tree
  `task_ids` union. Commit-time `task_id`/`task_ids[]` still apply.
- SHA-bound rows live in `.ai/_config/authorization.yaml` and are loaded
  only via `git show HEAD:.ai/_config/authorization.yaml`.
- Pinned eight already-pushed wave SHAs (0041/0052 Task-IDs). Did not pin
  `5ad0b94` / `7b03b97` / `5684304` (original task ids).
- `sai_auth_rebind_test.py` referenced from `scripts/verify-agent-authorization`.
- Appended CTO-024..027. CTO-024 IMPLEMENTED_AWAITING_SAUL. CTO-025
  BLOCKED_EXTERNAL. Did not disable candidate `saul-review.yml`.
- Did not PASS blockers. Did not merge. Did not edit grants/decisions/.cursor.
