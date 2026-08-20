# Plan — Fresh Cloud Agent discovery for PR 70 skills

- Task-ID: `20260820-0023-lauren-skills-fresh-cloud-cursor-cloud`
- Intake: `.ai/runs/20260820-0023-lauren-skills-fresh-cloud-cursor-cloud/01_intake/output/intake.md`
- Playbook: pstack `bug-fix.md` (own the task; ship the smallest change the evidence justifies)
- Decision to create: `0006-lauren-mode-fresh-cloud-discovery`

## Current behavior

PR 70 is on `Dezocode/Sai:main` (`8a30202`). Project skill is `.cursor/skills/lauren-mode/` with slash `/lauren-mode` and `disable-model-invocation: true`.

A fresh mobile Cloud Agent on the same personal environment reused snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0` (`gitSetup: reuse`, `branchName: null`). That snapshot predates the merge, so the working tree has no lauren files. The user typed `/lauren mode` (space). The agent concluded the skill was never added.

## Desired behavior

When the checkout **includes** this commit (or PR 70 plus this follow-up):

- `/lauren` and `/lauren-mode` both attach the Custom Mode.
- A prose ask ("lauren mode", "skills from pr70") can attach without Option+Enter (mobile has no pin chord).
- An always-on rule names the paths and forbids "files missing" without `git fetch origin main`.

When the checkout is an **older snapshot**, no in-repo file can appear until git moves. Docs must say that. Operators start a **new** agent on `main` at/after this commit, or fetch `origin/main` in that VM. We do not commit `.cursor/environment.json` to force a fetch (0005). Draft environment builds do not become the boot snapshot, so we do not trigger one.

## File changes

| Path | Change | Why |
|---|---|---|
| `.cursor/skills/lauren/SKILL.md` | New alias Custom Mode `/lauren` | Mobile types `/lauren` or `/lauren mode`. Folder name is the slash. |
| `.cursor/skills/lauren-mode/SKILL.md` | `disable-model-invocation: false`; document `/lauren` | Description matching on "Lauren mode". |
| `.cursor/rules/lauren-mode.mdc` | Thin `alwaysApply` discovery | Agents with this commit do not claim absence without fetch. Does not inline pstack (0005). |
| `.cursor/skills/lauren-mode/references/environment.md` | gitSetup reuse evidence | Snapshot `bld-20260819-500928d1-…` hid post-merge skills. |
| `AGENTS.md` | Hyphen vs space; stale snapshot | Cloud operators. |
| `.ai/CONTEXT.md`, pstack index, conventions, architecture, repository-map | `/lauren` alias | Memory stays true. |
| `.ai/shared/memory/decisions/0006-…` | New | Discovery vs vendoring vs env file. |
| `.ai/shared/memory/decisions/0005-…` | Pointer to 0006 | Complement, do not rewrite 0005. |
| `.ai/runs/20260820-0023-…/` | Run artifacts | ICM trail. |

## Out of scope (evidence rejected or gated)

- Copy pstack into `.cursor/skills/` (0004).
- Duplicate the skill into `.agents/skills/` (this session already loaded `.cursor/skills/`; extra copy is unproven).
- Commit `.cursor/environment.json` or `propose-environment-json` without the live install/start scripts (would replace the personal env).
- `trigger-environment-build` (draft; does not become the boot snapshot).
- Force-push / merge / mark ready.

## Verification

- Confirm `origin/main` has PR 70 files; this branch adds `/lauren` + rule.
- Parse YAML frontmatter (`disable-model-invocation` not true on either skill).
- `python3 -m json.tool` on edited JSON.
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit` on the new range
- `scripts/verify-merge-handoff origin/main..HEAD`
- Disclose: this VM cannot restage the user's other agent. A **new** Cloud Agent after merge of this PR is the matching-surface proof. Snapshot reuse can still hide the files until that agent checks out a SHA that contains them.

## Risks and rollback

- Two project Custom Modes (`/lauren`, `/lauren-mode`) plus plugin `/poteto-mode`. Intentional aliases.
- Model invocation on a mode skill may auto-attach more often. Acceptable for mobile.
- Rollback: revert the branch / close the unmerged PR.

## Review gates

No hard security-policy gates. PLAN report is the gate. PR stays draft.
