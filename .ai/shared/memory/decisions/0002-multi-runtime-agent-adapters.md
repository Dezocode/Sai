# 0002 — Multi-runtime agent adapters (Cursor, Claude Code, Codex Desktop)

- Date: 2026-07-15
- Task-ID: 20260715-0229-runtime-adapters-ceo
- Status: accepted
- Approver: dezocode (Slack direction 2026-07-15; layout approved)

## Decision

Extend the SAI agent framework with **runtime adapters** under each agent
folder (`.ai/agents/<name>/runtimes/{cursor,claude,codex}/`) while keeping
**one registry row and one runtime-neutral identity** per agent. Cursor
remains the default generation path; Claude Code and OpenAI Codex Desktop
gain parallel initialization suites without duplicate registries or charters.

## Context

Mimi's initialization (PR #4) registered a valid agent identity but exposed
a Cursor-first bias in `INITIALIZE.md`, `agent-scaffold`, and
`agent-automation-spec`. The Anthropic **@Claude Slack app** was mistaken for
the registered agent **Mimi** because no Layer 0 entry-point map existed.
ChatGPT and Sai CEO review after merge identified cross-runtime `tools.json`
corruption risk (addressed in draft PR #5; mechanical guards pending merge).

## Alternatives considered

- **Separate Claude/Codex registries** — rejected; violates single ICM Layer 1
  identity and duplicates semantic lines.
- **Duplicate AGENT.md per runtime** — rejected; identity must stay neutral.
- **Drive-only runtime docs** — rejected; GitHub `.ai/shared/` is canonical;
  Drive mirrors after verified SYNC only.

## Rationale

ICM already separates layers: identity (Layer 1) vs stable reference (Layer
3) vs per-task runs (Layer 4). Runtime-specific tools and automation belong in
indexed subfolders, not parallel agent trees. `registry.json` gains
`primary_runtime` and `entry_points` so Slack, Drive `#knowledgebase`, and
humans can resolve how to invoke an agent without conflating Slack bots with
registered identities.

## Consequences

- Every active agent declares `primary_runtime` and maintains
  `runtimes/<suite>/tools.json` for that runtime's verified capabilities.
- Root `tools.json` remains a **manifest** (backward compatible) pointing at
  `canonical_capabilities_path` until all agents migrate.
- `CLAUDE.md` and `CODEX.md` are Layer 0 entry routers; they do not replace
  `.ai/INITIALIZE.md`.
- `scripts/agent-scaffold` creates `runtimes/` skeletons; Cursor path unchanged
  as default (`--primary-runtime cursor`).
- Codex Desktop is a **stub suite** until a live initialization supplies
  evidence-backed `runtimes/codex/tools.json`.
- Drive index updates follow Git merge + `agent-sync-drive` SYNC report; never
  lead canonical structure.

## Supersedes

Nothing. Complements decision 0001 (ICM filesystem architecture).
