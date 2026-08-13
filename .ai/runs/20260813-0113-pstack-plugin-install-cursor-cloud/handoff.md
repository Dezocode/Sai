# Handoff — pstack project plugin

- Task-ID: `20260813-0113-pstack-plugin-install-cursor-cloud`
- Agent: `cursor-cloud`
- Principal: dezocode (`U0BHYH0NMCY`)
- Branch: `cursor/pstack-plugin-install-10de`
- PR: https://github.com/Dezocode/Sai/pull/57 (draft)
- First commit: `3dbd9514ba36311398f5144652cc8ed698c65c20`

## Requested outcome

dezocode asked to `/add-plugin pstack`, install it into `.ai`, and make it
executable from command input in cloud and local sessions.

## What was done

- Enabled pstack at project scope in `.cursor/settings.json`
  (`plugins.pstack.enabled: true`). That is the Cursor-supported equivalent
  of `/add-plugin pstack` with **project** scope. Cloud Agents and local
  Cursor both read this file.
- Indexed the plugin under `.ai/plugins/pstack/` (manifest + README) so ICM
  agents can see it. `.ai/` does not load slash commands.
- Recorded decision `0004-cursor-project-plugins`.
- Pointed `AGENTS.md`, Layer 0 map, runtime index, conventions, architecture,
  and repository-map at the new paths.
- Pushed branch; remote SHA matched local HEAD `3dbd951` after first push.
- Draft PR #57 opened against `Dezocode/Sai:main`.
- Local ICM checks passed: `verify-semantic-hierarchy`, `verify-agent-audit`,
  `verify-merge-handoff`, `verify-agent-setup`, JSON parse of new files.
- GitHub Actions `icm-enforcement` passed on PR #57.

## What was not done (disclosed)

- This Cloud Agent session cannot hot-load marketplace plugins. `/poteto-mode`
  appears in command input only after a **new** Cloud Agent or a local
  window reload on a commit that includes `.cursor/settings.json`.
- `/setup-pstack` model routing was not committed (needs
  `.cursor/rules/pstack-models.mdc` for cloud).
- Upstream pstack skill tree was not vendored.
- Drive sync is pending (`SAI_DRIVE_REMOTE` unset).
- `SAI_SLACK_BOT_TOKEN` unset; Slack MCP delivered #agentupdates posts;
  `scripts/agent-report` events remain queued.

## Next safe action

1. Co-founder review of draft PR https://github.com/Dezocode/Sai/pull/57
2. After merge, start a **new** Cloud Agent (or reload local Cursor) and
   type `/` to confirm `/poteto-mode` and `/setup-pstack`.
3. Optionally run `/setup-pstack` and commit `.cursor/rules/pstack-models.mdc`
   if shared model routing is wanted.
4. Do not merge, force-push, or mark ready without co-founder authorization.
