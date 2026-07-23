# Research report — Grok Build vs SAI runtimes + scaffolding critique

**Task:** `20260722-2341-grok-build-runtime-research-ctr-admin`  
**Agent:** Cora (`ctr-admin`)  
**Phase:** Research only — **no contract**, no schema/scaffold edits  
**Date:** 2026-07-22

---

## Executive verdict

**Yes — Grok Build needs a new SAI runtime suite** (`runtimes/grok/`, Layer 0
`GROK.md`, `primary_runtime` enum value such as `grok-build-cli`) **when** SAI
registers or contracts any agent whose primary execution environment is the
Grok Build CLI/harness.

**Do not** fold Grok into Cursor/Claude/Codex suites. Grok can *read*
`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` for compatibility, but it has a
distinct harness control plane: `~/.grok` + project `.grok/`, permission and
sandbox flags, ACP (`grok agent stdio`), hooks trust model, MCP CLI, worktrees,
sessions store, and local `/loop` automation.

**Do not** draft a contractor contract in this phase. Next step is a co-founder
decision (proposed draft in this run) that extends decision 0002, then a
follow-on scaffolding task.

---

## 1. What the Grok “harness” is (mapped to SAI)

Operator notes + public docs agree: Grok Build is a **local agentic harness**
(binary + config + auth + tool runtime + session store + bundled
skills/agents), not merely a model API.

| Harness tier | Paths / pieces | SAI mapping |
|---|---|---|
| **S — must exist** | `grok` binary, `auth.json` / `XAI_API_KEY`, remote model API | Outside git; record as environment prerequisites in `runtimes/grok/tools.json` evidence |
| **A — every turn** | `config.toml`, project rules (`AGENTS.md`, `.grok/rules/`, also Claude/Cursor compat), built-in tools, `sessions/` | Layer 0 entry (`GROK.md` + existing `AGENTS.md`), per-agent `runtimes/grok/{tools.json,automation/}` |
| **B — specialization** | Bundled/user skills, agents, roles/personas, MCP, hooks, plugins | Skills → agent `skills.md` + optional `.grok/skills/`; MCP/hooks → verified caps + hooks truth table |
| **C — ops/UX** | Docs, caches, completions, logs, worktrees.db | Reference material; not identity |

Sources: [Grok Build Overview](https://docs.x.ai/build/overview),
[Project rules](https://docs.x.ai/build/features/project-rules),
[CLI reference](https://docs.x.ai/build/cli/reference),
[Hooks](https://docs.x.ai/build/features/hooks),
[Background tasks](https://docs.x.ai/build/features/background-tasks);
requester `~/.grok` ranking (operator notes; VM has no local `~/.grok`).

### Modes (front ends, same core)

| Mode | Start | SAI analogue |
|---|---|---|
| TUI | `grok` | Cursor Desktop / Claude Code interactive / Codex Desktop session |
| Headless | `grok -p "..."` | CI/scripted agents; Cursor Cloud headless-ish jobs |
| ACP agent | `grok agent stdio` | IDE/external client protocol — **no current SAI suite models ACP** |

### Distinct control-plane facts (why a new suite)

1. **Home + project split:** user `~/.grok/config.toml` vs project
   `.grok/` (skills, plugins, hooks; project config contributes MCP/plugins/
   permission slices per docs).
2. **Rule discovery:** loads `AGENTS.md` / `AGENT.md` / `CLAUDE.md` /
   `.grok/rules/*.md` and also `.claude/rules/` + `.cursor/rules/` for
   compatibility — compatibility ≠ same runtime adapter.
3. **Permissions / sandbox:** `--always-approve` / `--yolo`, `--allow` /
   `--deny`, `--sandbox`, project hook trust via `/hooks-trust` or `--trust`
   stored in `trusted_folders.toml`.
4. **Automation:** local `/loop` scheduled prompts (interval, 7-day expiry,
   max 50), background commands, monitors, dashboard — **not** Cursor
   Automations UI and **not** Claude Code scheduled-tasks API.
5. **Session persistence:** `~/.grok/sessions/<cwd>/<id>/` with
   `updates.jsonl`, `system_prompt.txt`, etc. — resume/export/import
   (`grok import` from Claude Code exists).
6. **Bundled multi-runtime resume skills** (operator note:
   `resume-claude`, `resume-codex`, `resume-cursor`) reinforce that Grok is a
   **peer harness** that can hand off across ecosystems, not a thin wrapper
   around one of them.

---

## 2. Decision criteria — new runtime vs fold-in

### Fold into an existing suite? **No**

| Tempting shortcut | Why it fails |
|---|---|
| “Grok reads `CLAUDE.md` → use `runtimes/claude/`” | Claude suite assumes Claude Code CLI + Agent SDK packages/`query()`; Grok uses different binary, auth, ACP, hooks files under `.grok/hooks/` |
| “Grok reads `.cursor/rules/` → use `runtimes/cursor/`” | Cursor suite assumes Automations UI + Cursor MCP/tool IDs; Grok automation is `/loop`/headless/ACP |
| “Just document Grok in `CODEX.md`” | Codex Desktop is a different product; Saul’s suite is session-driven Codex evidence |

### Add `runtimes/grok/` when **any** of these become true

1. A registered agent’s `primary_runtime` will be Grok Build CLI, **or**
2. A contractor contract must bind deliverables to Grok-specific caps
   (ACP, permission modes, `.grok` hooks, headless CI), **or**
3. Org policy requires verified Grok capability surveys (Phase 5B) before
   Grok agents post `[SAI]` events.

### Defer adding the suite if

- Grok is only used informally by humans with no registry identity, **and**
- No contracts / CI / automation claims depend on Grok evidence.

**Org intent signal:** requester is “thinking about adding grok build cli to
the sai organization” → treat as **prepare decision + scaffold plan**, not
defer indefinitely.

---

## 3. Recommended SAI shape (future implementation — not this PR)

When co-founders accept the decision draft:

| Artifact | Purpose |
|---|---|
| `GROK.md` | Layer 0 entry router (peer of `CLAUDE.md` / `CODEX.md`) |
| `.ai/agents/<name>/runtimes/grok/tools.json` | Verified caps: binary, auth mode, models, built-in tools, MCP, ACP, hooks, worktrees, `/loop` |
| `…/runtimes/grok/automation/profile.md` | Honest mechanics only (local loop / headless / ACP / external wrapper) |
| `…/runtimes/grok/README.md` | Suite purpose + non-copy warning |
| Optional project `.grok/` | Repo-local skills/hooks/MCP — **only after** trust/security review |
| `primary_runtime: grok-build-cli` | Registry + contract schema enum + scaffold `--primary-runtime grok` |
| `.ai/contracts/_templates/grok-contract-template.{json,md}` | Cora contract path |
| Extend `agent-runtimes.md` + decision 0002 (or 000N) | Canonical index |

**Suggested `tools.json` capability categories for first Grok survey**

- `shell`/`binary`: `grok`, `grok version`, `grok inspect`
- `auth`: login / `XAI_API_KEY` (never store secrets in repo)
- `builtin_tools`: file/edit/grep/bash/web/todo/task (IDs as reported by
  live `grok inspect` / docs — do not invent)
- `mcp`: `grok mcp list|doctor`
- `protocol`: `grok agent stdio` (ACP)
- `automation`: `/loop` or headless wrapper — status `verified` only with
  evidence
- `hooks`: project/user hooks + trust state (no secrets)
- `worktrees`: `grok worktree` when used for isolation

---

## 4. Critique — existing runtime scaffolding vs docs

Canonical expectations from
`.ai/shared/references/agent-runtimes.md`,
`.ai/shared/references/claude-agent-sdk.md`,
decision `0002-multi-runtime-agent-adapters.md`,
and scaffold/verify scripts.

### Completeness matrix (primary suite emphasized)

| Agent | Primary | Cursor | Claude | Claude Agent SDK | Codex |
|---|---|---|---|---|---|
| Sai | cursor-cloud-vm | **High** (20 verified) | Low stub | N/A | Low stub |
| Mimi | claude-code-cli | Low README | **Medium** (25 mixed) | **Low** (README/config only) | Low stub |
| Saul | codex-desktop | Low README | Low stub | N/A | **High** (honest session profile) |
| Cora | cursor-cloud-vm | **High** (25 verified, role-tailored) | Low stub | N/A | Low stub |
| Alpha | claude-code-cli (provisional) | Low stub | **Low** (`capabilities: []`) | **Low** placeholder | Low stub |

### What “good” looks like today

**Best tooling inventory:** Cora Cursor — role-specific verified scripts
(contract scaffold, PR review, memory, worktrees) with evidence strings.

**Best honesty / tailored automation narrative:** Saul Codex —
explicitly refuses to claim unattended schedules or wake triggers that were
not verified (`runtimes/codex/automation/profile.md`).

**Best Claude interactive survey (incomplete vs SDK docs):** Mimi —
caps + hooks document scheduled task vs missing Slack/GitHub triggers, but
Agent SDK harness required by `claude-agent-sdk.md` is still a skeleton
(no `package.json` / `query()` runner / smoke evidence).

### Systemic gaps (docs vs files)

1. **Claude Agent SDK docs overshoot scaffolds.** Docs require
   `package.json`|`pyproject.toml`, `query()` entrypoint, smoke log, and
   verified `claude-agent-sdk` capability. `agent-scaffold` only writes
   README + `agent-options.json`. Mimi/Alpha both fail the “advanced”
   bar; Alpha’s primary `tools.json` is empty.
2. **`agent-automation-spec` is Cursor-first.** Emits Cursor Automations
   framing even when targeting Claude folders — produces misleading
   profiles (seen on Alpha; Mimi history stored Cursor-shaped content under
   Claude automation).
3. **Non-primary suites are thin READMEs.** They rarely state *which files
   are missing* or warn “never copy capabilities across runtimes.”
4. **Hooks truth tables are generic.** Scaffolded `hooks.json`
   `automation_triggers` still say “configure in Phase 7” for agents that
   already finished init (e.g. Cora) — unlike Saul’s prose honesty.
5. **Sai Cursor profile drift risk.** Automation profile can lag newer
   `tools.json` inventory (refresh when claiming live Automations).
6. **No ACP / headless-cli suite pattern exists** — Grok (and partially
   Claude headless) need a documented pattern for non-UI front ends.
7. **Contract/runtime enums are closed.** Adding Grok is a coordinated
   schema + scaffold + template + docs change — correct for a decision, not
   an ad-hoc agent folder edit.
8. **Verify gates soft on SDK.** `verify-agent-setup` can pass without SDK
   smoke unless `SAI_CI_REQUIRE_SDK_SMOKE=1` — docs describe a stricter
   world than CI enforces.

### Prioritized scaffolding improvements (existing runtimes)

Ordered for organizational value; **not executed in this research task**:

1. Make `agent-automation-spec` runtime-aware (cursor vs claude vs codex vs
   future grok).
2. Extend Claude scaffold to create package/runner stubs matching
   `claude-agent-sdk.md`.
3. Require package/runner (+ optional smoke) for **active** Claude-primary
   agents in `verify-agent-setup`.
4. Complete Mimi Agent SDK dispatcher to match her charter (Slack/GitHub).
5. Finish Alpha onboarding: populate Claude `tools.json`, non-Cursor
   automation, SDK smoke — before any coding GO.
6. Relocate/replace misfiled Cursor automation content under Claude paths.
7. Refresh Sai Cursor automation Tools section to match inventory.
8. Replace generic hooks automation blocks with verified mechanism fields
   per agent (Saul pattern).
9. Enrich non-primary README stubs with missing-file checklists.
10. Add a Layer 3 “runtime maturity rubric” (survey / automation honesty /
    SDK-or-harness / entry router) so critiques stay objective.

---

## 5. Implications for “adding Grok to the SAI organization”

| Track | Pre-contract research answer |
|---|---|
| New runtime? | **Yes**, as peer suite under decision 0002 model |
| Contract now? | **No** — wait for decision acceptance + enum/scaffold readiness |
| Minimum org adoption package | Decision + `GROK.md` + `agent-runtimes.md` update + scaffold/schema/templates + one pilot agent Phase 5B survey on a machine with real `grok` |
| Security notes | `permission_mode=always-approve` / `--yolo` is high-risk; SAI Grok profiles must default to recording actual mode and forbid claiming sandbox if disabled; never commit `auth.json` |
| Compatibility gift | Grok already loads `AGENTS.md` + Claude/Cursor rules — Layer 0 SAI docs remain useful immediately even before `GROK.md` |

### Pilot recommendation (post-decision)

1. Human installs/auths Grok on a non-Drive worktree machine.  
2. Run `grok inspect` in Dezocode/Sai; capture redacted output under a new
   run.  
3. Scaffold `runtimes/grok/` for a named agent (likely a new secretary or
   pilot contractor) via extended `agent-scaffold --primary-runtime grok`.  
4. Phase 5B verify caps with evidence.  
5. Only then consider Cora contract templates for Grok contractors.

---

## 6. Honesty bounds

- No local `~/.grok` on the research VM — binary internals and exact bundled
  skill list not re-listed from disk.
- Public docs confirm modes, rules discovery, hooks, `/loop`, ACP subcommand,
  MCP CLI; some operator tool ID spellings (`grep_search` vs `grep`, MCP
  `search_tool`/`use_tool`) may differ from UI labels — live survey must
  pin IDs.
- Scaffold critique based on repo files at `main` `@8da8530` plus this
  branch’s research-only additions.

---

## 7. Recommendation summary

1. **Accept** proposed decision: add Grok Build as a fourth runtime family.  
2. **Do not** open a contractor contract until scaffold/schema/templates
   exist.  
3. **Parallel (optional, separate tasks):** close Claude SDK / Alpha / Mimi
   scaffolding gaps so “advanced agents” docs match reality before adding
   another runtime’s empty stubs.  
4. **Cora’s next contract-admin action after GO:** extend
   `agent-contract-scaffold` + grok templates; keep Sai as protocol auditor.
