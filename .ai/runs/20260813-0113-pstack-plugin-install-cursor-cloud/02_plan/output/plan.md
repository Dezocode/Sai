# Plan — project-scope pstack + `.ai/plugins` index

- Task-ID: `20260813-0113-pstack-plugin-install-cursor-cloud`
- Intake: `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/01_intake/output/intake.md`
- Decision to create: `0004-cursor-project-plugins`

## Current behavior

- No `.cursor/settings.json`. pstack is not project-enabled.
- This Cloud Agent VM's plugin cache has user-scoped global plugins (slack, continual-learning, bright-data, cursor-sdk, composio) and **does not** include pstack.
- `.ai/` has no plugin index. Cursor slash commands are not documented for SAI agents.

## Desired behavior

- Typing `/` in Agent chat (Desktop **and** Cloud) lists pstack skills (`/poteto-mode`, `/setup-pstack`, `/how`, `/why`, …) because the repo enables the marketplace plugin at **project** scope.
- `.ai/plugins/pstack/` is the ICM record: marketplace identity, slash-command list, cloud vs local notes. It does not pretend to be a Cursor plugin loader.

## File changes

| Path | Change | Why |
|---|---|---|
| `.cursor/settings.json` | Create with `plugins.pstack.enabled: true` | Official project-scope install; Cloud Agents and local Cursor both read this. Equivalent of `/add-plugin pstack` with project scope. |
| `.ai/plugins/README.md` | New index | Layer 3 map of Cursor plugins this repo enables. |
| `.ai/plugins/pstack/manifest.json` | New | Stable identity: slug, version, source, slash commands. |
| `.ai/plugins/pstack/README.md` | New | How to invoke from command input; what `.ai/` does and does not load. |
| `.ai/shared/memory/decisions/0004-cursor-project-plugins.md` | New | Record that slash commands come from `.cursor/settings.json`, not `.ai/`. |
| `.ai/CONTEXT.md` | Add `.ai/plugins/` to workspace map | Layer 0 must name the new folder. |
| `AGENTS.md` | Short Cloud/local note | Cloud Agents read AGENTS.md; tell them `/poteto-mode` is project-enabled. |
| `.ai/shared/references/agent-runtimes.md` | Pointer | Cursor runtime suite includes project plugins. |
| `.ai/shared/memory/conventions.md` | Convention | How to add the next plugin without vendoring into `.ai/`. |
| `.ai/runs/20260813-0113-pstack-plugin-install-cursor-cloud/` | Run artifacts | ICM audit trail. |

## Out of scope

- Vendoring the full `github.com/cursor/plugins/pstack` tree (stale copies; does not register `/` commands).
- Committing `.cursor/rules/pstack-models.mdc` (model routing; needs `/setup-pstack` or explicit co-founder model picks).
- Installing `cursor-team-kit` (optional companion; not requested).
- Copying benny automations.
- Team-dashboard Required/Default-On plugin mode (needs org admin UI).

## Verification

- `python3 -m json.tool` on new JSON files.
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit` on the new commit range
- `scripts/verify-merge-handoff origin/main..HEAD`
- Confirm `.cursor/settings.json` parses and contains `plugins.pstack.enabled === true`
- Disclose: this session cannot prove the `/` picker lists pstack; that requires a **new** Cloud Agent or a local window reload on this commit.

## Risks and rollback

- First Cloud Agent after enabling a project plugin has historically sometimes booted without plugins; workaround is a second session. Documented in the plugin README.
- Duplicate slash commands if someone later also copies pstack skills into `.cursor/skills/` — convention forbids that.
- Rollback: revert the branch / close the unmerged PR. No production impact.

## Review gates

None of the hard gates in `.ai/_config/security-policy.md`. PLAN report is the gate; proceed unless a co-founder objects. PR remains draft until a co-founder marks it ready.
