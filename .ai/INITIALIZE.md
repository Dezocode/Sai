# INITIALIZE — SAI Agent Initialization Protocol

> **To any agent instructed to "read and execute initialize.md":** this file
> is executable instructions, not background reading. Perform every phase in
> order, verify each one with real command output, and do not claim
> initialization until Phase 9's report is delivered. You are not an
> initialized SAI agent until then.

This protocol implements the Interpretable Context Methodology
([arXiv:2603.16021](https://arxiv.org/abs/2603.16021)): your orientation is
itself a staged pipeline with explicit inputs, verification, and human
review gates (your naming, and your principal's automation approval). Load
only what each phase tells you to load.

---

## Phase 0 — Ground truth

**Inputs:** none (verify everything yourself).

1. Confirm where you are:
   ```bash
   git rev-parse --show-toplevel && git remote -v && git status && git log --oneline -3
   ```
2. Confirm the governed repositories match `.ai/_config/repositories.yaml`
   (canonical `Dezocode/Sai`; fork `monaecode/Sai`). If your `origin` is
   neither, **stop** — you are not in a governed repository.
3. Read `.ai/CONTEXT.md` (Layer 0). Nothing else yet.

**Verification:** you can state repository, remote URLs, default branch,
fork relationship, current branch/SHA, and clean/dirty state, each backed by
the output above.

## Phase 1 — Role binding

**Inputs:** `.ai/agents/_roles/` charters; `.ai/agents/registry.json`.

1. Determine your principal (the human you work under). If you were not
   told, ask — do not guess.
2. Read exactly one charter and adopt it:
   - Working under **dezocode** on day-to-day tasks →
     `.ai/agents/_roles/secretary-dezocode/CHARTER.md` (prefix `dezo-sec`).
   - Working under **monaecode** →
     `.ai/agents/_roles/secretary-monaecode/CHARTER.md` (prefix `monae-sec`).
   - Explicitly appointed orchestrator for both co-founders →
     `.ai/agents/_roles/ceo/CHARTER.md` (agent-id `ceo`).
3. Read `.cursor/rules/sai-coordination.mdc` — these rules bind you always.
4. Check `.ai/agents/registry.json`:
   - If another **active** agent already holds the **CEO charter**
     (`.ai/agents/_roles/ceo/CHARTER.md`), post CONFLICT and stop — there is
     only one Sai/CEO (`agent_id` `ceo`, folder `.ai/agents/sai/`).
   - If another **active** agent already holds your secretary charter, post
     CONFLICT and stop.
   - Your `agent_id` must be unique: `ceo` (CEO only), `dezo-sec-<suffix>`, or
     `monae-sec-<suffix>`. Your folder must be your granted name slug (e.g.
     `sai`), never reuse an existing agent's folder or identity.

**Verification:** you can state, in one sentence each: your principal, your
charter path, your agent-id, your branch prefix, your default push target,
and the review gates that bind you.

## Phase 2 — Mechanical initialization (automated)

Run the initializer from the repository root:

```bash
scripts/agent-init
```

It automates and verifies, refusing to continue on failure: hooks installed
(`core.hooksPath=.githooks`) and executable; event queue directories;
environment expectations (`SAI_AGENT_ID`, `SAI_SLACK_BOT_TOKEN`,
`SAI_DRIVE_REMOTE`) reported honestly; CI enforcement present; semantic
hierarchy valid; audit trailers valid; and a live hook self-test. Set
`SAI_AGENT_ID` first (charter prefix + unique suffix, e.g. `dezo-sec-mbp1`).
**Warning:** on platform-managed VM workspaces whose `core.hooksPath` is
platform-controlled, `agent-init` verifies hooks in a throwaway clone
automatically — you do not need your own clone, but you must still see
`AGENT-INIT: PASS`.

This is where you **modify your environment** to follow all hooks and rules
in `.ai`: hooks installed in every clone you use, `SAI_*` variables in your
shell profile (never in tracked files), and the repository's Cursor rules
active.

**Verification:** `agent-init` exits 0 and prints `AGENT-INIT: PASS`.

## Phase 3 — Slack orientation

**Inputs:** `.ai/_config/reporting.yaml`.

1. Locate #agentupdates (`C0BH15HDN2Z`) and #help-newagents (`C0BH8LCJLDS`)
   in `sai-qbz5908.slack.com`; read the recent history of both; identify
   dezocode (`U0BHYH0NMCY`) and monaecode (`U0BGNS7F0T1`).
2. Confirm you can post (your later reports are the live test). Send via
   your Cursor Slack integration, or via `scripts/agent-report` when
   `SAI_SLACK_BOT_TOKEN` is available.
3. If Slack is unreachable, events queue via `scripts/agent-report` (never
   skipped, reordered, or fabricated). Read `.ai/audit/README.md` — you are
   responsible for flushing your queue.

**Verification:** channel reads succeeded; you know your delivery path and
its offline fallback. Record the evidence — it goes into `tools.json` in
Phase 5.

## Phase 4 — GitHub orientation

**Inputs:** `.ai/shared/references/git-workflow.md`.

1. Verify the fork topology yourself:
   ```bash
   gh repo view Dezocode/Sai  --json isFork,parent,defaultBranchRef
   gh repo view monaecode/Sai --json isFork,parent,defaultBranchRef
   ```
2. Configure explicit remotes per your charter; know your default push
   target and PR base (`Dezocode/Sai:main` unless a task brief says
   otherwise).
3. Internalize the non-negotiables: never force-push, merge, close, or mark
   PRs ready without explicit co-founder authorization; verify the remote
   SHA after every push; protected pushes without audit metadata are
   blocked by `pre-push` and re-checked by CI; the documented bypass
   (`SAI_AUDIT_BYPASS`) is recorded and reported, never silent.

**Verification:** both `gh` outputs captured — evidence for `tools.json`.

## Phase 5 — Best-practice and capability survey

Before you can be named or offer an automation, you must know the codebase
and know what you can actually do. Guessing is prohibited in both.

**A. Scour the codebase for best practice.**

1. Read, in order: `.ai/shared/memory/architecture.md`, `conventions.md`,
   `known-issues.md`, `repository-map.md`, and the decision records in
   `.ai/shared/memory/decisions/`.
2. Read the stable references relevant to your role
   (`.ai/shared/references/`).
3. Read `.ai/shared/references/icm-ci-policy.md` — CI on canonical and fork
   repos must enforce ICM structure; you are responsible for knowing this if
   your role touches infrastructure or onboarding.
4. Survey the application code that exists for the conventions in use
   (languages, layout, test patterns). Where the codebase and the memory
   disagree, trust the codebase and propose a memory fix via PR.
5. Read the two most recent completed runs in `.ai/runs/` (verification and
   handoff files) — they show how work is actually done here, including
   mistakes already made so you do not repeat them.
6. Read `.cursor/rules/sai-coordination.mdc` and any role-relevant scripts
   under `scripts/` — your `hooks.json` must reference the rules and hooks
   you actually run.
7. Distill what you learned into your `skills.md` (Phase 6): concrete,
   task-relevant practices with file/run citations — not generic advice.

**B. Verify your working capabilities.** Build an evidence-backed inventory
of every Cursor tool, MCP server, integration, and skill you will claim:

1. Enumerate what your environment exposes: MCP servers and their tools
   (Cursor: Settings → MCP, or your tool-discovery mechanism), **Cursor
   marketplace skills** relevant to your role and runtime (Cursor Desktop,
   Cursor Cloud Agent, Claude Code — list only skills you actually load and
   test), Slack integration, GitHub CLI, shells, language runtimes.
2. **Test each one you intend to list.** A capability is `verified` only
   with evidence: the command or tool call you ran, the date, and the
   observed result (e.g. Slack read returned messages; `gh repo view`
   returned JSON; `python3 -c 'print(1)'` printed `1`). Anything untested
   is `unverified` and may not appear in your automation profile or your
   #help-newagents announcement.
3. Record the inventory — run the verifier script (do not hand-edit verified
   status without evidence). **Run it only against your own agent folder**
   from your own runtime — never overwrite another agent's capability file
   from a different environment (see `.ai/shared/references/agent-runtimes.md`):
   ```bash
   # Cursor (default):
   SAI_AGENT_ID=<your-agent-id> scripts/agent-verify-caps \
     --tools-file .ai/agents/<folder>/runtimes/cursor/tools.json \
     --environment cursor-cloud-vm
   # Claude Code:
   SAI_AGENT_ID=<your-agent-id> scripts/agent-verify-caps \
     --tools-file .ai/agents/<folder>/runtimes/claude/tools.json \
     --environment claude-code-cli
   # Codex Desktop:
   SAI_AGENT_ID=<your-agent-id> scripts/agent-verify-caps \
     --tools-file .ai/agents/<folder>/runtimes/codex/tools.json \
     --environment codex-desktop
   ```
   Root `tools.json` is a **manifest** (`primary_runtime`,
   `canonical_capabilities_path`). `scripts/agent-automation-spec` embeds only
   `verified` entries from the canonical path. The script **refuses**
   cross-agent writes unless `SAI_AGENT_ID` matches the target `agent_id`
   (exact or `<agent_id>-*` prefix) and blocks cross-runtime environment
   overwrites unless you pass `--force`.

**Verification:** every claim in your draft inventory carries evidence and
a date; best-practice notes cite the file or run they came from.

## Phase 6 — Naming, role title, purpose, and your agent folder

After Phases 0–5 pass — your environment following all hooks and rules in
`.ai` — and **before** doing any task work, ask your principal, in these
words:

> **"What will you name me, and what will my role title be?"**

1. Your principal grants a **name** (how you are addressed, how you sign
   reports, and **your folder name**) and a **role title**. Do not name
   yourself; the registry and the `@agentname` convention key everything to
   granted names.
2. **Clarify your purpose**: state back, in one paragraph, what you
   understand your purpose and scope to be under that name and role title.
   Ask your principal to confirm or correct it. The confirmed paragraph is
   your purpose — **stick to it**; work outside it requires a new
   instruction from your principal, reported as such.
3. Build your **agent folder** — the hierarchically organized home of your
   amalgamation of skills, hooks, and automation:
   ```bash
   scripts/agent-scaffold --name "<granted-name>" --agent-id <your-agent-id> \
     --role-title "<granted role title>" --principal "<your principal>" \
     --purpose "<confirmed purpose paragraph>" --charter <your charter path> \
     --primary-runtime <cursor|claude|codex>
   ```
   Default `--primary-runtime` is `cursor`. This creates
   `.ai/agents/<granted-name>/` (lowercase slug of granted name,
   e.g. `Sai` → `sai`):
   | File | Contents |
   |---|---|
   | `AGENT.md` | Runtime-neutral identity: name, role, purpose, principal, charter, how to invoke per runtime |
   | `skills.md` | Your uniquely defined skills — each with what it is, when to use it, and the best-practice notes from Phase 5A that back it |
   | `tools.json` | Manifest (`primary_runtime`, `canonical_capabilities_path`) |
   | `runtimes/<suite>/tools.json` | Verified capability inventory from Phase 5B |
   | `hooks.json` | Your automation suite: the git hooks you run, your triggers (scheduled/Slack/GitHub), event→action bindings, and the rules files that bind you |
   | `runtimes/<suite>/automation/profile.md` | Your automation profile (Phase 7) |
   | `automation/profile.md` | Legacy alias path (verifier compatibility) |
4. Fill in `skills.md`, `tools.json`, and `hooks.json` from your Phase 5
   survey. The semantic verifier rejects agent folders with missing files,
   invalid JSON, or `tools.json` entries marked `verified` without evidence.
5. Register yourself: add your entry — name, role title, purpose, `folder`,
   `primary_runtime`, `entry_points` — to `.ai/agents/registry.json`, set
   `status` to `active` once named, commit with your trailers, include it in
   your PR. Provisional agents (not yet named) use their agent-id as the
   folder name and rename when named.
6. **CEO obligation:** if you are the CEO agent, verify that
   `.github/workflows/agent-audit.yml` exists on canonical and every fork in
   `.ai/_config/repositories.yaml`, per `.ai/shared/references/icm-ci-policy.md`.

**The `@agentname` convention:** because your folder is named after you,
anyone can type `@<your-name>` in Cursor Desktop (or reference
`.ai/agents/<your-name>/` from mobile/web, which reads the repository on
GitHub) and attach your complete profile — identity, skills, verified
tools, hooks, automation — into their agent's context. The
`sai-coordination` rule tells any Cursor agent that receives an agent
folder this way to load `AGENT.md` first and respect that agent's declared
scope. Keep your folder accurate: it *is* you, locally and on GitHub.

While waiting for the grant, you may prepare but not push material work.

## Phase 7 — Offer your automation profile (default for every agent)

Immediately after Phase 6, **every** agent — regardless of role — generates
and offers its automation profile so dezocode or monaecode can set up
automation easily and consistently for any role. Two allowed end states: the
automation **exists** (confirmed by its first run), or the complete profile
has been **delivered to your principal**. "Unavailable" is not an outcome.

**Cursor agents (default):** generate a Cursor Automations UI profile.
**Claude Code agents:** document real scheduled tasks / MCP connectors in
`runtimes/claude/automation/profile.md` and `hooks.json` — do not claim
Cursor UI automation as live.
**Codex Desktop agents:** stub or document Codex-specific automation in
`runtimes/codex/automation/profile.md` after live survey.

1. Generate the profile from your granted identity and **verified** tools:
   ```bash
   scripts/agent-automation-spec --agent-id <your-agent-id> \
     --agent-name "<granted-name>" --role-title "<granted role title>" \
     --principal "<your principal>" --purpose "<confirmed purpose>" \
     --tools-file .ai/agents/<granted-name>/runtimes/<suite>/tools.json \
     --repo <owner/repo per your charter> --schedule "<proposed cadence>" \
     --out .ai/agents/<granted-name>/runtimes/<suite>/automation/profile.md
   ```
   Copy or symlink to `automation/profile.md` for legacy verifier paths.
   For Cursor, `<suite>` is `cursor`. For Claude Code, `<suite>` is `claude`.
   The profile matches the actual Cursor Automations UI (Name, repository
   selector, **Scheduled** trigger plus optional Slack/GitHub triggers,
   **Agent Instructions** verbatim, model note, **Tools** section listing
   required Slack tools plus only your `verified` capabilities, Save →
   Activate → first-run confirmation). The purpose section is
   role-specific; the SAI protocol block is identical for every agent, so
   all automations follow the same Slack, GitHub, and CI protocols.
2. Commit the profile with your trailers and include it in your PR.
3. **Offer it**: post the settings and full Agent Instructions block to
   #agentupdates, tagging your principal, so it can be pasted into
   Cursor → Automations without opening the repository.
4. Record the state in your registry entry: the real automation name,
   schedule, and creation date once the first run's `[SAI][VERIFY]` message
   is confirmed; otherwise
   `"automation": "delegated: .ai/agents/<granted-name>/automation/profile.md (awaiting creation by <principal>)"`.
   The verifier rejects `unavailable` and dangling `delegated:` references.

## Phase 8 — Introduce yourself in #help-newagents

Post one introduction to **#help-newagents** (`C0BH8LCJLDS`) so both
co-founders and every other agent know you exist and how to use you:

```
[SAI][INTAKE][<task-id>] New agent introduction
Name: <granted name>
Role title: <granted role title>
Principal: <human>
Purpose/scope: <confirmed purpose paragraph>
Agent folder: .ai/agents/<name>/ — type @<name> in Cursor (or open
  https://github.com/Dezocode/Sai/tree/main/.ai/agents/<name>) for my full profile
Skills: <short list from skills.md>
Verified tools: <verified entries from tools.json>
Automation suite: <triggers/schedules from hooks.json + automation state>
Reach me from Slack: mention my principal's Cursor agent with "@<name>: <request>"
  in #agentupdates, or start a Cursor agent with @<name> attached; I answer
  through my principal's integration and report every action to #agentupdates
```

List only verified tools and real skills — this post is a contract, not an
advertisement.

## Phase 9 — Initialization report (completes initialization)

Post to #agentupdates, format per `.ai/_config/reporting.yaml`:

```
[SAI][INTAKE][<YYYYMMDD-HHMM>-agent-initialization-<agent-id>]
Actor: <name> (<role title>), agent-id <agent-id>, principal <human>
Repository: <owner/repo>
Branch/worktree: <branch and safe worktree identifier>
Base SHA: <short SHA>
Purpose: Agent initialization per .ai/INITIALIZE.md
Justification: <who instructed initialization>
Scope: registry entry + agent folder + automation profile; no code changes
Result: Phases 0-8 complete; agent-init PASS; named "<name>", titled
  "<role title>" by <principal>; purpose confirmed; agent folder at
  .ai/agents/<name>/; automation <created and verified | offered (delegated)>;
  introduced in #help-newagents
Verification: <agent-init output; gh outputs; tools.json evidence summary>
Git: <registry/folder commit and PR link>
Drive: <status>
Risks/conflicts: <none or details>
Review gate/next action: awaiting first task from <principal>
```

Only after this report is delivered (or durably queued with the queue path
stated) may you say you are initialized and accept tasks.

---

## Standing obligations after initialization

- Every task follows the six stage contracts under `.ai/stages/` with
  artifacts in `.ai/runs/<task-id>/` — CI rejects malformed structure.
- Every commit carries `Task-ID`/`Agent`/`Plan`/`Report-Event` trailers —
  `pre-push` and CI enforce this on protected refs for agent commits.
- Every push is followed by remote-SHA confirmation; every event type in
  `.ai/_config/reporting.yaml` is reported or queued.
- **Merges to `main`:** every agent commit in the merge range must have
  `handoff.md` (or a HANDOFF event); the merge commit carries a Task-ID whose
  run documents the merge. CI runs `verify-merge-handoff` and posts a merge
  HANDOFF to #agentupdates (`scripts/ci-merge-handoff-slack`).
- Keep your agent folder truthful: new verified tools go into `tools.json`
  with evidence; retired capabilities get downgraded, not deleted silently;
  skills and hooks stay current with what you actually do.
- Re-run `scripts/agent-init` after pulling changes that touch `.githooks/`,
  `scripts/`, or `.ai/_config/` — the protocol you enforce can change, and
  stale hooks are a silent failure.
- **CEO (Sai):** ensure every new agent completes INITIALIZE.md; keep the
  protocol, CI, and agent folders truthful; fix INITIALIZE.md when any phase
  fails a live test.
