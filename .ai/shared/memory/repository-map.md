# SAI — Repository map

> Verified 2026-08-28 against `Dezocode/Sai:main` at `b429c7cc` after prototype
> lane enforcement (#136). This is a curated durable map of architectural
> surfaces, not a branch inventory. Keep current when durable top-level or
> authority boundaries change.

| Path | Purpose |
|---|---|
| `README.md` | Product description |
| `Team.md` | Team page (currently empty) |
| `AGENTS.md` / `CLAUDE.md` / `CODEX.md` / `OPENCLAW.md` | Agent/runtime entry routers and repository instructions |
| `.ai/` | ICM agent workspace — see `.ai/CONTEXT.md` |
| `.ai/INITIALIZE.md` | Read-and-execute initialization protocol for new agents |
| `.ai/_config/` | Repository, reporting, sync, and security policy |
| `.ai/agents/` | Role charters, registry, and named agent folders |
| `.ai/shared/memory/` | Durable memory (this folder) |
| `.ai/shared/schemas/` | JSON schemas for events and stage outputs |
| `.ai/shared/references/` | Git workflow, testing, release, CI, and runtime references |
| `.ai/stages/` | ICM stage contracts |
| `.ai/runs/` | Per-task working artifacts and handoffs |
| `.ai/audit/` | Audit trail documentation |
| `.cursor/settings.json` | Project-scoped Cursor plugins/settings |
| `.cursor/skills/` | Project Agent Skills, including `/lauren-mode` and `verify-sai` |
| `.cursor/rules/` | Shared Cursor operating rules |
| `.githooks/` | Reporting git hooks |
| `.github/` | CI workflows and trusted repository policy |
| `apps/apple/` | Native macOS and iOS/iPadOS SwiftUI application shells |
| `apps/apple/Packages/SaiKit/` | Shared Swift package: `SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`, `SaiFeatures` |
| `api/openapi.yaml` | OpenAPI boundary between native clients and authoritative Go backend |
| `cmd/sai/` | Production Go server entrypoint |
| `internal/` | Authoritative Go backend/domain implementation |
| `design/` | Production Sai Design Language contract/schema |
| `cmd/sai-verify/` | Canonical feature-map verifier kernel, CLI, hooks, and proof engine |
| `cmd/sai-design-check/` | Production design/source checker plus prototype-lane structural enforcement |
| `prototypes/plugins/` | **Reserved canonical prototype path** `prototypes/plugins/<plugin>/`; may be absent until the first prototype lands; non-shipping and one-way isolated from production |
| `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md` | Enabling contract for the prototype plugin lane (#75) |
| `docs/architecture/SAI-PROTOTYPE-LANE-ENFORCEMENT.md` | Mechanical lane-enforcement contract (#136) |
| `deploy/backend/` | Backend deployment boundary |
| `migrations/` | Database/schema migration boundary |
| `openclaw-dashboard/` | Agent/runtime operational dashboard infrastructure |
| `scripts/` | Repository verification, agent, reporting, and operational scripts |
| `go.mod` | Root Go module `github.com/Dezocode/Sai` |

## Prototype lane semantics

- Only `prototypes/plugins/<plugin>/...` receives prototype authority.
- Canonical prototype SwiftUI/design experimentation is intentionally free from
  production design-literal restrictions; `SaiDesignLanguage` is optional
  preferred reuse, not prototype compliance.
- Production Swift/Go/build graphs must never depend on `prototypes/**`.
- Prototype-scoped work may reuse stable Sai capabilities but may not modify
  protected production Go for convenience.
- Prototype code/design does not graduate by file move; production integration
  requires explicit reconciliation and normal production verification.

## Remotes and fork topology

- `Dezocode/Sai` — canonical repository, default branch `main`.
- `monaecode/Sai` — fork of `Dezocode/Sai`, default branch `main`.
- Feature-branch names are ephemeral and intentionally omitted from this map.
