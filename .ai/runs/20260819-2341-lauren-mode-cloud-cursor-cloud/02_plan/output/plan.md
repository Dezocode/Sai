# Plan — Lauren mode Custom Mode + 08-19-26 cloud harness

- Task-ID: `20260819-2341-lauren-mode-cloud-cursor-cloud`
- Intake: `.ai/runs/20260819-2341-lauren-mode-cloud-cursor-cloud/01_intake/output/intake.md`
- Decision to create: `0005-lauren-mode-cloud-skills`

## Current behavior

Cloud Agents load pstack from `.cursor/settings.json`. They do not get a project Custom Mode named Lauren, they do not get committed pstack model routing, and AGENTS.md does not tell them how to use the 2026-08-19 harness (subscriptions, `/goal`, VM-isolated subagents, steering, Browser pane) or how to launch the same setup via `@cursor/sdk`.

## Desired behavior

- Typing `/lauren-mode` (or pinning it as a Custom Mode) keeps SAI Cloud Agents on Lauren Tan's pstack playbook plus the 08-19-26 cloud harness.
- `.cursor/rules/pstack-models.mdc` applies in Cloud and local because it is committed, using only Task slugs confirmed on this VM.
- AGENTS.md and the pstack ICM index tell operators how to pin the mode, when to use `/goal`, cloud VM subagents, `/subscribe`, `@Browser`, and the personal environment dashboard. They do not add a repo `environment.json`.

## File changes

| Path | Change | Why |
|---|---|---|
| `.cursor/skills/lauren-mode/SKILL.md` | New Custom Mode skill | Project-level `/` skill Cloud Agents load. Does not copy pstack. |
| `.cursor/skills/lauren-mode/references/harness.md` | 08-19-26 playbook | Goal, subscriptions, VM subagents, steering. Loaded on demand. |
| `.cursor/skills/lauren-mode/references/browser-pane.md` | Browser pane | `@Browser`, built-in Browser subagent, `computerUse`, Chrome path. |
| `.cursor/skills/lauren-mode/references/sdk-cloud.md` | SDK launch | `@cursor/sdk` `cloud.repos` so launched agents inherit project skills. |
| `.cursor/skills/lauren-mode/references/environment.md` | Live env facts | Personal DB-managed environment IDs. Warn against committing `environment.json`. |
| `.cursor/rules/pstack-models.mdc` | New alwaysApply rule | Cloud-safe pstack role models (deferred in 0004). |
| `.ai/shared/memory/decisions/0005-lauren-mode-cloud-skills.md` | New | Project Custom Mode wrapper vs vendoring pstack. |
| `AGENTS.md` | Cloud notes | How to pin `/lauren-mode`; harness; env dashboard. |
| `.ai/plugins/README.md`, `.ai/plugins/pstack/README.md`, `manifest.json` | Index | Point at `/lauren-mode` without claiming `.ai/` loads it. |
| `.ai/shared/memory/conventions.md`, `architecture.md`, `repository-map.md` | Memory | Skills vs plugins. |
| `.ai/shared/references/agent-runtimes.md` | Pointer | Cursor suite includes project skills. |
| `.ai/runs/20260819-2341-lauren-mode-cloud-cursor-cloud/` | Run artifacts | ICM trail. |

## Out of scope

- Copying the pstack skill tree into `.cursor/skills/` (decision 0004).
- Committing `.cursor/environment.json` (would override the personal dashboard env).
- Snapshot/rebuild of the Cloud Agent environment (skills load from git, not install).
- Installing `cursor-team-kit`.
- Full SAI agent initialization of this cloud worker.

## Verification

- `python3 -m json.tool` on new/edited JSON.
- YAML frontmatter parse of SKILL.md and pstack-models.mdc.
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit` on the new commit range
- `scripts/verify-merge-handoff origin/main..HEAD`
- Confirm Chrome exists on this VM (`/usr/bin/google-chrome`)
- Disclose: `/` picker and Custom Mode badge require a **new** Cloud Agent or Desktop reload on this commit.

## Risks and rollback

- Two Custom Modes (`/poteto-mode` from plugin, `/lauren-mode` from project) is intentional. Lauren-mode is the SAI cloud pin; poteto-mode stays the upstream skill.
- Model slugs in pstack-models.mdc can drift when Cursor renames models. Only detected slugs are written; `inherit-parent` and `auto` remain valid.
- Rollback: revert the branch / close the unmerged PR.

## Review gates

None of the hard gates in `.ai/_config/security-policy.md`. PLAN report is the gate. PR stays draft.
