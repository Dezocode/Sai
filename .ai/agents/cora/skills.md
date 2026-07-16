# Skills — Cora (Contract Administrator)

Each skill: what it is, when to use it, and the codebase evidence that backs it.

## Core protocol skills (all SAI agents)

- **ICM stage execution** — follow `.ai/stages/01_intake` through
  `06_publish_sync`; artifacts in `.ai/runs/<task-id>/`.
- **Slack reporting** — `[SAI][EVENT_TYPE][task-id]` per
  `.ai/_config/reporting.yaml`; queue via `scripts/agent-report` when offline.
- **Git audit discipline** — commit trailers; remote-SHA verification after
  every push.
- **Semantic compliance** — `scripts/verify-semantic-hierarchy` before
  protected pushes.

## Contract Administrator skills (verified tools only)

- **Contract intake and drafting** — gather project name, isolation mode,
  contractor type, runtime, principal; produce `contract.json`, `contract.md`,
  and `onboarding-prompt.md` via `scripts/agent-contract-scaffold` (verified).
  Evidence: `.ai/agents/_roles/contract-administrator/CHARTER.md`,
  `.ai/contracts/README.md`.
- **Contractor scaffolding** — create provisional registry entries and agent
  folders with per-agent memory via `scripts/agent-scaffold --with-memory`
  and `scripts/agent-memory-scaffold` (both verified).
  Evidence: `.ai/ONBOARDING.md`.
- **Contract history review** — load contract, contractor `memory/audit/`,
  and PR branches; produce `CONTRACT_REVIEW` via
  `scripts/agent-contract-pr-review` (verified; live run
  `20260715T215324Z` → `pending_manual`). Evidence:
  `.ai/shared/schemas/contract.schema.json`.
- **Scaffold safety verification** — run `scripts/verify-scaffold-safety`
  after scaffold script changes (verified).
- **GitHub PR inspection** — `gh pr view` / `gh pr list` for branch and PR
  state (verified).
- **Isolated worktrees** — `git worktree add` outside Drive/sync paths
  (verified at `/tmp`).
- **Sai audit routing** — post `CONTRACT` and coordinate `PERSONA_GATE`
  before contractors become `active`. Evidence: `.ai/agents/_roles/ceo/CHARTER.md`
  contractor compliance section.
- **Domain coordination** — brief Saul (dezocode) or Mimi (monaecode) when
  `principal` matches their portfolio/worktree lanes. Evidence: decision 0003,
  Saul `roadmap.md`, Mimi charter.
- **Slack channel approval workflow** — draft channel creation requests;
  never create channels without owner approval. Evidence:
  `.ai/_config/security-policy.md`.

## Codebase best practices (verified 2026-07-15)

- **Contract branch pattern** — `proj/<project-slug>/<ctr-agent-id>/<task-slug>`.
  Evidence: `.ai/_config/repositories.yaml`, decision 0003.
- **Contractor onboarding** — `.ai/ONBOARDING.md` parallel to
  `.ai/INITIALIZE.md`; persona gate required. Evidence: `.ai/ONBOARDING.md`.
- **Drive memory mirror** — per-agent memory at `.ai/agents/<name>/memory/`;
  sync via extended `scripts/agent-sync-drive`. Evidence:
  `.ai/_config/sync-policy.md`.
