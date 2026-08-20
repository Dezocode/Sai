# 0006 — Lauren mode discovery for fresh Cloud Agents

- Date: 2026-08-20
- Task-ID: 20260820-0023-lauren-skills-fresh-cloud-cursor-cloud
- Status: accepted
- Approver: dezocode (asked to fix PR 70 skills in a fresh Cursor Cloud Agent)

## Decision

Keep the PR 70 Custom Mode at `.cursor/skills/lauren-mode/`. Add a short alias at `.cursor/skills/lauren/` (`/lauren`) so mobile command input matches `/lauren` and `/lauren mode` (space). Allow model invocation on `/lauren-mode` so a prose ask can attach when the files are in the tree. Add a thin always-apply rule `.cursor/rules/lauren-mode.mdc` that names the paths and requires `git fetch origin main` before claiming the skill is absent. Do not vendor pstack. Do not commit `.cursor/environment.json`.

## Context

PR 70 merged to `Dezocode/Sai:main` as `8a30202` at 2026-08-20T00:12:17Z. A fresh mobile Cloud Agent (`bc-01a01c89-0d79-709c-aacf-ba84185f18aa`) started at 00:19:04Z, after that merge, and concluded "No lauren files in the tree yet." Runtime facts:

- `branchName` was null
- Same personal env `6f2ece39-800a-11f1-ba66-0e7d0216e441`
- `gitSetup: reuse` of snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0` (predates the merge)
- Install exited 0 immediately
- The user typed `/lauren mode` with a space
- PR 70 set `disable-model-invocation: true`, so description matching could not attach even when files exist

This parent session loaded `.cursor/skills/lauren-mode/` from a checkout that includes PR 70. Cloud Agents do scan that directory when the working tree has the files.

## Alternatives considered

- **Commit `.cursor/environment.json` with a fetch-on-start script** — rejected. Decision 0005. A repo file would replace the personal dashboard environment. Live install/start scripts are owner-restricted, so a proposal would guess.
- **Trigger a draft environment build / snapshot this VM** — rejected for this change. Draft builds do not become the boot snapshot. 0005 already said not to snapshot for skills-only work.
- **Copy the skill into `.agents/skills/`** — rejected. Unproven extra copy. This session already loaded `.cursor/skills/`.
- **Always-apply rule that inlines poteto-mode** — still rejected (0005). This record adds a short discovery pointer only.
- **Leave `disable-model-invocation: true` and only document the hyphen** — rejected. Mobile has no Option+Enter pin. Prose and `/lauren mode` must attach when files are present.

## Rationale

Two bugs stacked. Slash identity (`/lauren-mode` vs `/lauren` vs a space) is a project-skill problem we can fix in git. Snapshot reuse of a pre-merge tree is a Cloud gitSetup problem. In-repo files cannot appear in a checkout that does not contain them. Discovery plus docs is the smallest change the evidence justifies. Operators start a new agent on latest `main`, or fetch `origin/main` in that VM.

## Consequences

- `/lauren` and `/lauren-mode` are both project Custom Modes. `/poteto-mode` remains the marketplace skill.
- Model invocation may auto-attach Lauren mode from a description. Acceptable for Cloud mobile.
- Agents on a SHA that includes this commit will see `.cursor/rules/lauren-mode.mdc` even if they forget to type a slash.
- Agents still on snapshot `bld-20260819-500928d1-…` without fetching `origin/main` will still lack the files. Tell them to fetch or start from latest `main`.

## Complements

0005 (Custom Mode wrapper, no env file). Does not reopen vendoring pstack (0004).
