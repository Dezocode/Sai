# Intake — 20260714-0418-sai-agent-framework-cursor-cloud-30d8

## Requester and requested outcome

- **Requester:** dezocode (Slack `U0BHYH0NMCY`), via the SAI Shared Cursor
  Agent Operating Prompt delivered to a Cursor cloud agent, consistent with
  the requests posted in #agentupdates on 2026-07-13.
- **Requested outcome:** set up the environment for dezocode's
  GitHub/Slack/Google Drive coordination; plan the repository structure
  according to arXiv:2603.16021 (ICM); establish a CEO agent that manages
  the project for co-founders dezocode and monaecode; prepare the framework
  for two subordinate Cursor agents acting as each co-founder's secretary.

## Repository verification (command output evidence)

- `git remote -v` → `origin https://github.com/dezocode/sai` (fetch/push).
- `gh repo view dezocode/sai` → `isFork: false`, `parent: null`,
  default branch `main`, owner `Dezocode`.
- `gh repo view monaecode/sai` → `isFork: true`,
  `parent: Dezocode/Sai`, default branch `main`.
- `git status` → clean on `main` at `34827e7`
  ("Merge pull request #1 from monaecode/main").
- Worktree: isolated cloud-agent VM at a non-synced path.
- Existing content: `README.md`, `Team.md` only. No `.ai/`, `.cursor/`,
  hooks, or scripts existed (checked before creating anything).

## Constraints and acceptance criteria

- New files only; do not modify `README.md` or `Team.md`.
- Structure must match the operating prompt's required filesystem
  architecture and ICM principles (one stage one job, Markdown/JSON
  interfaces, layered context, review gates, provenance).
- No secrets in any committed file.
- Slack reporting per the contract; queue if unavailable.
- Drive sync recorded honestly (`pending` — no credentials in this VM).

## Risks

- Slack MCP delivery from this environment failed silently on first attempts
  (recorded in `.ai/shared/memory/known-issues.md`); events are mirrored to
  `events.jsonl` and the delivery state is disclosed in the handoff.
- No other agent claims these paths (only other remote branch is
  `cursor/cloud-env-setup-532b`, which does not overlap).
