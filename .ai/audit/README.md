# Audit trail

The audit trail for SAI agent work has four layers of defense:

1. **Run artifacts** — `.ai/runs/<task-id>/` (committed): plans, changes,
   verification, reviews, events, handoffs.
2. **Local event queue** — `.git/agent-events/queue/` and `sent/`
   (NOT committed; lives in `.git/`): schema-valid JSON events produced by
   `scripts/agent-report`, delivered to Slack #agentupdates idempotently by
   `event_id`. Failures stay in `queue/`; acknowledged events move to
   `sent/`. Events are never reordered, dropped, or fabricated.
3. **Git metadata** — commit trailers (`Task-ID`, `Agent`, `Plan`,
   `Report-Event`) verified by `scripts/verify-agent-audit`.
4. **CI verification** — `.github/workflows/agent-audit.yml` runs
   `verify-agent-audit` on pushes and PRs, and publishes a server-side push
   report (Git has no native post-push hook; CI is the trustworthy
   confirmation of remote state).

Git hooks are local and bypassable by design; that is why CI re-verifies
commit and PR metadata. Emergency bypasses (`SAI_AUDIT_BYPASS`) are recorded
as BYPASS events and must be reported to #agentupdates with the reason.

Long-term recovery copies of audit records are mirrored to Google Drive
under `SAI/repositories/<owner>-sai/audit/` per `.ai/_config/sync-policy.md`.
