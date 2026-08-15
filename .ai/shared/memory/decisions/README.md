# Decision records

One file per durable decision: `NNNN-<slug>.md`, numbered sequentially.

Every record must include: date, task ID, decision, context, alternatives
considered, rationale, consequences, approver (when approval was required),
and the superseded record (when applicable). Prefer superseding decisions
over silently rewriting history: mark the old record `Status: superseded by
NNNN` and leave it in place.

See also: `0006-agent-authorization-loop.md` (accepted; PR #62 comment 5282088737),
`0007-parallel-runtime-intelligence-plane.md`,
`0008-persistent-primary-cursor-orchestrator.md` (PR #62 comment 5287297355),
`0009-trusted-saul-comptroller-product-quality-loop.md` (accepted; PR #62 comments 5303750100, 5303804678, 5303809236; supersedes only 0008's "No Decision 0009" clause).

Template:

```markdown
# NNNN — <title>

- Date: YYYY-MM-DD
- Task-ID: <task-id>
- Status: accepted | superseded by NNNN
- Approver: <human, if required>

## Decision
## Context
## Alternatives considered
## Rationale
## Consequences
```
