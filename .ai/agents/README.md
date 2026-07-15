# SAI Agent Registry and Profiles

This directory holds role charters, the agent registry, and one folder per
initialized agent. It implements Layer 1 of the ICM workspace (see
`.ai/CONTEXT.md`).

Multi-runtime adapters: `.ai/shared/references/agent-runtimes.md` (decision
`0002-multi-runtime-agent-adapters.md`). **One registry row per agent**;
runtime suites live under `runtimes/{cursor,claude,codex}/`.

## Layout

```
.ai/agents/
  README.md              <- this file
  registry.json          <- roster of all initialized agents
  _roles/                <- charter templates (not agent profiles)
    ceo/CHARTER.md
    secretary-dezocode/CHARTER.md
    secretary-monaecode/CHARTER.md
    portfolio-manager-monaecode/CHARTER.md
  automation-specs/      <- legacy specs; new profiles live in agent folders
  <agent-name>/          <- one folder per registered agent
    AGENT.md             <- identity card (runtime-neutral; load first)
    skills.md            <- role-specific skills + best practices
    tools.json           <- manifest (primary_runtime, canonical_capabilities_path)
    hooks.json           <- git hooks, rules, automation triggers
    automation/profile.md <- legacy alias (see runtimes/<suite>/automation/)
    runtimes/
      README.md
      cursor/            <- Cursor Desktop / Cloud suite
      claude/            <- Claude Code CLI suite
      codex/             <- OpenAI Codex Desktop suite (stub until live init)
```

## @agentname convention (Cursor)

Each registered agent has a folder named after their **granted name**
(lowercase, hyphenated). In Cursor Desktop, type `@<agent-name>` to attach
that agent's complete profile to your session.

## Claude Code and Codex Desktop

- **Claude Code:** read repo-root `CLAUDE.md`, then `.ai/agents/<name>/AGENT.md`.
- **Codex Desktop:** read repo-root `CODEX.md`, then follow `INITIALIZE.md`.
- Survey capabilities only into `runtimes/<suite>/tools.json` for your runtime.

## Registering a new agent

1. Execute `.ai/INITIALIZE.md` in full (Phases 0–9).
2. Ask your principal for a **name** and **role title** (Phase 6).
3. Run `scripts/agent-scaffold --primary-runtime <cursor|claude|codex> …`.
4. Fill `skills.md` and runtime `tools.json` from Phase 5B survey.
5. Run `scripts/agent-automation-spec` into `runtimes/<suite>/automation/profile.md`.
6. Add registry entry with `primary_runtime`, `entry_points`, `folder`, etc.
7. Post introductions to #help-newagents and #agentupdates per Phase 8–9.

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
| `primary_runtime` | active only | `cursor-desktop`, `cursor-cloud-vm`, `claude-code-cli`, or `codex-desktop` |
| `entry_points` | active only | Map of runtime → how to invoke this agent |
| `automation` | yes | Real automation name or `delegated: <spec path>` |
