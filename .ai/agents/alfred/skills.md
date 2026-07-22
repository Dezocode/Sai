# Skills — Alfred

> Fill from Phase 5A best-practice survey. Each skill: what it is, when to
> use it, and the codebase evidence that backs it.

## Core protocol skills (all SAI agents)

- **ICM stage execution** — follow `.ai/stages/01_intake` through
  `06_publish_sync`; artifacts in `.ai/runs/<task-id>/`.
- **Slack reporting** — `[SAI][EVENT_TYPE][task-id]` format per
  `.ai/_config/reporting.yaml`; queue via `scripts/agent-report` when
  offline.
- **Git audit discipline** — commit trailers; `scripts/verify-agent-audit`;
  remote-SHA verification after every push.
- **Semantic compliance** — `scripts/verify-semantic-hierarchy` before
  protected pushes.

## Role-specific skills

<!-- Add skills unique to this agent's purpose after Phase 5A survey -->
