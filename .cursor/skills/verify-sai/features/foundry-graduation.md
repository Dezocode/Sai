# Foundry graduation engine
Plan-bound prototype graduation executor (integrate, spinoff, delete-archive) scoped under `prototypes/plugins/foundry/`.
## Sub-features
- `foundry-grad-engine` `prototypes/plugins/foundry/graduation-engine/*` plan-bound v0 executor with idempotent journal and audit provenance.
- `foundry-grad-cli` `prototypes/plugins/foundry/graduation-engine/cmd/graduate/*` CLI entry for dry-run and execute modes.
- `foundry-grad-fixture` `prototypes/plugins/foundry/test-widget/*` miniature prototype fixture for E2E tests.
- `foundry-plan-schema` `.ai/shared/schemas/foundry-plan-v0.schema.json` JSON schema for validated graduation plans.
- `foundry-plan-draft` `docs/plan-schema-draft.md` human-readable plan schema draft for slices 79–81.
## How to get to it
- Read `docs/roadmap/foundry/09-graduation-engine-v1.md` and `docs/plan-schema-draft.md`.
- Run `go run ./prototypes/plugins/foundry/graduation-engine/cmd/graduate --help` from repo root.
- Tests: `go test ./prototypes/plugins/foundry/graduation-engine/...`.
## Driving it with verify-sai
- **Engine tests.** ::gotest ./prototypes/plugins/foundry/graduation-engine/... timeout=120
- **Schema.** ::json .ai/shared/schemas/foundry-plan-v0.schema.json
- **Fixture.** ::exists prototypes/plugins/foundry/test-widget/manifest.json prototypes/plugins/foundry/test-widget/widget.txt
- **Roadmap.** ::exists docs/roadmap/foundry/09-graduation-engine-v1.md
## Gotchas
- Production Go must never import `prototypes/**`. Engine is prototype-scoped only.
- Plans bind to exact prototype HEAD and graph_hash; stale plans fail closed.
- GitHub repository creation is stubbed without owner token; spinoff materializes local candidate only.
- Integrate writes draft PR candidate JSON only; never pushes to `main` or marks ready.
