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
- Cursor Marketplace plugins are enabled at project scope in
  `.cursor/settings.json` and indexed under `.ai/plugins/` (decision 0004).
  First plugin: pstack (`/poteto-mode`). Cloud Agents pin the project
  Custom Mode `/lauren-mode` with alias `/lauren` (decisions 0005, 0006).
- `.cursor/skills/verify-sai/` is the canonical feature map; `cmd/sai-verify` is the only machine parser.
- Three agents: CEO (orchestrator), secretary-dezocode, secretary-monaecode.
  Charters under `.ai/agents/_roles/`; named agent profiles under
  `.ai/agents/<name>/`.
- Reporting to Slack #agentupdates via `scripts/agent-report`, wired through
  `.githooks/` (installed with `scripts/install-agent-hooks`).
- Google Drive is a replicated recovery layer per `.ai/_config/sync-policy.md`.

## Prototype plugin lane (verified 2026-08-28, PR #136 on `main`)

A verifier-owned non-shipping prototype lane exists at `prototypes/plugins/`.
Production design authority (`featureUIAllowed=false`, `SaiDesignLanguage`) is
unchanged. Lane contracts are in
`docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` and
`docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md`; mechanical enforcement
is owned by `cmd/sai-verify` and `cmd/sai-design-check` (see
`.cursor/skills/verify-sai/features/prototype-plugins.md`).
