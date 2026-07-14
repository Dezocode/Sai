# INITIALIZE — SAI Agent Initialization Protocol

> **To any agent instructed to "read and execute initialize.md":** this file
> is executable instructions, not background reading. Perform every phase in
> order, verify each one with real command output, and do not claim
> initialization until Phase 7's report is delivered. You are not an
> initialized SAI agent until then.

This protocol implements the Interpretable Context Methodology
([arXiv:2603.16021](https://arxiv.org/abs/2603.16021)): your orientation is
itself a staged pipeline with explicit inputs, verification, and a human
review gate (your naming). Load only what each phase tells you to load.

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

**Inputs:** `.ai/agents/` charters; `.ai/agents/registry.json`.

1. Determine your principal (the human you work under). If you were not
   told, ask — do not guess.
2. Read exactly one charter and adopt it:
   - Working under **dezocode** on day-to-day tasks →
     `.ai/agents/secretary-dezocode/CHARTER.md` (agent-id prefix `dezo-sec`).
   - Working under **monaecode** → `.ai/agents/secretary-monaecode/CHARTER.md`
     (agent-id prefix `monae-sec`).
   - Explicitly appointed orchestrator for both co-founders →
     `.ai/agents/ceo/CHARTER.md` (agent-id `ceo`).
3. Read `.cursor/rules/sai-coordination.mdc` — these rules bind you always.
4. Check `.ai/agents/registry.json`: if another **active** agent already
   holds the role you are adopting, post a CONFLICT report and wait for your
   principal instead of proceeding.

**Verification:** you can state, in one sentence each: your principal, your
charter path, your agent-id, your branch prefix, your default push target,
and the review gates that bind you.

## Phase 2 — Mechanical initialization (automated)

Run the initializer from the repository root:

```bash
scripts/agent-init
```

It automates and verifies, refusing to continue on failure:

- hooks installed (`core.hooksPath=.githooks`) and executable;
- event queue directories created;
- environment expectations (`SAI_AGENT_ID`, `SAI_SLACK_BOT_TOKEN`,
  `SAI_DRIVE_REMOTE`) reported honestly;
- CI enforcement present (`.github/workflows/agent-audit.yml`);
- semantic hierarchy of `.ai/` valid (`scripts/verify-semantic-hierarchy`);
- audit trailers valid on your current range (`scripts/verify-agent-audit`);
- a live hook self-test in a throwaway branch (commit → event captured),
  cleaned up afterwards.

Set `SAI_AGENT_ID` before running it (your charter's agent-id plus a unique
suffix, e.g. `dezo-sec-mbp1`). **Warning:** do not run `agent-init` inside a
managed VM workspace whose `core.hooksPath` is platform-controlled; use your
own clone or worktree (Cursor Desktop clones qualify).

**Verification:** `agent-init` exits 0 and prints `AGENT-INIT: PASS`.

## Phase 3 — Slack orientation

**Inputs:** `.ai/_config/reporting.yaml`.

1. Locate #agentupdates (channel id `C0BH15HDN2Z`) in the
   `sai-qbz5908.slack.com` workspace; confirm you can read it (fetch the
   latest messages) and identify dezocode (`U0BHYH0NMCY`) and monaecode
   (`U0BGNS7F0T1`).
2. Confirm you can post: your Phase 7 report is the test. Send messages
   through your Cursor Slack integration, or via `scripts/agent-report`
   when `SAI_SLACK_BOT_TOKEN` is available to your shell.
3. If Slack is unreachable, events must queue via `scripts/agent-report`
   (never skipped, never reordered, never fabricated). Read
   `.ai/audit/README.md` so you understand the queue you are responsible
   for flushing.

**Verification:** you have read the channel's recent history and know the
delivery path you will use, including the offline fallback.

## Phase 4 — GitHub orientation

**Inputs:** `.ai/shared/references/git-workflow.md`.

1. Verify the fork topology yourself (do not trust files alone):
   ```bash
   gh repo view Dezocode/Sai  --json isFork,parent,defaultBranchRef
   gh repo view monaecode/Sai --json isFork,parent,defaultBranchRef
   ```
2. Configure explicit remotes per your charter, and know your default push
   target and PR base (`Dezocode/Sai:main` unless a task brief says
   otherwise).
3. Internalize the non-negotiables: never force-push, merge, close, or mark
   PRs ready without explicit co-founder authorization; verify the remote
   SHA after every push (`scripts/agent-report push-confirm` or
   `.githooks/post-push-equivalent.sh`); protected pushes without audit
   trailers are blocked by `pre-push` and re-checked by CI — the documented
   bypass (`SAI_AUDIT_BYPASS`) is recorded and reported, never silent.

**Verification:** both `gh` outputs quoted in your Phase 7 report.

## Phase 5 — Naming and role title (human review gate)

After Phases 0–4 pass, and **before** doing any task work, ask your
principal to give you:

1. a **name** (how you will be addressed and how you sign reports), and
2. a **role title** (e.g. "Secretary to monaecode", "Release Steward").

Do not name yourself. Do not skip this because it feels ceremonial — the
registry keys ownership and conflict resolution to named agents. While
waiting, you may prepare but not push material work.

When granted, register yourself: add your entry to
`.ai/agents/registry.json` (schema documented in the file) on a branch,
commit with your trailers, and include it in your next PR.

## Phase 6 — Cursor automation self-setup

Every initialized agent maintains its own Cursor automation so that
protocol upkeep does not depend on memory. There are exactly two allowed
outcomes of this phase: the automation **exists**, or a complete
specification for it has been **delivered to your principal**. "Unavailable"
is not an outcome.

**Path A — you can create automations** (Cursor Desktop → Automations, or
[cursor.com/automations](https://cursor.com/automations)):

1. Generate your prompt and settings so they are exact, not improvised:
   ```bash
   scripts/agent-automation-spec --agent-id <your-agent-id> \
     --agent-name "<your granted name>" --principal "<your principal>" \
     --repo <owner/repo per your charter> --schedule "<approved cadence>" --stdout
   ```
2. Create the automation exactly as the spec says (name
   `SAI <your-name> — protocol upkeep (<agent-id>)`, owner = your
   principal, schedule approved by them, the prompt verbatim).
3. Run it once manually; confirm its `[SAI][VERIFY]` message appears in
   #agentupdates.
4. Record name, schedule, and creation date in your registry entry's
   `automation` field.

**Path B — you cannot create automations** (cloud VM, restricted
environment, missing permissions). Complete the delegated path in full:

1. Generate the spec file:
   ```bash
   scripts/agent-automation-spec --agent-id <your-agent-id> \
     --agent-name "<your granted name>" --principal "<your principal>" \
     --repo <owner/repo per your charter> --schedule "<proposed cadence>"
   ```
   This writes `.ai/agents/automation-specs/<agent-id>.md` containing every
   detail the principal needs: where to create it, every settings field
   (name, owner, schedule, repository, branch, environment, optional
   secrets), the full automation prompt to paste verbatim, and the
   post-creation confirmation steps. Nothing is left for the principal to
   figure out.
2. Commit the spec with your trailers and include it in your PR.
3. Deliver it: post the spec's **full prompt block and settings table** to
   #agentupdates, tagging your principal, so it can be pasted into
   Cursor → Automations without opening the repository.
4. Set your registry entry to
   `"automation": "delegated: .ai/agents/automation-specs/<agent-id>.md (awaiting creation by <principal>)"`.
   The semantic verifier rejects `unavailable` and rejects `delegated:`
   entries whose spec file does not exist.
5. When your principal confirms creation and the first manual run has
   posted its `[SAI][VERIFY]` message, update the registry field to the
   real automation name, schedule, and creation date.

On both paths: enable the repository's Cursor rules (`.cursor/rules/` —
`sai-coordination.mdc` applies always) and keep the git hooks installed in
every clone you create (`scripts/install-agent-hooks`). Say in Phase 7 which
path you took — never claim an automation exists before its first confirmed
run.

## Phase 7 — Initialization report (completes initialization)

Post to #agentupdates, format per `.ai/_config/reporting.yaml`:

```
[SAI][INTAKE][<YYYYMMDD-HHMM>-agent-initialization-<agent-id>]
Actor: <name> (<role title>), agent-id <agent-id>, principal <human>
Repository: <owner/repo>
Branch/worktree: <branch and safe worktree identifier>
Base SHA: <short SHA>
Purpose: Agent initialization per .ai/INITIALIZE.md
Justification: <who instructed initialization>
Scope: registry entry; no code changes
Result: Phases 0-6 complete; agent-init PASS; named "<name>" by <principal>
Verification: <agent-init output line; gh repo view outputs; hook self-test evidence>
Git: <registry commit/PR link, or "pending">
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
- Re-run `scripts/agent-init` after pulling changes that touch `.githooks/`,
  `scripts/`, or `.ai/_config/` — the protocol you enforce can change, and
  stale hooks are a silent failure.
