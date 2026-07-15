# SAI agent runtimes — canonical index (Layer 3)

> Indexed reference for multi-runtime agent adapters (decision
> `0002-multi-runtime-agent-adapters.md`). GitHub is canonical; Google Drive
> `#knowledgebase` mirrors `.ai/shared/` after verified SYNC only.

## Principle

| Concept | Canonical location | Never duplicate |
|---|---|---|
| Agent identity | `.ai/agents/<name>/AGENT.md` | Per runtime |
| Role charter | `.ai/agents/_roles/*/CHARTER.md` | Per runtime |
| Registry row | `.ai/agents/registry.json` | Second registry |
| Runtime capabilities | `.ai/agents/<name>/runtimes/<suite>/tools.json` | In Slack bot config |
| Runtime automation | `.ai/agents/<name>/runtimes/<suite>/automation/profile.md` | Fabricated UI |

## Runtime suites

| Suite folder | `primary_runtime` values | Layer 0 entry | Automation mechanism |
|---|---|---|---|
| `runtimes/cursor/` | `cursor-desktop`, `cursor-cloud-vm` | `.cursor/rules/sai-coordination.mdc` + `@<name>` | Cursor Automations UI |
| `runtimes/claude/` | `claude-code-cli` | `CLAUDE.md` | Claude Code scheduled tasks / MCP connectors |
| `runtimes/codex/` | `codex-desktop` | `CODEX.md` | Codex Desktop app (stub until live init) |

## Registry fields (active agents)

| Field | Required | Description |
|---|---|---|
| `primary_runtime` | yes (active) | One of the values in the table above |
| `entry_points` | yes (active) | Map of runtime label → human-readable invoke instructions |

## Agent folder layout

```
.ai/agents/<name>/
  AGENT.md                 # runtime-neutral identity (load first)
  skills.md                # role skills
  hooks.json               # git hooks, reporting, trigger truth table
  tools.json               # manifest: primary_runtime + canonical_capabilities_path
  automation/profile.md    # legacy alias → see runtimes/<suite>/automation/
  runtimes/
    README.md              # which suites this agent uses
    cursor/
      tools.json           # Cursor-verified capabilities
      automation/profile.md
    claude/
      tools.json           # Claude Code-verified capabilities
      automation/profile.md
    codex/
      README.md            # stub until codex-desktop init
```

## Initialization branches (`.ai/INITIALIZE.md`)

Phases 0–4 and 6–9 are **runtime-neutral**. Only Phase 5B and Phase 7 vary:

| Phase | Cursor default | Claude / Codex |
|---|---|---|
| 5B | `agent-verify-caps --environment cursor-cloud-vm` | `… --environment claude-code-cli` or `codex-desktop` |
| 7 | `agent-automation-spec` → `runtimes/cursor/automation/profile.md` | Runtime-specific spec; record real mechanism or `delegated:` |

**Hard rule:** never run `agent-verify-caps` against another agent's folder
unless `SAI_AGENT_ID` matches that agent (or `<agent_id>-*` prefix).

## Slack vs registered agents

| Integration | Is a registered SAI agent? |
|---|---|
| Cursor `@sai`, `@mimi` | Yes — loads `.ai/agents/<name>/` |
| Claude Code with repo + `CLAUDE.md` | Yes — when session adopts named profile |
| Anthropic `@Claude` Slack app | **No** — separate product; not in `registry.json` |
| ChatGPT Slack app | **No** |

Posts "Sent using @Claude" are **not** `[SAI]` protocol compliance by themselves.

## Drive `#knowledgebase` indexing

After merge to `main`, mirror paths (per `.ai/_config/sync-policy.md`):

- `SAI/repositories/dezocode-sai/memory/decisions/0002-*.md`
- `SAI/repositories/dezocode-sai/memory/references/agent-runtimes.md`
- Agent folders under `SAI/repositories/dezocode-sai/snapshots/<sha>/`

Record SYNC with checksum in `[SAI][SYNC]` events. Status `pending` when
`SAI_DRIVE_REMOTE` is unset.
