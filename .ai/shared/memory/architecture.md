# SAI — Durable architecture memory

> Only verified, durable knowledge belongs here. Label uncertainty. Never
> record guesses. Update via reviewed commits only.

## Product

SAI is an app for parents to give their children access to the internet and
AI tools safely, supporting parental-guided growth with technology
(per `README.md`).

## Codebase state (verified 2026-08-28, `main` at `b429c7cc`)

- Native Apple application foundations exist under `apps/apple/`: SwiftUI
  shells for macOS and iOS/iPadOS plus the shared `SaiKit` package.
- `SaiKit` owns the shared `SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`, and
  `SaiFeatures` package boundaries.
- Go is the authoritative backend/domain core under `cmd/sai/` and `internal/`.
  `api/openapi.yaml` is the Swift/Go API boundary.
- `design/sai-design-language.json` is the production design contract and keeps
  `featureUIAllowed=false`; production UI remains governed by
  `SaiDesignLanguage`.
- `deploy/backend/` and `migrations/` are explicit deployment and migration
  boundaries.
- `.cursor/skills/verify-sai/` is the canonical feature map;
  `cmd/sai-verify` is its machine verifier. `cmd/sai-design-check` enforces the
  production design/source contract and the structural prototype firewall.

## Prototype plugin lane (verified 2026-08-28, PR #136 on `main`)

The verifier reserves and enforces the canonical non-shipping prototype path
`prototypes/plugins/<plugin>/`. The directory may be absent from `main` until a
real prototype lands; the authority is the verifier-owned path contract, not
pre-created placeholder files.

Inside a canonical plugin, SwiftUI and prototype-local visual, layout,
typography, interaction, and motion experiments are intentionally free from
production design-literal restrictions. `SaiDesignLanguage` may be reused when
useful, but it is not prototype compliance and `PrototypeDesign/` is only an
optional organizational convention.

The firewall remains one-way: production Swift/Go/build graphs may never depend
on `prototypes/**`; prototypes may reuse stable Sai capabilities but
prototype-scoped work may not modify protected production Go for convenience.
Prototype design or code gains no production authority by existing. Graduation
requires explicit reconciliation and a normal production PR.

Lane contracts are in `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` and
`docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md`; the verifier map is
`.cursor/skills/verify-sai/features/prototype-plugins.md`.

## Agent system architecture

- ICM (arXiv:2603.16021) filesystem workspace under `.ai/` — see
  `.ai/CONTEXT.md` for the layer map.
- Cursor Marketplace plugins are enabled at project scope in
  `.cursor/settings.json` and indexed under `.ai/plugins/` (decision 0004).
  Cloud Agents use the project Custom Mode `/lauren-mode` with alias `/lauren`.
- Role charters and named agent profiles live under `.ai/agents/`; do not treat
  the current set of agent names or remote branches as durable architecture.
- Reporting to Slack #agentupdates uses `scripts/agent-report`, wired through
  `.githooks/` (installed with `scripts/install-agent-hooks`).
- Google Drive is a replicated recovery layer per `.ai/_config/sync-policy.md`.
