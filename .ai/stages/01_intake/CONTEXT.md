# Stage 01 — Intake

## Purpose

Capture who is asking for what, verify the repository context, and produce a
single intake record that every later stage can trust without re-deriving it.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 3 | `.ai/_config/repositories.yaml` | Governed repos, fork topology, branch naming |
| 3 | `.ai/_config/reporting.yaml` | Reporting contract |
| 3 | `.ai/_config/security-policy.md` | Review gates that may apply |
| 4 | The request itself | Slack message, issue, PR, or direct instruction |

## Process

1. Identify the requesting user and the exact requested outcome.
2. Confirm, with command output: current repository, remote URLs, default
   branch, fork relationship, current branch and commit, worktree path, and
   clean/dirty state (`git remote -v`, `git status`, `gh repo view`).
3. Read repository-local instructions (`.cursor/rules/`, `.ai/CONTEXT.md`)
   before planning.
4. Note existing uncommitted human or agent changes that must be preserved.
5. Record constraints, acceptance criteria, dependencies, and security or
   compatibility risks.
6. Allocate the task ID: `YYYYMMDD-HHMM-<issue-or-purpose>-<agent-id>` (UTC),
   create `.ai/runs/<task-id>/` with `metadata.json`, and start
   `events.jsonl`.

## Outputs

- `.ai/runs/<task-id>/01_intake/output/intake.md` — the intake record.
- `.ai/runs/<task-id>/01_intake/output/brief.md` — only when the CEO agent
  delegates to a secretary (see the CEO charter's delegation contract).
- `.ai/runs/<task-id>/metadata.json` — task ID, agent, repository, branch,
  claimed files, status.
- INTAKE (or combined INTAKE+PLAN) report posted to #agentupdates **before
  material edits**.

## Verification

`metadata.json` parses as JSON; every repository fact in `intake.md` is
backed by quoted command output.

## Human review gate

None by default. If the request itself is ambiguous, conflicts with another
active run, or touches a hard gate in the security policy, stop here and
post BLOCKED.

## Rollback

Delete `.ai/runs/<task-id>/` if the task is abandoned before planning, and
post a HANDOFF report noting abandonment.

## Provenance

`intake.md` must name the requester, the source of the request (link or
quote), and the verification commands used.
