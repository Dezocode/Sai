# Plan — CTO-030 remove candidate Hostinger path (A-012/v12)

Do not PASS. Do not merge. Do not push. Skip-guard is not a
trust boundary. Delete candidate-controlled `saul-review.yml`.
Harden trusted default-branch job `if:` so Hostinger is acquired
only for same-repo `pull_request_target` or `workflow_dispatch`
from the default-branch ref. Job `if:` is evaluated before
runner assignment.

Retarget tests at the trusted file; absent `saul-review.yml` is
PASS. Ledger CTO-030 IMPLEMENTED_AWAITING_SAUL, CTO-031 TRIAGED.
Keep 025 IMPLEMENTED_AWAITING_SAUL with a supersede note. Keep
026 uncleared. Do not rework 015..021/024/028/029.
