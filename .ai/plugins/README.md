# Cursor plugins (ICM index)

This folder is the **Layer 3 index** of Cursor Marketplace plugins this
repository enables at **project scope**. It is documentation for SAI agents
across runtimes. It is **not** a Cursor plugin loader.

## How slash commands actually load

Cursor registers `/` skills from:

1. Built-in product skills (`/add-plugin`, `/create-skill`, `/loop`, …)
2. Marketplace plugins enabled in committed `.cursor/settings.json`
3. Project skills under `.cursor/skills/` and `.agents/skills/`
4. Project commands under `.cursor/commands/`

Cursor does **not** scan `.ai/plugins/` for `plugin.json`, `SKILL.md`, or
slash commands. Putting a plugin tree here will not make `/poteto-mode`
appear in command input.

Cloud Agents and local Cursor sessions both read `.cursor/settings.json`
from the repo. User-scoped `/add-plugin` on one laptop does not reliably
reach Cloud Agent VMs.

## Enabled plugins

| Plugin | Marketplace | Project enablement | ICM record |
|---|---|---|---|
| pstack | [cursor.com/marketplace/cursor/pstack](https://cursor.com/marketplace/cursor/pstack) | `.cursor/settings.json` → `plugins.pstack.enabled` | [`pstack/`](pstack/) |

## Adding another plugin

1. Enable it in `.cursor/settings.json` (`plugins.<slug>.enabled: true`).
   Preserve unrelated keys.
2. Add `.ai/plugins/<slug>/manifest.json` and `README.md`.
3. List it in this table.
4. Do **not** copy the upstream skill tree into `.cursor/skills/` (duplicate
   `/` names) or into `.ai/` expecting Cursor to load it.
5. Do **not** put plugins in `environment.json` — that schema has no
   `plugins` key.

See decision `0004-cursor-project-plugins`.
