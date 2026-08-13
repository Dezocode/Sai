# Intake — enable pstack for cloud and local Cursor sessions

- Task-ID: `20260813-0113-pstack-plugin-install-cursor-cloud`
- Agent: `cursor-cloud` (unnamed Cloud Agent; not in `registry.json`)
- Requester: dezocode (`U0BHYH0NMCY`)
- Source: Cursor Cloud Agent run `bc-019ff8a9-0aaa-75f8-806e-b3d9c5f810de` (mobile), prompt: `/add-plugin pstack Install plugin into .ai too make sure it's executable from command input during cloud and local sessions can we do this`
- Date (UTC): 2026-08-13

## Requested outcome

1. Install the Cursor Marketplace plugin **pstack** (slash command `/add-plugin pstack`).
2. Also record/install it under `.ai/` so SAI agents can see it.
3. Make pstack skills invocable from **command input** (`/` picker) in both **Cloud Agent** and **local Cursor** sessions.

## Repository facts (command-backed)

| Fact | Value | Evidence |
|---|---|---|
| Toplevel | `/workspace` | `git rev-parse --show-toplevel` |
| Origin | `github.com/Dezocode/Sai` (canonical, not a fork) | `git remote -v`; `gh repo view` `isFork: false` |
| Default branch | `main` | `gh repo view` `defaultBranchRef.name` |
| Start SHA | `d07935113ee565281a91f98103832bab0fbe27db` | `git rev-parse HEAD` |
| Start branch | `main` (clean) | `git status`: up to date with `origin/main`, nothing to commit |
| Task branch | `cursor/pstack-plugin-install-10de` | created from `main` at `d079351` |

## Constraints

- Cursor loads marketplace plugins from committed `.cursor/settings.json` (`plugins.<name>.enabled`). It does **not** load plugins, skills, or slash commands from `.ai/`.
- User-scoped `/add-plugin` on a laptop does not reliably reach Cloud Agent VMs.
- `/setup-pstack` writes `~/.cursor/rules/pstack-models.mdc`, which Cloud Agents do not apply. Shared model routing must live in `.cursor/rules/` if desired (out of scope unless requested).
- Do not vendor the full upstream pstack tree into `.ai/` expecting slash-command registration.
- Hard security gates in `.ai/_config/security-policy.md` do not apply (no secrets, force-push, access, or production deploy).
- Overlap check: other `in_progress`/`active` runs do not claim `.cursor/settings.json`, `.ai/plugins/`, `AGENTS.md`, or `.ai/CONTEXT.md`.

## Acceptance criteria

- `.cursor/settings.json` enables `pstack` at project scope.
- `.ai/plugins/` indexes pstack (manifest + README) so ICM agents know it exists and how to invoke it.
- `AGENTS.md` and Layer 0 map tell Cloud/local agents to type `/poteto-mode` (and related skills) in command input.
- A **new** Cloud Agent rooted on this commit should resolve pstack skills in project scope. This current session cannot hot-load marketplace plugins mid-run.

## Existing uncommitted changes

None. Working tree was clean at intake.
