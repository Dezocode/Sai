# Saul formal disposition (workflow_dispatch)

| Field | Value |
|-------|-------|
| Run | https://github.com/Dezocode/Sai/actions/runs/31738840708 |
| Reviewed head | `6c50e0b2c55b9741bcd5284511c16c65eccd08ca` |
| Contract | `20260813-ri-subprocess-init` v1 |
| disposition | **BLOCKED** |
| codex_invoked | true |
| synthetic | false (formal runner path) |
| reason | FINAL_REVIEW_PACKAGE_UNREADABLE — execution sandbox failed before package read: `bwrap: No permissions to create a new namespace`. Saul could not inspect complete exact-head diff; cannot truthfully APPROVE. |
| Job failure secondary | Commit status step 422 — description >140 chars |

## Intended-function scoring
- Formal Codex path **invoked**: yes
- Exact-head package prepared: yes (git + Hostinger)
- Saul **APPROVE** achieved: **NO**
- Org ACTIVE: **NO**

Next: repair Saul runner sandbox/namespace OR re-run when package readable; do not fabricate APPROVE.
