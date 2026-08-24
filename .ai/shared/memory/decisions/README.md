# Decision records

One file per durable decision: `NNNN-<slug>.md`, numbered sequentially.

Every record must include: date, task ID, decision, context, alternatives
considered, rationale, consequences, approver (when approval was required),
and the superseded record (when applicable). Prefer superseding decisions
over silently rewriting history: mark the old record `Status: superseded by
NNNN` and leave it in place.

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
