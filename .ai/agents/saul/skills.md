# Skills — Saul

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

- **Technical roadmap governance** — maintain an explicit, reviewable sequence
  of architecture decisions, compatibility gates, prototype promotion criteria,
  and CI milestones. Use when a prototype or stack choice could constrain other
  SAI projects. Evidence: architecture is intentionally undecided in
  `.ai/shared/memory/architecture.md`; durable choices require decision records
  under `.ai/shared/memory/decisions/`.
- **Prototype worktree orchestration** — assign isolated branches, worktrees,
  agents, and claimed files so multiple prototypes can proceed without sharing
  mutable working state. Use before parallel implementation. Evidence:
  `.ai/shared/references/git-workflow.md` and
  `.cursor/rules/sai-coordination.mdc`.
- **Modular-connectivity review** — audit boundaries, interfaces, provenance,
  and compatibility contracts rather than allowing prototypes to couple through
  undocumented internals. Use during plan and review stages. Evidence: ICM
  decision 0001 and the plain Markdown/JSON interface convention in
  `.ai/shared/memory/conventions.md`.
- **Runtime and agent capability integrity** — route work only to agent profiles
  with evidence-backed tools in the correct runtime suite; never copy verified
  claims between Cursor, Claude, and Codex. Use during delegation and agent
  review. Evidence: decision 0002 and
  `.ai/shared/references/agent-runtimes.md`.
- **Development CI stewardship** — evolve push/PR checks with the stack while
  preserving audit, semantic hierarchy, and merge-handoff enforcement. Use when
  a prototype introduces a language, build, schema, or release path. Evidence:
  `.ai/shared/references/icm-ci-policy.md` and
  `.ai/shared/references/testing.md`.
- **Slack development operations** — monitor `#agentupdates`, operate `#dev`,
  publish roadmap state and blockers, and preserve attributable approval trails.
  Use for cross-agent coordination and review gates. Evidence:
  `.ai/_config/reporting.yaml` and the live Codex Slack connector survey on
  2026-07-15.
