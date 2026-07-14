# SAI Agent Registry and Profiles

This directory holds role charters, the agent registry, and one folder per
initialized agent. It implements Layer 1 of the ICM workspace (see
`.ai/CONTEXT.md`).

## Layout

```
.ai/agents/
  README.md              <- this file
  registry.json          <- roster of all initialized agents
  _roles/                <- charter templates (not agent profiles)
    ceo/CHARTER.md
    secretary-dezocode/CHARTER.md
    secretary-monaecode/CHARTER.md
  automation-specs/      <- legacy specs; new profiles live in agent folders
  <agent-name>/          <- one folder per registered agent
    AGENT.md             <- identity card (load first)
    skills.md            <- role-specific skills + best practices
    tools.json           <- verified Cursor tools/MCP/integrations
    hooks.json           <- git hooks, rules, automation triggers
    automation/profile.md <- paste-ready Cursor Automations UI profile
```

## @agentname convention

Each registered agent has a folder named after their **granted name**
(lowercase, hyphenated). In Cursor Desktop, type `@<agent-name>` to attach
that agent's complete profile to your session. On mobile/web, open
`https://github.com/Dezocode/Sai/tree/main/.ai/agents/<agent-name>/`.

The `sai-coordination` Cursor rule tells any agent that receives an attached
folder to load `AGENT.md` first and respect that agent's declared scope.

## Registering a new agent

1. Execute `.ai/INITIALIZE.md` in full (Phases 0–9).
2. Ask your principal for a **name** and **role title** (Phase 6).
3. Run `scripts/agent-scaffold` to create your folder.
4. Fill `skills.md`, `tools.json`, and `hooks.json` from Phase 5 survey.
5. Run `scripts/agent-automation-spec` to generate `automation/profile.md`.
6. Add your entry to `registry.json` with `folder`, `name`, `role_title`,
   `purpose`, and `automation` fields.
7. Post introductions to #help-newagents and #agentupdates per Phase 8–9.

Provisional agents (not yet named) use their `agent_id` as the folder name
and rename when named.

## registry.json fields

| Field | Required | Description |
|---|---|---|
| `agent_id` | yes | Charter prefix + unique suffix |
| `name` | active only | Granted by principal |
| `role_title` | active only | Granted by principal |
| `purpose` | active only | One paragraph, confirmed by principal |
| `folder` | yes | Repo-relative path, e.g. `.ai/agents/my-name/` |
| `charter` | yes | Path to role charter under `_roles/` |
| `principal` | yes | Human the agent works under |
| `status` | yes | `provisional`, `active`, or `retired` |
| `automation` | yes | Real automation name or `delegated: <spec path>` |
