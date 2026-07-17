# Subagent invocation test — mimi-dispatcher

Status: **artifact valid; live invocation BLOCKED in this session** (two
paths attempted, both failed for environmental reasons — recorded per the
contract's "post BLOCKED, do not claim it works" rule).

## Attempt 1 — headless CLI

```
$ claude -p "Delegate this to the mimi-dispatcher subagent..." 
Invalid API key · Please run /login
```

The `/opt/homebrew/bin/claude` CLI (1.0.98) is not authenticated for
headless API use on this machine (the interactive app session uses separate
auth). CLI 1.0.98 also predates the `--agent` flag.

## Attempt 2 — in-session Agent tool

```
Agent(subagent_type: "mimi-dispatcher") →
Error: Agent type 'mimi-dispatcher' not found. Available agents: claude,
claude-code-guide, Explore, general-purpose, Plan, statusline-setup
```

Claude Code snapshots `.claude/agents/` at session start; a subagent file
created mid-session is not loadable until a fresh session.

## What IS verified this session

- Frontmatter parses; `name: mimi-dispatcher`, description, `memory:
  project`, tools allowlist all present and spec-shaped (python check, OK).
- `.claude/settings.json` hooks execute correctly (force-push guard tested
  with live sample payloads: blocks `--force`/`-f`, passes normal pushes).

## Reproduction for reviewers (fresh session in this repo)

1. `claude` (interactive) → `/agents` → confirm `mimi-dispatcher` listed.
2. Prompt: "Use the mimi-dispatcher subagent to state its name, persona,
   and dispatch-discipline rules 3 and 5." → paste transcript here and
   flip this file's status to VERIFIED with the session date.

## Skills discovery caveat (flagged for Saul/Sai review)

The three SKILL.md files are nested per the contract's layout
(`.claude/skills/mimi-dispatcher/<skill>/SKILL.md`). Claude Code's
documented discovery is `.claude/skills/<skill-name>/SKILL.md` (one
level); whether nested skills load is version-dependent and was NOT
verifiable this session (fresh session required). If a fresh session does
not list them, the fix is to flatten to
`.claude/skills/<skill-name>/SKILL.md` — content is layout-independent.
