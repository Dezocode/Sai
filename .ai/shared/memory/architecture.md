# SAI — Durable architecture memory

> Only verified, durable knowledge belongs here. Label uncertainty. Never
> record guesses. Update via reviewed commits only.

## Product

SAI is an app for parents to give their children access to the internet and
AI tools safely, supporting parental-guided growth with technology
(per `README.md`, verified 2026-07-14).

## Codebase state (verified 2026-07-14, commit 34827e7)

The repository contains no application code yet — only `README.md`,
`Team.md`, and the `.ai/` agent infrastructure. Technology stack, service
architecture, and data model are **not yet decided**; record them here as
decision records once they exist.

## Agent system architecture

- ICM (arXiv:2603.16021) filesystem workspace under `.ai/` — see
  `.ai/CONTEXT.md` for the layer map.
- Three agents: CEO (orchestrator), secretary-dezocode, secretary-monaecode.
  Charters under `.ai/agents/_roles/`; named agent profiles under
  `.ai/agents/<name>/`.
- Reporting to Slack #agentupdates via `scripts/agent-report`, wired through
  `.githooks/` (installed with `scripts/install-agent-hooks`).
- Google Drive is a replicated recovery layer per `.ai/_config/sync-policy.md`.
