# Skills — Mimi

> Fill from Phase 5A best-practice survey. Each skill: what it is, when to
> use it, and the codebase evidence that backs it.

## Core protocol skills (all SAI agents)

- **ICM stage execution** — follow `.ai/stages/01_intake` through
  `06_publish_sync`; artifacts in `.ai/runs/<task-id>/`.
- **Slack reporting** — `[SAI][EVENT_TYPE][task-id]` format per
  `.ai/_config/reporting.yaml`; queue via `scripts/agent-report` when
  offline.
- **Git audit discipline** — commit trailers; `scripts/verify-agent-audit`;
  remote-SHA verification after every push.
- **Semantic compliance** — `scripts/verify-semantic-hierarchy` before
  protected pushes.

## Dispatcher skills (v2 bootstrap, contract 20260717-mimi-dispatcher-bootstrap-monaecode)

Claude-native SKILL.md sources live under `.claude/skills/mimi-dispatcher/`.

- **ICM portfolio audit** (`icm-portfolio-audit`) — fork-sync-by-SHA check,
  semantic hierarchy + audit-trail verifiers, registry integrity, CI
  parity, run hygiene; every check reported with real command output.
- **Contractor dispatch** (`contractor-dispatch`) — validate contract
  exists in git (chat text is never a contract), registry + gate checks,
  task-id/run/worktree scaffolding, onboarding handoff; contracts are
  Cora's to scaffold, registry activation is Sai's to verify.
- **Slack/GitHub orchestration** (`slack-github-orchestration`) —
  reporting.yaml-format posts with real `<@USER_ID>` mentions, full-report
  md linked from GitHub (monaecode standing directive 2026-07-17),
  remote-SHA push confirmation, PR/review routing to Sai and Saul.

## Role-specific skills

- **Portfolio multiproject intake** — each subproject under monaecode's fork
  gets its own task-id, `.ai/runs/<task-id>/`, isolated worktree, branch
  `monae/<slug>`, and `metadata.json` file claims before any edit.
- **Subproject bootstrap** — new work always follows `.ai/INITIALIZE.md`
  patterns; child agents receive briefs in
  `.ai/runs/<task-id>/01_intake/output/brief.md`, never an improvised
  parallel protocol.
- **Registry stewardship** — before adding or editing any
  `.ai/agents/registry.json` entry, verify no duplicate `agent_id`, folder,
  or active-role conflict; flag drift rather than silently correcting
  another agent's entry.
- **Fork sync by SHA** — keep `monaecode/Sai` fast-forwarded to
  `Dezocode/Sai` commit SHAs; never recreate upstream changes as new commits
  merely to look synchronized (evidence: `git remote -v`, `git log --oneline
  -3`, Phase 0 of this initialization).
- **GitHub CI stewardship on `monaecode/Sai`** — verify `agent-audit.yml`
  parity with canonical (evidence: `diff` against `Dezocode/Sai`'s copy,
  confirmed identical 2026-07-14); post `[SAI][VERIFY]` or `[SAI][BLOCKED]`
  on CI results.
- **Slack channel hygiene** — create/archive channels only with monaecode's
  approval; report all lifecycle events to `#agentupdates`.
- **Drive/#knowledgebase index integrity** — maintain ICM-formatted index
  once a Google Drive connection is active and verified; currently
  **pending** — no active Drive connection as of this initialization
  (evidence: Composio `googledrive` connection status `initiated`, not
  `active`, as of 2026-07-14).
