# DRAFT — 000N — Grok Build CLI as a SAI runtime suite

> **Status:** proposed draft in run artifacts only — **not** accepted, **not**
> filed under `.ai/shared/memory/decisions/`. Co-founder review required.
> Suggested number: next free decision id after existing `0002` series
> (confirm against `decisions/` at filing time).

- Date: 2026-07-22 (draft)
- Task-ID: 20260722-2341-grok-build-runtime-research-ctr-admin
- Status: **proposed**
- Approver: _pending dezocode / monaecode_

## Decision (proposed)

Extend SAI multi-runtime adapters (decision 0002) with a **Grok Build CLI**
suite:

- Suite folder: `.ai/agents/<name>/runtimes/grok/`
- Layer 0 entry: `GROK.md`
- `primary_runtime` value: `grok-build-cli`
- Contract templates: `.ai/contracts/_templates/grok-contract-template.*`
- Scaffold/verify: `scripts/agent-scaffold --primary-runtime grok` and
  `agent-verify-caps --environment grok-build-cli`

Keep **one registry row and one runtime-neutral `AGENT.md`** per agent.
Do not treat Grok’s ability to read `CLAUDE.md` / `.cursor/rules/` as
identity equivalence with those runtimes.

## Context

Dezocode requested research on adding Grok Build CLI to the SAI organization.
Grok Build is a terminal agentic harness (TUI, headless `-p`, ACP
`grok agent stdio`) with `~/.grok` control plane, project `.grok/`, distinct
permissions/sandbox/hooks-trust, MCP CLI, worktrees, and local `/loop`
automation. Existing SAI enums and scaffolds only know cursor/claude/codex.

## Alternatives considered

- **No new suite; document Grok under Claude** — rejected; different binary,
  auth, ACP, hooks paths, automation model; corrupts capability evidence.
- **No new suite; document under Cursor** — rejected; Automations UI ≠ Grok
  `/loop`/ACP; tool IDs and MCP management differ.
- **Wait until a Grok-primary agent is named** — acceptable *deferral of
  filing*, but the **decision** should still accept the suite shape so Cora
  does not invent ad-hoc contracts.
- **Separate Grok registry** — rejected; violates single Layer 1 identity
  (same as 0002 alternatives).

## Rationale

Decision 0002 already established runtime adapters as indexed subfolders.
Grok is a peer harness with first-class project integration and org adoption
intent. Encoding it as `runtimes/grok/` preserves ICM layering and prevents
Slack/bot/runtime confusion.

## Consequences (when accepted and implemented)

- Update `.ai/shared/references/agent-runtimes.md`, `CONTEXT.md` runtime
  table, `INITIALIZE.md` Phase 5B/7 branches, contract schema enum,
  `agent-scaffold` / `agent-contract-scaffold`, and agents README.
- First Grok-primary agent must run live Phase 5B on a machine with `grok`
  installed; no fabricated caps.
- Project `.grok/hooks` and MCP require trust/security review before commit.
- Never commit `~/.grok/auth.json` or tokens.
- Cora may then offer Grok contractor templates; Sai audits protocol.

## Supersedes

Nothing. **Extends** decision 0002.

## Evidence pointers

- Run report:
  `.ai/runs/20260722-2341-grok-build-runtime-research-ctr-admin/03_implement/output/research-report.md`
- https://docs.x.ai/build/overview
- https://docs.x.ai/build/features/project-rules
- https://docs.x.ai/build/cli/reference
