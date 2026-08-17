# Cursor and runtimes
Project-enabled Cursor plugins, SAI Cursor rules, and Layer 0 routers for Claude Code, Codex, OpenClaw, and Cloud Agents select the correct profile without mixing runtime inventories.
## Sub-features
- `cursor-settings` `.cursor/settings.json` `plugins.pstack.enabled: true` (cloud + local `/` commands).
- `pstack-index` `.ai/plugins/pstack/{manifest.json,README.md}` ICM record; Cursor does not load from `.ai/`.
- `plugins-index` `.ai/plugins/README.md` how slash commands actually load.
- `cursor-rules` `.cursor/rules/sai-coordination.mdc` always-on SAI protocol.
- `entry-agents` `AGENTS.md` Cloud/runtime notes + check commands.
- `entry-claude` `CLAUDE.md` Claude Code router.
- `entry-codex` `CODEX.md` Codex Desktop router.
- `entry-openclaw` `OPENCLAW.md` Gateway/VPS router + Alfred deploy two-step (`first-prompt-attach-contract.md`).
- `pstack-verify-skills` marketplace `/create-verification-skill` and `/maintain-verification-skill`; repo-local `/verify-sai` is `.cursor/skills/verify-sai/`.
- `decision-0004` `.ai/shared/memory/decisions/0004-cursor-project-plugins.md` project-scope plugins.
## How to get to it (user POV)
- Cursor: type `/` → pstack skills; attach `@<name>` for `.ai/agents/<name>/`.
- Claude Code: read `CLAUDE.md` then `AGENT.md`.
- Codex: `CODEX.md`. OpenClaw: `OPENCLAW.md` then Alfred first message.
- Cloud: new agent on a commit containing `.cursor/settings.json`.
## Driving it with verify-sai
Preconditions: repo root.
- **Settings.** `python3 -m json.tool .cursor/settings.json` contains `"pstack"`.
- **Index.** `python3 -m json.tool .ai/plugins/pstack/manifest.json`; `grep -q create-verification-skill .ai/plugins/pstack/README.md`
- **Routers.** `test -f AGENTS.md -a -f CLAUDE.md -a -f CODEX.md -a -f OPENCLAW.md -a -f .cursor/rules/sai-coordination.mdc`
- **Proof.** `go run ./cmd/sai-verify relevant --path .cursor/settings.json --tool Read` lists `cursor-runtimes`.
## Gotchas
- Do not vendor pstack skills into `.cursor/skills/` (duplicate `/` names). `verify-sai` is a project verification skill, not a pstack clone.
- User-scoped `/add-plugin` does not reach Cloud Agent VMs.
- Slack bots are not registered agents unless in `registry.json`.
