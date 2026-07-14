# Skills — pending Phase 6 grant

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

- **SAI framework bootstrap** — design and maintain `.ai/` ICM workspace,
  git hooks (`.githooks/`), CI enforcement (`.github/workflows/agent-audit.yml`),
  and initialization scripts. Evidence: runs `20260714-0418-sai-agent-framework`,
  `20260714-0501-initialize-protocol`, PR #3.
- **Agent onboarding protocol** — execute and upgrade `.ai/INITIALIZE.md` so
  every new agent scaffolds a folder, verifies capabilities, registers in
  `registry.json`, and posts to #agentupdates and #help-newagents. Evidence:
  `.ai/agents/README.md`, `scripts/agent-scaffold`, `scripts/agent-verify-caps`.
- **Hook matrix verification** — test hooks in scratch clones when the VM has
  platform-managed `core.hooksPath`; `agent-init` auto-spawns temp clones.
  Evidence: run `20260714-0439-hook-verification`, `known-issues.md`.
- **Slack MCP delivery** — use `message` param (not `text`) for
  `slack_send_message`; confirm via returned link. Evidence: `known-issues.md`.
