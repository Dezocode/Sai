# Plan — CTO P1 remediation on PR #47

1. Restore `.ai/INITIALIZE.md` from `origin/main` on this research branch.
2. Set deepdive `head_sha` to CTO-reviewed tip `739b3f4ffe12d98e6dd4fd65a9475ed91e8f78e4` with provenance note + pointer to this remediation task.
3. Keep parent-run `events.jsonl` schema fix from CEO commit `31c6104` (that is audit repair, not policy).
4. Discard uncommitted duplicate HANDOFF line (agent-report dedupe).
5. Verify, push, update PR, Slack HANDOFF asking for fresh Saul review.
6. Do **not** merge; do **not** re-add INITIALIZE policy here.
