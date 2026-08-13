# Handoff — pstack project plugin

- Task-ID: `20260813-0113-pstack-plugin-install-cursor-cloud`
- Agent: `cursor-cloud`
- Branch: `cursor/pstack-plugin-install-10de`
- Status: implementation on branch; verification and PR follow in this run

## Requested outcome

dezocode asked to `/add-plugin pstack`, install it into `.ai`, and make it
executable from command input in cloud and local sessions.

## What was done

- Enabled pstack at project scope in `.cursor/settings.json`
  (`plugins.pstack.enabled: true`). That is the Cursor-supported equivalent
  of `/add-plugin pstack` with **project** scope, and it is what Cloud
  Agents and local Cursor both read.
- Indexed the plugin under `.ai/plugins/pstack/` (manifest + README) so ICM
  agents can see it. `.ai/` does not load slash commands.
- Recorded decision `0004-cursor-project-plugins`.
- Pointed `AGENTS.md`, Layer 0 map, runtime index, conventions, architecture,
  and repository-map at the new paths.

## What was not done (disclosed)

- This Cloud Agent session cannot hot-load marketplace plugins. `/poteto-mode`
  appears in command input only after a **new** Cloud Agent or a local
  window reload on a commit that includes `.cursor/settings.json`.
- `/setup-pstack` model routing was not committed (would need
  `.cursor/rules/pstack-models.mdc` for cloud).
- Upstream pstack skill tree was not vendored.
- Drive sync is pending (`SAI_DRIVE_REMOTE` unset).
- `SAI_SLACK_BOT_TOKEN` unset; Slack MCP used for #agentupdates; 
  `scripts/agent-report` events remain queued.

## Next safe action

1. Human review of the draft PR against `Dezocode/Sai:main`.
2. After merge, start a **new** Cloud Agent (or reload local Cursor) and
   type `/` to confirm `/poteto-mode` and `/setup-pstack`.
3. Optionally run `/setup-pstack` and commit `.cursor/rules/pstack-models.mdc`
   if shared model routing is wanted.
4. Do not merge without co-founder authorization.
