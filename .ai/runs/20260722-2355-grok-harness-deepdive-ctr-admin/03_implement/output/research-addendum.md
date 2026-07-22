# Research addendum — Grok harness tiers → SAI runtime scaffold

**Task:** `20260722-2355-grok-harness-deepdive-ctr-admin`  
**Parent:** `20260722-2341-grok-build-runtime-research-ctr-admin` (PR #47)  
**Agent:** Cora (`ctr-admin`)  
**Phase:** Research only — **no contract**, no Layer 0/schema edits  
**Date:** 2026-07-22

---

## Executive verdict (unchanged, refined)

**Yes — Grok Build requires a new SAI peer runtime suite** when adopted as an
org-registered or contracted primary environment:

| Field | Proposed value |
|---|---|
| Suite folder | `.ai/agents/<name>/runtimes/grok/` |
| Layer 0 entry | `GROK.md` |
| `primary_runtime` | `grok-build-cli` |
| Verify env | `agent-verify-caps --environment grok-build-cli` |

**Do not fold** into `runtimes/claude/` or `runtimes/cursor/` because Grok
reads those ecosystems’ rules/skills/MCP/hooks as **compatibility scanners**,
not as identity. Official docs confirm distinct binary (`grok`), auth plane
(`auth.x.ai` / OIDC / `XAI_API_KEY`), home (`~/.grok` / `$GROK_HOME`), project
dialect (`.grok/config.toml` subset), ACP (`grok agent stdio`), and automation
(`/loop`, headless `-p`, dashboard).

**Do not draft a contractor contract** until: (1) co-founders accept the draft
decision from the parent run, (2) enum/scaffold/templates land, (3) a live
Phase 5B survey runs against a real `grok` binary.

---

## 1. Operator harness ranking → SAI ownership

Operator ranking (Tier S/A/B/C) is engineering importance for the agent loop.
SAI maps that into **what must be surveyed / scaffolded / never committed**.

### Tier S — must exist (outside git; evidence only)

| Rank | Harness piece | SAI handling |
|---|---|---|
| 1 | `grok` binary (`~/.grok/bin` → downloads/) | `tools.json` cap `kind: shell/binary` with `grok version` / `grok inspect` evidence |
| 2 | `~/.grok/auth.json` / login / `XAI_API_KEY` | Cap `kind: auth` — status only; **never commit tokens** |
| 3 | Remote model API (`grok-4.5` etc.) | Cap `kind: model` — record default model from config (redacted) |

### Tier A — every-turn control plane (scaffold + survey)

| Rank | Harness piece | Future SAI artifact |
|---|---|---|
| 4 | `~/.grok/config.toml` (model, `permission_mode`, MCP, features) | Documented in `runtimes/grok/README.md` + verified caps for permission/sandbox modes actually used |
| 5 | Project rules: `AGENTS.md`, `.grok/rules/`, plus Claude/Cursor compat | Layer 0 `GROK.md` router + existing `AGENTS.md` / `CLAUDE.md` / `.cursor/rules` remain shared instruction layer |
| 6 | Built-in tools (binary) | Caps list pinned by live `grok inspect` / docs IDs — not invented from UI labels |
| 7 | `~/.grok/sessions/<cwd>/<id>/` | Ops reference only; optional run notes for resume/debug — not agent identity |

**Policy lines that matter more than skill files** (operator note, confirmed
by docs permissions modes): `models.default`, `permission_mode` /
`--always-approve` / `--yolo`, reasoning effort, sandbox profile. SAI Grok
profiles must **record actual mode** and forbid claiming sandbox if disabled.

### Tier B — specialization packs (optional verified caps)

| Rank | Harness piece | Future SAI artifact |
|---|---|---|
| 8 | Bundled/user skills (`SKILL.md`) | Agent `skills.md` + optional project `.grok/skills/` after security review |
| 9 | Bundled/custom agents (general-purpose, explore, plan) | Note as harness subagents — do **not** confuse with SAI registry agents |
| 10 | Roles / personas TOML | Optional; document if used for contractor policy |
| 11 | `bundled/manifest.json` | Integrity of install — ops only |
| 12 | Overlays: `~/.grok/{skills,agents}`, project `.grok/`, hooks, plugins, MCP | Caps + `hooks.json` truth table; project hooks need `/hooks-trust` review before commit |

### Tier C — ops/UX (reference, not identity)

Docs, caches, completions, `worktrees.db`, logs, housekeeping JSON — cite in
`runtimes/grok/README.md` “non-identity” section; do not invent registry fields.

---

## 2. Modes → SAI automation profile shape

| Mode | Entry | Must appear in `runtimes/grok/automation/profile.md` |
|---|---|---|
| TUI | `grok` | Interactive human-driven sessions (default desk work) |
| Headless | `grok -p` / `--single` | CI/scripted jobs; output formats; `--no-auto-update` |
| ACP | `grok agent stdio` | IDE/external client protocol — **no current SAI suite models ACP** |

Additional automation (not Cursor Automations UI): `/loop` (interval prompts,
max 50, 7-day expiry), background tasks, dashboard. Profiles must use Saul’s
honesty pattern: claim only verified mechanisms.

---

## 3. Why compatibility ≠ fold-in (docs reinforcement)

From docs.x.ai (see source list below):

- Loads `AGENTS.md` / `CLAUDE.md` / `.grok/rules/` **and** `.claude/rules/` /
  `.cursor/rules/` for compatibility.
- MCP merges Claude/Cursor configs **below** `config.toml`.
- Hooks can load Claude/Cursor hook files; project `.grok/hooks` still needs
  Grok trust.
- `grok import` / session resume across Claude/Codex/Cursor exists as
  **cross-ecosystem** feature — reinforces peer-harness status.
- Settings expose `[compat.claude]` / `[compat.cursor]` scanners — adapters
  over foreign trees, not identity merge.

Folding Grok into Claude/Cursor suites would corrupt Phase 5B evidence
(wrong binary, auth, automation, hook paths).

---

## 4. Closed enums today (blocks honest contracts)

| Gate | Current set | Grok |
|---|---|---|
| `contract.schema.json` `primary_runtime` | cursor-cloud-vm, cursor-desktop, claude-code-cli, codex-desktop | **absent** |
| `verify-semantic-hierarchy` `VALID_RUNTIMES` | same | **absent** |
| `agent-scaffold --primary-runtime` | cursor \| claude \| codex | **absent** |
| `agent-contract-scaffold --runtime` | cursor \| claude \| codex | **absent** |
| Layer 0 | `CLAUDE.md`, `CODEX.md`, `.cursor/rules/…` | **no `GROK.md`** |
| Contract templates | cursor/claude/codex only | **none** |

Correct for research: enums block ad-hoc Grok contracts until decision +
implementation.

---

## 5. Scaffolding critique summary (deepened)

Full file-level matrix:
`scaffolding-critique-filelevel.md`  
Rubric: `runtime-maturity-rubric.md`  
Future inventory: `proposed-grok-suite-inventory.md`

| Agent | Primary | Maturity | Headline gap |
|---|---|---|---|
| Cora | cursor | High inventory / Medium honesty on hooks | 25/25 caps; `hooks.json` still “configure in Phase 7”; automation `delegated` not live |
| Sai | cursor | High | Live Automations URL; keep profile Tools synced |
| Saul | codex | High honesty | Best non-Cursor model; 17/17 verified |
| Mimi | claude | Medium | Caps mixed; **Cursor-shaped** `runtimes/claude/automation/profile.md` vs honest `hooks.json`; Agent SDK missing package/`query()`/smoke |
| Alpha | claude (provisional) | Low | Empty caps; Cursor-shaped automation; SDK placeholder |

**Systemic docs vs files mismatch**

1. `claude-agent-sdk.md` requires package + `query()` + smoke; scaffold writes
   README + `agent-options.json` only; CI smoke flag off.
2. `agent-automation-spec` Cursor-first → poisons Claude Phase 7 folders.
3. `agent-verify-caps` defaults Slack to `cursor-mcp` kinds even outside Cursor.
4. Non-primary suite READMEs rarely list missing files.
5. No ACP/headless-cli profile pattern — Grok will need one first.

**Priority before adding Grok empty stubs (parallel, separate tasks)**

1. Runtime-aware `agent-automation-spec`
2. Fix Mimi/Alpha Claude automation profiles
3. Complete Claude Agent SDK harness for active Claude-primary agents
4. Branch `agent-verify-caps` by environment
5. Then implement Grok suite after decision accept

---

## 6. Pre-contract recommendation for org adoption

| Step | Owner | Notes |
|---|---|---|
| A. Accept/reject draft decision (parent run) | dezocode + monaecode (+ Sai audit) | Still unfiled |
| B. Implementation task: `GROK.md`, enums, scaffold, templates, `agent-runtimes.md` | Sai/Cora/Saul lane as assigned | Not this research |
| C. Live Phase 5B on machine with `grok` | Pilot agent principal | Capture redacted `grok inspect` |
| D. Only then: Cora contract templates / contractor `primary_runtime: grok-build-cli` | Cora | Persona gate + Sai audit still apply |

Security defaults for any future Grok profile:

- Prefer recording real `permission_mode` / sandbox; treat `always-approve` /
  `--yolo` as high-risk explicit choice.
- Never commit `auth.json`, session tokens, or managed secrets.
- Project `.grok/hooks` / MCP require trust + security-policy review before
  shared commit.

---

## 7. Honesty bounds

- No local `~/.grok` on research VM — Tier S/A file layout from operator notes
  + docs.x.ai; tool internal IDs may differ from UI (`bash` vs permission name
  `Bash`, etc.).
- Bundled skill names (`resume-claude`, etc.) from operator disk; changelog
  confirms cross-runtime session resume; treat skill package names as
  operator evidence pending live inspect.
- Critique based on repo files at branch HEAD after pull of CEO verify commits
  on PR #47.

---

## Sources

**Operator:** harness ranking message in this task (2026-07-22).  
**Parent research:** `…/20260722-2341-…/03_implement/output/research-report.md`  
**Official:**  
https://docs.x.ai/build/overview  
https://docs.x.ai/build/cli/headless-scripting  
https://docs.x.ai/build/features/project-rules  
https://docs.x.ai/build/settings  
https://docs.x.ai/build/features/hooks  
https://docs.x.ai/build/features/mcp-servers  
https://docs.x.ai/build/features/permissions  
https://docs.x.ai/build/features/background-tasks  
https://docs.x.ai/build/enterprise  
https://x.ai/news/grok-build-cli  
**Repo:** `.ai/shared/references/agent-runtimes.md`, `claude-agent-sdk.md`,
decision `0002-multi-runtime-agent-adapters.md`, scaffold/verify scripts.
