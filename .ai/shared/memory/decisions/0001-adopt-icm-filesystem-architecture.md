# 0001 — Adopt ICM filesystem architecture for agent coordination

- Date: 2026-07-14
- Task-ID: 20260714-0418-sai-agent-framework-cursor-cloud-30d8
- Status: accepted
- Approver: dezocode (requested via #agentupdates and the shared operating
  prompt)

## Decision

Adopt the Interpretable Context Methodology (ICM, arXiv:2603.16021) as the
coordination architecture for SAI agents: a version-controlled `.ai/`
workspace with numbered stage folders, Markdown/JSON stage interfaces,
layered context loading, per-run artifact folders, and human review gates.
Layer a three-agent hierarchy on top: a CEO orchestrator agent and one
secretary agent per co-founder (dezocode, monaecode).

## Context

Two co-founders each run Cursor Desktop agents against a fork pair
(`Dezocode/Sai` canonical, `monaecode/Sai` fork). They need shared,
version-controlled instructions, auditable intermediate work, Slack
reporting to #agentupdates, and a Google Drive recovery mirror.

## Alternatives considered

- Framework-based orchestration (LangChain/CrewAI/AutoGen): rejected — the
  workflows are sequential and human-reviewed; a code framework adds opacity
  and developer dependency the problem does not require.
- Unstructured per-user Cursor rules only: rejected — no shared memory, no
  audit trail, no stage gates, no coordination records.

## Rationale

ICM makes every intermediate artifact a readable, editable file; the folder
structure itself scopes context per stage. ICM does not by itself solve
concurrent multi-agent coordination, so concurrency is handled with isolated
worktrees, branch ownership, GitHub PRs, and coordination records — not by
ICM alone. ICM is a preprint pattern, not conclusively validated research;
we adopt it as an architectural convention, revisable by a superseding
decision.

## Consequences

- All agents follow the six stage contracts under `.ai/stages/`.
- Per-task artifacts live in `.ai/runs/<task-id>/` and are committed unless
  they are large, secret, machine-specific, or noisy.
- Reporting and audit are enforced in depth: git hooks, `scripts/agent-report`
  queue, and CI verification (`scripts/verify-agent-audit`).
