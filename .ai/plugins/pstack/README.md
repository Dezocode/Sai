# pstack (project-enabled Cursor plugin)

pstack is Lauren Tan's Cursor plugin for rigorous, parallelizable agent
workflows. SAI enables it at **project scope** so `/` command input works in
**local Cursor** and **Cloud Agent** sessions that clone this repo.

Upstream: [github.com/cursor/plugins/tree/main/pstack](https://github.com/cursor/plugins/tree/main/pstack)
Marketplace: [cursor.com/marketplace/cursor/pstack](https://cursor.com/marketplace/cursor/pstack)
License: MIT. Observed version: 0.14.0 (2026-08-13).

## Can we run it from command input in cloud and local?

Yes, after this repo's `.cursor/settings.json` is on the commit the session
is using:

1. Local: reload the window (or reopen the folder). Type `/` and choose
   `/poteto-mode` (or another pstack skill).
2. Cloud: start a **new** Cloud Agent on a commit that includes
   `.cursor/settings.json` with `plugins.pstack.enabled: true`. Type `/` in
   that agent's first message. This current session cannot hot-load a
   marketplace plugin mid-run.

Interactive equivalent on Desktop: `/add-plugin pstack` and choose
**project** scope (writes the same settings file). User scope only helps
that one account's Desktop/CLI.

## What `.ai/plugins/pstack/` is

An ICM index (`manifest.json` + this README). Cursor does **not** load
slash commands from `.ai/`. Do not copy the upstream skill tree here
expecting `/poteto-mode` to appear.

## Get started

1. `/setup-pstack` — pick models per role. It writes
   `~/.cursor/rules/pstack-models.mdc` on the local machine. That path does
   **not** apply in Cloud Agents. Shared cloud+local routing is committed
   at `.cursor/rules/pstack-models.mdc` (decision 0005). Re-run
   `/setup-pstack` and update that file when available model slugs change.
2. `/poteto-mode` — default pstack entry for any non-trivial task. Sticky
   across turns. `disable-model-invocation: true`, so type the slash
   command; the agent will not auto-enter it.
3. `/lauren-mode` — SAI project Custom Mode (`.cursor/skills/lauren-mode/`).
   Pin it in Cloud Agents with Option+Enter / Use as Mode. It does not
   replace the plugin. It adds the 2026-08-19 harness, Browser pane, and
   SDK notes. See decision `0005-lauren-mode-cloud-skills`.

## Command input (skills)

`/poteto-mode` routes to playbooks and other skills. Invoke these directly
when you want one:

| Command | When |
|---|---|
| `/lauren-mode` | SAI Cloud Custom Mode pin (project skill, not the plugin) |
| `/poteto-mode` | Default pstack entry for rigorous work |
| `/setup-pstack` | Choose models per role |
| `/how` | Walkthrough of how a subsystem works |
| `/why` | Why something was built this way |
| `/recall` | Rebuild recent context on a topic |
| `/blast-radius` | What else a small change could break |
| `/architect` | Settle types and module shape first |
| `/arena` | N parallel attempts, keep the best parts |
| `/swarm` | N parallel workers across slices |
| `/interrogate` | Multi-model review of a diff |
| `/tdd` | Failing test first, then the fix |
| `/unslop` | Remove AI writing tells |
| `/no-comments` | Strip comments before review |
| `/teach` | Understand a change, not just summarize it |
| `/reflect` | Capture a long-task recipe as a skill edit |
| `/automate-me` | Draft your own `-mode` skill |
| `/figure-it-out` | No bundled playbook fits |
| `/show-me-your-work` | Reviewable decision trail |
| `/create-verification-skill` | Generate a project-local verify skill |
| `/maintain-verification-skill` | Correct a drifted verify feature map |
| `/typescript-best-practices` | Type-system discipline in TypeScript |
| `/bro` | Restate the last message in plain language |
| `/technical-writing` | Layered doc standard |

Subagents (spawn from a parent agent, not `/`): `poteto-agent`,
`Comment Sicko`.

## Other runtimes (Claude Code, Codex, OpenClaw)

Those runtimes do not load Cursor marketplace plugins. They can still read
this index. To follow pstack methodology there, fetch the MIT-licensed
skills from the upstream repo at the version in `manifest.json` — do not
expect `/poteto-mode` in their command palettes unless that runtime adds
its own skill loader.

## Companion (not enabled)

pstack's README notes that `/deslop`, `control-cli`, and `control-ui` ship
in `cursor-team-kit`. That plugin is **not** project-enabled here unless a
later task adds it to `.cursor/settings.json`.
