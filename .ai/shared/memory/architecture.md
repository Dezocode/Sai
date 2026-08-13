# SAI — Durable architecture memory

> Only verified, durable knowledge belongs here. Label uncertainty. Never
> record guesses. Update via reviewed commits only.

## Product

SAI is an app for parents to give their children access to the internet and
AI tools safely, supporting parental-guided growth with technology
(per `README.md`, verified 2026-07-14).

## Codebase state (verified 2026-08-13)

The repository contains no accepted application product stack — only ICM
coordination files, agent profiles, and the `openclaw-dashboard/` prototype
scaffold (DR-20260724). Technology stack, service architecture, and data
model are **not yet decided**; record them here as decision records once
they exist.

Code health is enforced independently of the stack via
`.ai/_config/code-health.yaml` and `scripts/verify-code-health` (decision
0005): bloat, duplicates, orphans, and CI coverage that requires an
executable `run:` step for every active check. Dispatcher detectors have
synthetic positive/negative fixtures. `live-pass` is not a negative
evaluation. Language-specific tests stay deferred until a stack decision
exists. Line-shingle Jaccard is not semantic clone detection.

## Agent system architecture

- ICM (arXiv:2603.16021) filesystem workspace under `.ai/` — see
  `.ai/CONTEXT.md` for the layer map.
- Cursor Marketplace plugins are enabled at project scope in
  `.cursor/settings.json` and indexed under `.ai/plugins/` (decision 0004).
  First plugin: pstack (`/poteto-mode`).
- Three agents: CEO (orchestrator), secretary-dezocode, secretary-monaecode.
  Charters under `.ai/agents/_roles/`; named agent profiles under
  `.ai/agents/<name>/`.
- Reporting to Slack #agentupdates via `scripts/agent-report`, wired through
  `.githooks/` (installed with `scripts/install-agent-hooks`).
- Codebase health registry `.ai/_config/code-health.yaml` (decision 0005),
  enforced in `.github/workflows/agent-audit.yml`.
- Google Drive is a replicated recovery layer per `.ai/_config/sync-policy.md`.
