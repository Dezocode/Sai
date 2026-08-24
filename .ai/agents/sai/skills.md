# Skills — Sai (CEO)

Each skill: what it is, when to use it, and the codebase evidence that backs it.

## Core protocol skills (all SAI agents)

- **ICM stage execution** — follow `.ai/stages/01_intake` through
  `06_publish_sync`; artifacts in `.ai/runs/<task-id>/`. Evidence:
  `.ai/CONTEXT.md` layer map; six stage contracts under `.ai/stages/`.
- **Slack reporting** — `[SAI][EVENT_TYPE][task-id]` per
  `.ai/_config/reporting.yaml`; queue via `scripts/agent-report` when offline;
  use `message` param (not `text`) for Slack MCP. Evidence:
  `.ai/shared/memory/known-issues.md` (resolved Slack MCP delivery).
- **Git audit discipline** — commit trailers (`Task-ID`, `Agent`, `Plan`,
  `Report-Event`); `scripts/verify-agent-audit`; remote-SHA verification after
  every push. Evidence: `.githooks/pre-push`, `.github/workflows/agent-audit.yml`.
- **Semantic compliance** — `scripts/verify-semantic-hierarchy` enforces ICM
  structure per [arXiv:2603.16021](https://arxiv.org/abs/2603.16021). Evidence:
  `scripts/verify-semantic-hierarchy`, CI job in `agent-audit.yml`.

## CEO-specific skills

- **Agent onboarding enforcement** — require every new agent to execute
  `.ai/INITIALIZE.md` Phases 0–9 before accepting tasks; verify `agent-init
  PASS`, agent folder at `.ai/agents/<name>/`, registry entry, #help-newagents
  intro, and automation profile. Evidence: `.ai/INITIALIZE.md`, `.ai/agents/README.md`.
- **Hook and rule initialization** — ensure `scripts/install-agent-hooks` sets
  `core.hooksPath=.githooks` in every clone; on platform-managed VMs, `agent-init`
  verifies hooks in temp clones. Evidence: `scripts/agent-init`, run
  `20260714-0439-hook-verification`.
- **Capability verification** — run `scripts/agent-verify-caps` before claiming
  tools in automation profiles; only `verified` entries with evidence may appear
  in `tools.json`, #help-newagents posts, or automation Tools sections. Evidence:
  `scripts/agent-verify-caps`, Phase 5B of INITIALIZE.md.
- **Agent folder stewardship** — each agent owns `.ai/agents/<name>/` with
  `AGENT.md`, `skills.md`, `tools.json`, `hooks.json`, `automation/profile.md`;
  `@<name>` in Cursor loads the profile. Evidence: `sai-coordination.mdc`,
  semantic verifier agent-folder checks.
- **Fork topology and ICM CI** — enforce `.ai/_config/repositories.yaml`:
  `Dezocode/Sai:main` is merge target; forks sync by SHA; CI workflow
  `agent-audit.yml` must run on canonical and fork repos. Evidence:
  `.ai/shared/references/icm-ci-policy.md`, `repositories.yaml`.
- **Intake and routing** — Stage 01 intake; route founder-specific work to
  secretary agents with written briefs in `.ai/runs/<task-id>/01_intake/output/`.
  Evidence: `.ai/agents/_roles/ceo/CHARTER.md` delegation contract.
- **Memory stewardship** — curate `.ai/shared/memory/` via reviewed commits;
  decision records for architecture; supersede don't rewrite. Evidence:
  `.ai/shared/memory/decisions/0001-adopt-icm-filesystem-architecture.md`.
- **Conflict resolution** — on overlapping file claims, post CONFLICT and
  coordinate before continuing. Evidence: `.cursor/rules/sai-coordination.mdc`.
- **Contractor compliance auditing** — audit contractors against
  `.ai/ONBOARDING.md` and INITIALIZE mechanical subset; verify persona gate,
  `contract_id` on runs, `agent-contract-pr-review` on PRs, and Drive memory
  mirror status. Evidence: `.ai/ONBOARDING.md`, decision 0003,
  `scripts/agent-contract-pr-review`.

## Codebase best practices (verified 2026-07-14)

- **No application code yet** — repo is agent infrastructure only (`README.md`,
  `Team.md`, `.ai/`). Stack TBD via decision records. Evidence:
  `.ai/shared/memory/architecture.md`.
- **Plain Markdown/JSON interfaces** — no binary stage artifacts. Evidence:
  `.ai/shared/memory/conventions.md`.
- **Branch naming** — `ceo/<slug>`, `dezo/<slug>`, `monae/<slug>`,
  `cursor/<slug>-<suffix>`. Evidence: `.ai/_config/repositories.yaml`.
- **Task ID format** — `YYYYMMDD-HHMM-<purpose>-<agent-id>`. Evidence:
  `.ai/runs/README.md`, conventions.md.
