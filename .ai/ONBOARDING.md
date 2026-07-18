# ONBOARDING — SAI Contractor Persona and Capability Protocol

> **To any contractor agent instructed to "read and execute onboarding.md":**
> this file is executable instructions. Perform every phase in order. You are
> not an active contractor until Phase 6 persona gate + Sai audit PASS.
> Sai audits your build against **both** this protocol and `.ai/INITIALIZE.md`.

Contractors are pointed here by the Contract Administrator's
`onboarding-prompt.md`. Load your contract from `.ai/contracts/<contract-id>/`
before starting.

---

## Phase 0 — Load contract

**Inputs:** owner prompt, `.ai/contracts/<contract-id>/contract.json`,
`.ai/contracts/<contract-id>/contract.md`.

1. Read `contract.json` and `contract.md` completely.
2. Read `.ai/CONTEXT.md` (Layer 0) and your type charter:
   - coding → `.ai/agents/_roles/contractor-coding/CHARTER.md`
   - design → `.ai/agents/_roles/contractor-design/CHARTER.md`
3. Read `.ai/agents/_roles/contractor-base/CHARTER.md`.
4. Read `.cursor/rules/sai-coordination.mdc`.

**Verification:** state `contract_id`, `project_slug`, `contractor_type`,
`isolation_mode`, `primary_runtime`, and principal in one sentence each.

## Phase 1 — Confirm contract terms

**Inputs:** owner (principal).

1. State back the contract terms: project name, deliverables, acceptance
   criteria, isolation mode, compatibility layer, branch prefix, Slack channel.
2. Ask the owner to confirm or correct. Amend `contract.json` and `contract.md`
   if needed; record amendments under `amendments/`.
3. Post a `CONTRACT` event to #agentupdates tagging Contract Administrator
   and Sai.

**Verification:** owner confirmation recorded in `amendments/` or contract
status moved from `draft` to `active`.

## Phase 2 — Research capabilities

**Inputs:** contract scope, runtime template from `.ai/contracts/_templates/`.

1. Survey MCP servers, marketplace skills, hooks, and dependencies relevant
   to the contracted work and `primary_runtime`.
2. Use the runtime-specific template for survey commands:
   - Cursor: `runtimes/cursor/tools.json`, Cursor MCP settings
   - Claude: `runtimes/claude/tools.json`, Claude Code connectors
   - Codex: `runtimes/codex/tools.json`, Codex Desktop tools
3. List candidates in a draft `approved_capabilities` proposal — do not
   install anything yet.

**Verification:** candidate list with rationale tied to contract deliverables.

## Phase 3 — Mandatory dependency approval loops

**Inputs:** candidate list from Phase 2, owner.

For **each** candidate MCP server, skill, hook, or dependency, ask the owner:

> **"Do you want me to bring [name] ([type]) into my agent profile?"**

Record every answer in `contract.json` → `approved_capabilities[]` with:
`name`, `type`, `approved_by`, `approved_at`, and `evidence` (or rejection
reason if declined).

Never add unapproved capabilities to `tools.json` or `hooks.json`.

**Verification:** every candidate has an owner decision on record.

## Phase 4 — Self-improve contract and profile

1. Update `contract.md` with the finalized capability plan.
2. Configure `hooks.json` and runtime `tools.json` for approved capabilities
   only. Test each; mark `verified` only with evidence per INITIALIZE Phase 5B.
3. Run `scripts/agent-verify-caps` against your runtime tools file.
4. Update `skills.md` with contract-specific skills backed by evidence.
5. Loop back to Phase 3 if new candidates emerge from research.
6. **Claude Code shell allowlists** (when copying `claude-desktop-bootstrap.json`
   or editing `.claude/settings.json`): never grant `Bash(git branch <prefix>/*)`
   or other bare `git branch <ref>` wildcards — prefix matchers still permit
   `git branch <allowed-prefix> -D <victim>`. Use read-only
   `Bash(git branch --list …)`, `Bash(git branch --show-current)`, and
   `Bash(git checkout -b …)` for branch creation; keep `-D`/`-d`/`--delete` in
   `explicitly_excluded`. CI runs `scripts/verify-contract-shell-allowlist` on
   every push/PR.

**Verification:** `agent-verify-caps` passes; only approved capabilities listed;
contract JSON passes `verify-contract-shell-allowlist`.

## Phase 5 — Mechanical initialization (INITIALIZE subset)

Run these INITIALIZE.md phases only:

| INITIALIZE phase | Contractor action |
|---|---|
| 0 | Ground truth (repo, remotes, status) |
| 1 | Role binding to contractor charter |
| 2 | `scripts/agent-init` — must print `AGENT-INIT: PASS` |
| 5B | Capability verification (already done in Phase 4) |
| 6 | Scaffold agent folder if not exists; registry entry `provisional` |

**Defer** INITIALIZE Phases 3–4 (Slack/GitHub orientation) if already done in
Phases 0–1; **defer** Phases 7–9 until after persona gate.

Set `SAI_AGENT_ID` to your `ctr-code-*` or `ctr-design-*` ID before `agent-init`.

**Verification:** `AGENT-INIT: PASS`; folder at `.ai/agents/<name>/`;
registry `status: provisional`.

## Phase 6 — Persona assumption gate

You are onboarded only when you **fully assume the contracted persona**.

1. Demonstrate contracted identity in `AGENT.md`, `skills.md`, and a live
   capability demonstration (one verified tool call per approved capability).
2. Post introduction to #help-newagents per INITIALIZE Phase 8 format, tagged
   with `contract_id`.
3. Post `PERSONA_GATE` event to #agentupdates; tag Contract Administrator and
   Sai.
4. Wait for Contract Administrator acknowledgment and Sai audit PASS before
   changing registry `status` to `active`.

**Verification:** `PERSONA_GATE` event delivered; Sai posts `VERIFY` PASS;
registry `status: active`.

## Phase 7 — Claim worktree and branch

**Inputs:** `.ai/shared/references/git-workflow.md`, contract `branch_prefix`.

1. Verify branch name unclaimed: `proj/<project-slug>/<agent-id>/<task-slug>`.
2. Post WORKTREE report.
3. `git worktree add <local-non-synced-path> <branch>` — outside Drive.
4. Join project `slack_channel` (if channel exists; if not, Contract Admin
   requests owner approval).

**Verification:** WORKTREE report; branch exists locally; worktree outside
synced paths.

## Phase 8 — Begin contracted work

Every task run must include in `metadata.json`:

- `contract_id`
- `project_slug`
- `contractor_type`
- `isolation_mode`

Follow ICM stages 01–06. On every PR, run:

```bash
scripts/agent-contract-pr-review --contract-id <id> --branch <branch>
```

Initialize per-agent memory at `.ai/agents/<name>/memory/` (see
`.ai/agents/README.md`).

---

## Standing obligations

- Evaluate every PR against contract acceptance criteria.
- Report to project Slack channel and #agentupdates.
- Keep `memory/audit/` current for multi-year contract audit.
- On contract close, Contract Administrator sets registry `status: retired`;
  preserve `memory/` indefinitely.

## Runtime templates

See `.ai/contracts/_templates/` for runtime-specific contract frameworks and
onboarding prompt structures.
