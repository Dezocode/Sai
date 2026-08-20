# ICM workspace
Operators and agents load Layer 0 identity, six stage contracts, run artifacts, durable memory, schemas, and policy files that constrain every SAI task.
## Sub-features
- `icm-layer0` `.ai/CONTEXT.md` names governed repos, people, layers, and non-negotiable rules.
- `icm-stages` `.ai/stages/01_intake` … `06_publish_sync/CONTEXT.md` are the only stage folders.
- `icm-runs` `.ai/runs/README.md` + `<YYYYMMDD-HHMM-purpose-agent>/` `metadata.json`, `events.jsonl`, `handoff.md`, stage `NN_*/output/manifest.json`.
- `icm-memory` `.ai/shared/memory/{architecture,conventions,known-issues,repository-map}.md` plus `decisions/`.
- `decision-0001` `.ai/shared/memory/decisions/0001-adopt-icm-filesystem-architecture.md`
- `decision-0002` `.ai/shared/memory/decisions/0002-multi-runtime-agent-adapters.md`
- `decision-0003` `.ai/shared/memory/decisions/0003-contractor-charters-and-agent-memory.md`
- `decision-dr-20260724` `.ai/shared/memory/decisions/DR-20260724-openclaw-dashboard-prototype-boundary.md` prototype vs core.
- `icm-schemas` `.ai/shared/schemas/agent-event.schema.json` (enum includes `BYPASS`; `.ai/_config/reporting.yaml` `event_types` omits it) `stage-output.schema.json` `contract.schema.json`.
- `icm-security` `.ai/_config/security-policy.md` hard gates and `SAI_AUDIT_BYPASS`.
- `icm-sync` `.ai/_config/sync-policy.md` Drive as replica, never Git replacement.
- `icm-repos` `.ai/_config/repositories.yaml` Dezocode/Sai canonical, monaecode/Sai fork, SHA mirror.
- `icm-reporting-config` `.ai/_config/reporting.yaml` #agentupdates `C0BH15HDN2Z` and #help-newagents `C0BH8LCJLDS`.
- `icm-audit-docs` `.ai/audit/README.md` trail contract.
- `icm-refs` `.ai/shared/references/{git-workflow,testing,release-policy,icm-ci-policy,agent-runtimes,claude-agent-sdk,openclaw-runtime}.md`.
- `icm-product` `README.md` product sentence; `Team.md` team page (may be empty).
## How to get to it (user POV)
- Open `.ai/CONTEXT.md` then the stage `CONTEXT.md` for the current stage. Create a run with `metadata.json` matching `.ai/runs/README.md`. Read Layer 3 policy under `.ai/_config/` and `.ai/shared/` before edits.
## Driving it with verify-sai
- **Layer 0.** ::exists .ai/CONTEXT.md .ai/INITIALIZE.md
- **Stages.** ::exec scripts/verify-semantic-hierarchy
- **Schemas.** ::json .ai/shared/schemas/agent-event.schema.json
- **Policy YAML.** ::exists .ai/_config/repositories.yaml
- **Decisions.** ::exists .ai/shared/memory/decisions/DR-20260724-openclaw-dashboard-prototype-boundary.md
- **Proof.** ::sai relevant --path .ai/CONTEXT.md --tool Read
## Gotchas
- `.ai/plugins/` is an ICM index, not a Cursor loader. Empty `Team.md` is still a mapped surface; do not invent team content.
