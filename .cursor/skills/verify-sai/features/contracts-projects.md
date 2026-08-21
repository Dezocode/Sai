# Contracts and projects
Contract Administrator scaffolds versioned contracts and project branch indexes; reviewers evaluate contractor PRs against `contract.json` acceptance criteria.
## Sub-features
- `contract-scaffold` `scripts/agent-contract-scaffold --project-name --project-slug --principal --contractor-type --isolation-mode --runtime`
- `contract-schema` `.ai/shared/schemas/contract.schema.json` validates `contract.json`.
- `contract-templates` `.ai/contracts/_templates/{cursor,claude,codex,openclaw}-contract-template.{md,json}`
- `contract-pr-review` `scripts/agent-contract-pr-review --contract-id ID --branch BRANCH [--task-id ID]` → pass|pending_manual|fail
- `contract-splunk` `.ai/contracts/20260715-splunk-clone-monaecode/` plus reviews/
- `contract-mimi-dispatcher` `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/`
- `contract-openclaw` `.ai/contracts/20260722-openclaw-dashboard-dezocode/` including `first-prompt-attach-contract.md`, amendments, and deploy checklists
- `project-splunk` `.ai/projects/splunk-clone/{branches-index,contract-refs,coordination/slack-channel}.json`
- `project-openclaw` `.ai/projects/openclaw-dashboard/{branches-index,contract-refs,coordination/slack-channel}.json`
- `contracts-readme` `.ai/contracts/README.md` ID format `YYYYMMDD-<slug>-<principal>`
## How to get to it (user POV)
- Create: `scripts/agent-contract-scaffold` as documented in `.ai/contracts/README.md` Review: `scripts/agent-contract-pr-review --contract-id 20260715-splunk-clone-monaecode --branch <branch>` Read live contracts under `.ai/contracts/<id>/contract.md`
## Driving it with verify-sai
- **Templates.** ::exists .ai/contracts/_templates/claude-contract-template.json
- **Schema.** ::json .ai/shared/schemas/contract.schema.json
- **Live JSON.** ::json .ai/contracts/20260722-openclaw-dashboard-dezocode/contract.json
- **Review.** ::exists scripts/agent-contract-pr-review
- **Allowlist.** ::exec scripts/verify-contract-shell-allowlist
## Gotchas
- Isolation mode `prototype` vs `integration` is a contract field, not a hidden default. Do not edit another contractor's claimed branch; coordinate via indexes + Slack. OpenClaw dashboard remains prototype per DR-20260724. `.ai/projects/mimi-dispatcher/` is absent (contract exists; product gap).
