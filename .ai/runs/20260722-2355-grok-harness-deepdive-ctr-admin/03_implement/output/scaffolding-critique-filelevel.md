# File-level scaffolding critique — agent runtimes vs docs

Base: `Dezocode/Sai` branch `cursor/grok-build-runtime-research-bd87`  
Docs: `agent-runtimes.md`, `claude-agent-sdk.md`, decision 0002, `CLAUDE.md`,
`CODEX.md`, `INITIALIZE.md` Phase 5B/7 notes.

## Expected layout (from `agent-runtimes.md`)

```
.ai/agents/<name>/
  AGENT.md, skills.md, hooks.json, tools.json (manifest)
  runtimes/
    README.md
    cursor|claude|codex/
      tools.json, automation/profile.md, README.md
    claude/agent-sdk/   # required for Claude-primary
```

---

## Sai (`ceo`) — primary `cursor-cloud-vm`

| Path | Status | Critique |
|---|---|---|
| `runtimes/cursor/tools.json` | Present | **20/20 verified** — strong |
| `runtimes/cursor/automation/profile.md` | Present | Matches Cursor Automations; registry has live URL |
| `hooks.json` | Present | Scheduled + Slack/GitHub recommendations aligned |
| `runtimes/claude|codex/README.md` | Stubs | OK if intentional non-primary |
| Agent SDK | N/A | Correct absence |

**Gap:** Keep automation Tools section synced when `tools.json` grows.

---

## Cora (`ctr-admin`) — primary `cursor-cloud-vm`

| Path | Status | Critique |
|---|---|---|
| `runtimes/cursor/tools.json` | Present | **25/25 verified**, role-tailored (contract scripts) — best inventory |
| `runtimes/cursor/automation/profile.md` | Present | Valid Cursor shape; registry still `delegated` / awaiting creation |
| `hooks.json` | Present | **Generic scaffold:** “configure per runtime in Phase 7” — honesty gap |
| Non-primary READMEs | Boilerplate | Should list missing files |

**Gap:** Inventory High, trigger truth Medium/Low — update hooks to match
registry automation state (offered vs live).

---

## Saul (`dezo-sec-codex1`) — primary `codex-desktop`

| Path | Status | Critique |
|---|---|---|
| `runtimes/codex/tools.json` | Present | **17/17 verified**, non-Cursor kinds |
| `runtimes/codex/automation/profile.md` | Present | **Gold standard honesty** — session-driven, no fake schedules |
| `hooks.json` | Present | `not_configured` / session_driven — matches profile |
| Cursor/Claude | Stubs | OK |

**Gap:** Minor scaffold leftover (`cursor_rules` key); verify-caps has no
Codex-specific branch (hand-curated caps).

---

## Mimi (`mimi`) — primary `claude-code-cli`

| Path | Status | Critique |
|---|---|---|
| `runtimes/claude/tools.json` | Present | **19 verified / 25 total**; no `claude-agent-sdk` cap |
| `runtimes/claude/automation/profile.md` | Present | **Wrong runtime:** titled “Cursor automation profile”; Automations UI paste flow |
| `hooks.json` | Present | **Honest:** Claude scheduled task `mimi-protocol-upkeep`; Slack/GitHub `not_built` |
| `runtimes/claude/agent-sdk/README.md` | Present | Checklist only |
| `…/agent-sdk/config/agent-options.json` | Present | Skeleton |
| `package.json` / `query()` runner / smoke | **Missing** | Fails `claude-agent-sdk.md` required layout |
| `runtimes/cursor/README.md` | Present | Notes historical Cursor UI — good |

**Gap vs docs:** `CLAUDE.md` and SDK reference forbid fabricating Cursor
Automations as live Claude automation. Profile file violates that; hooks do not.

---

## Alpha (`ctr-code-splunk1`) — primary `claude-code-cli` (provisional)

| Path | Status | Critique |
|---|---|---|
| `runtimes/claude/tools.json` | Present | **`capabilities: []`** — Phase 5B incomplete |
| `runtimes/claude/automation/profile.md` | Present | Cursor-shaped (same generator disease) |
| `hooks.json` | Present | Generic scaffold text |
| Agent SDK | README + config only | Placeholder |

**Gap:** Not ready for coding GO; ONBOARDING/persona gate must populate
Claude caps + non-Cursor automation + SDK smoke before active status.

---

## Generator / verifier gaps (root cause)

| Script / doc | Behavior | Impact |
|---|---|---|
| `scripts/agent-scaffold` | Enum `cursor\|claude\|codex`; Claude gets SDK README+config only | Cannot scaffold Grok; under-builds Claude advanced harness |
| `scripts/agent-automation-spec` | Cursor Automations framing | Writes Cursor profiles into Claude folders (Mimi, Alpha) |
| `scripts/agent-verify-caps` | Default env Cursor; Slack as `cursor-mcp` | Wrong kind labels for Claude/Codex surveys |
| `scripts/verify-agent-setup` | SDK: README+JSON presence; smoke via `SAI_CI_REQUIRE_SDK_SMOKE` (off) | Docs stricter than CI |
| `claude-agent-sdk.md` | Requires package + `query()` + smoke + verified cap | Mimi/Alpha fail advanced bar |
| Contract templates | cursor/claude/codex only | Correctly blocks Grok contracts |

---

## What “comprehensive tailored scaffolding” should mean

Per **primary** runtime, an agent folder is complete when:

1. `tools.json` verified caps match that runtime’s real tool/MCP/script surface
2. `automation/profile.md` names the real mechanism (Cursor UI / Claude schedule+SDK / Codex session / future Grok TUI|headless|ACP|/loop)
3. `hooks.json` truth table matches (1)+(2) and registry `automation` string
4. Harness extras required by Layer 3 docs exist (Claude Agent SDK tree; future Grok inspect notes)
5. `skills.md` lists role skills with codebase evidence (Cora pattern is good)
6. Non-primary suites: stub README with missing-file checklist + never-copy warning

Grok should be designed to that bar from day one — not as empty mirrors of
Cursor stubs.
