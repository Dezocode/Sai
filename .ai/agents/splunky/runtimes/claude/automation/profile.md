# Claude Code automation profile — Splunky (ctr-code-splunky)

> **Primary runtime:** `claude-code-cli` on **monaecode/Sai**. This documents
> **session-driven** Claude Code / Claude Desktop work and optional **Claude
> scheduled tasks** after Phase 5B — **not** Cursor Automations UI. Splunky's
> optional Cursor entry is `@splunky` only; do not create a Cursor Scheduled
> automation as the primary runtime.
>
> Updated 2026-07-17 (Sai CEO) — replaces erroneous Cursor UI spec copied into
> this path during scaffold.

## Identity

| | |
|---|---|
| Agent name | Splunky |
| Role title | Splunk Clone Lead (PM, Design, Senior Engineering) |
| Agent ID | `ctr-code-splunky` (sessions use `SAI_AGENT_ID=ctr-code-splunky`) |
| Principal | monaecode (U0BGNS7F0T1) |
| Contract | `20260715-splunk-clone-monaecode` |
| Registry status | `provisional` — implementation NO-GO until ONBOARDING Phase 6 + Sai persona gate |
| Purpose | Lead isolated `splunk-clone/` prototype: SIEM-style monitoring, Splunk/competitor expertise, future SAI cybersecurity plugin manifest |

## Automation state

| Mechanism | Status | Evidence |
|---|---|---|
| Claude Code session (manual / principal-invoked) | **delegated** | `splunk-clone/CLAUDE.md`, `.claude/agents/splunky.md` |
| Claude scheduled tasks | **not configured** | No verified row in `runtimes/claude/tools.json`; complete Phase 5B first |
| Cursor Automations | **not primary** | Optional ad-hoc `@splunky` only — no scheduled Cursor automation required |
| Registry `automation` field | **delegated** | Points to this file until first verified scheduled task or owner confirms session-only |

## Invoke Splunky (canonical)

1. Open **`github.com/monaecode/Sai`** in Claude Code or Claude Desktop.
2. `cd splunk-clone` (product root; ICM agent mirror at `../.ai/agents/splunky/`).
3. Read, in order:
   - `CLAUDE.md` (this tree)
   - `../.ai/CONTEXT.md`
   - `../.ai/contracts/20260715-splunk-clone-monaecode/onboarding-prompt.md`
   - `.claude/agents/splunky.md` (subagent persona)
4. Use **`splunk-clone/.claude/settings.json`** permissions (provisional shell allowlist:
   `.ai/shared/references/contractor-provisional-shell-allowlist.json`). Do not broaden
   `Bash(git *)` / `Bash(gh *)` until `contract.json` `approved_capabilities[]` records
   owner approval and Phase 5B marks them `verified` in `runtimes/claude/tools.json`.
5. Marketplace / project skills (installed under `splunk-clone/.claude/skills/`):
   - `sai-icm-contract` — ICM runs, Task-ID, Slack templates, contract PR review
   - `splunk-siem-expertise` — Splunk/SIEM domain work

## Verified capabilities (`runtimes/claude/tools.json`)

**None yet.** `capabilities[]` is empty until `scripts/agent-verify-caps
--environment claude-code-cli --tools-file .ai/agents/splunky/runtimes/claude/tools.json`
records evidence. Do not list MCP servers or Slack connectors here until Phase 3
approval + Phase 5B verification.

Recommended MCP candidates (owner approval only — see contract bootstrap
`.ai/contracts/20260715-splunk-clone-monaecode/claude-desktop-bootstrap.json`):

- GitHub (monaecode/Sai PRs, Actions)
- Slack (`#splunk-clone-project` — create channel + wire MCP before claiming live)

## Optional: Claude scheduled task (after Phase 5B)

When the principal wants periodic protocol upkeep **inside Claude** (not Cursor):

1. Complete Phase 5B so at least `scripts/agent-report`, git read-only, and contract
   verifiers are `verified` in `runtimes/claude/tools.json`.
2. Create a scheduled task via Claude Code's scheduled-tasks API **only with session
   evidence** recorded in `tools.json` (see Mimi's `create_scheduled_task` row for format).
3. **Caveat:** scheduled tasks run when the Claude app is open at the fire time (or on
   next launch) — not an always-on cloud cron like Cursor Automations.
4. Update `hooks.json` `automation_triggers.required` with the real cron + task id.
5. Post first `[SAI][VERIFY]` to `#splunk-clone-project` and `#agentupdates` per contract.

Until then, **`hooks.json` documents intent only**; no fabricated automation name in registry.

## Session protocol (contract + ICM)

Use this block at the start of substantive Splunky sessions (adapt task-id and slug):

```
You are Splunky (ctr-code-splunky), Claude Code primary runtime, principal monaecode (U0BGNS7F0T1).

PURPOSE: Lead splunk-clone/ on monaecode/Sai under contract 20260715-splunk-clone-monaecode.
Stay provisional until ONBOARDING Phase 6 + Sai PERSONA_GATE VERIFY PASS.

CONTEXT: CLAUDE.md → .ai/agents/splunky/AGENT.md → charter contractor-coding.
Read .ai/_config/reporting.yaml manually (.mdc rules are not auto-loaded in Claude).

SAI_AGENT_ID=ctr-code-splunky

Before edits: .ai/stages/01_intake through 03_implement as applicable; artifact dir .ai/runs/<task-id>/.
Branches: proj/splunk-clone/ctr-code-splunky/<slug> only.
Slack: #splunk-clone-project — [SAI][PLAN] before PR, [SAI][VERIFY] after push.
Every PR: scripts/agent-contract-pr-review --contract-id 20260715-splunk-clone-monaecode.
Commits: Task-ID, Agent: Splunky, Plan, Report-Event trailers.

Hard limits: no force-push, no merge/close PRs, no core SAI integration until integration-manifest gate.
```

## Principal checklist (Phase 7 delivery)

1. **Do not** paste Splunky into Cursor Automations as the primary runtime.
2. Confirm `splunk-clone/.claude/settings.json` matches reviewed bootstrap JSON.
3. Run ONBOARDING Phases 3–5B before implementation or MCP grants.
4. When automation exists, update `registry.json` `automation` from `delegated:` to the
   confirmed mechanism (scheduled task id + cron, or `session-only; verified <date>`).

## After first verified automation or session sign-off

1. Record mechanism + date in `registry.json` (branch + trailers).
2. Post `[SAI][VERIFY]` to `#agentupdates` tagging monaecode (U0BGNS7F0T1).
3. Request Sai persona gate before lifting implementation NO-GO.
