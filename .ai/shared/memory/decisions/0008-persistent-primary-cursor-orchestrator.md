# 0008 — Persistent primary Cursor orchestrator

- Date: 2026-08-13
- Task-ID: 20260813-2015-pr62-queue-ceo
- Status: accepted as principal requirement (PR #62 comment 5287297355);
  subject to the same Saul/Sai/human gates as the rest of PR #62
- Approver: dezocode
- Depends on: Decision 0006 (authorization loop), Decision 0007 (Runtime
  Intelligence plane). This record does not supersede 0006 or 0007.
- Source: https://github.com/Dezocode/Sai/pull/62#issuecomment-5287297355
- Also binds: comments 5287013791, 5285843795, 5282088737,
  5287857514, 5287878905, 5287885878, 5289020312

## Decision

SAI keeps a **persistent logical primary coordinator**. Physical Cursor
Cloud runtimes (`bcId`) are disposable workers of that logical program.
The previous physical primary ending because its child Task list emptied
while the PR exit predicate was still false is a **continuity defect**,
not completion.

Repo Git is canonical. Wiki/dashboard/Runtime Intelligence memory are
projections.

### Persistent logical primary

Each implementation program has a stable `primary_logical_id` (PR #62:
`pr62-primary`). Compact durable state lives at
`.ai/runs/<task-id>/coordinator-state.json` (schema
`coordinator-state.schema.json`). Pickup reads that file, then **refreshes
HEAD from git/GitHub**. Never reset to an older snapshot SHA.

### Physical runtime preference

Prefer continuing the last physical `bcId` when a supported follow-up
exists: Cloud Agents API `POST /v1/agents/{id}/runs` or Cursor SDK
`Agent.resume` + `send`. Both **require a prompt** (OpenAPI
`CreateRunRequest.required = [prompt]`). A busy agent returns 409
`agent_busy`.

Observed 2026-08-13: GitHub/Hostinger **cannot** silently resume a paused
interactive Cloud turn. Automations spawn a **new** agent. `/loop` only
while that conversation is still armed. This environment had **no**
`CURSOR_API_KEY`, so this VM cannot address `bcId` programmatically.

Fallback (required, not optional): `/resume-sai` logical pickup → new
physical runtime P1 → **same** logical primary → continue. No human
reconstruction.

Do not invent silent computer-use keystroke injection. MCP may transport
events; it is not the reasoning engine.

### `/resume-sai`

Official Cursor mechanism (docs 2026-08-13): **Agent Skills** at
`.cursor/skills/<name>/SKILL.md`, invoked as `/resume-sai`. Legacy
`.cursor/commands/` still load; new workflows are skills.

The skill runs `scripts/sai-resume` (deterministic reconstruction) then
continues the matching pstack-style playbook (`session-pickup`,
`orchestrate`, `autonomous-run` / SAI poteto default). It must not redo
completed work.

### SAI poteto default

`.cursor/rules/sai-orchestration.mdc` (`alwaysApply`) is SAI's in-repo
poteto: a co-founder saying "Implement X" is enough. pstack marketplace
plugin remains HOW when the Cloud session actually loaded it. SAI is WHO.
Neither bypasses the other.

### Lazy first-write Cora routing

Unchanged from 0006 + comment 5287013791: read/plan freely; first governed
mutation emits `SAI_IDENTITY_REQUIRED` / `SAI_CUE CORA_ADMISSION` or
`RESUME_CONTRACTOR`. Follow the cue. Do not ask the human to initialize.

### Named Cora worker

When contract administration is actually required, launch Cora as a
**named bounded subagent** of the primary:

- name: Cora
- agent_id: `ctr-admin`
- role: Contract Administration
- parent: the logical primary (and its physical `bcId`)
- contract / revision / grant / work-item / base SHA / model / state

Cora may inspect the task, update contract administration, create/amend
where authorized, register/reuse contractor identities, issue/refresh
leases, and return a compact admin result. Cora **must not** become the
implementation worker.

### Named contractor worker tree

Cora produces or selects contractor identities. Reuse a valid existing
contractor. Persist parent/child. Child authorization is **explicit**
(lease/grant); parent authority does not implicitly transfer.

```text
PRIMARY (logical id + physical bcId)
  +-- Cora / ctr-admin
  +-- named contractor A
  +-- named contractor B
  +-- named verifier
```

Task title is not organizational identity. Persist `agent_id`, `name`,
`role`, parents, contract, revision, lease/grant, work-item, base SHA,
model, state (`scripts/sai-runtime-registry`).

### Async subagents and waiting

Native Cursor children are `WAITING_WORKER` (nonterminal). Completions
are queue events (`scripts/sai-event-adapter`). Drain → integrate →
recompute the exit predicate → next work. Empty todos are not exit.

External Saul/CI/Sai are `WAITING_EXTERNAL` (nonterminal). Persist the
wake/pickup condition. Do not model-poll.

### Deterministic event queue

Digest-compare material payloads. Duplicate state is a cheap NOOP.
Primary owns: frame, brief, spawn, drain, integrate, decide, frontier,
human report, exit predicate. Workers perform bounded implementation.

### Liveness heartbeat

Default **1500 seconds** (25 minutes), configurable
(`SAI_WATCHDOG_HEARTBEAT_SECONDS` / coordinator `heartbeat_seconds`).
`scripts/sai-watchdog` reads durable worker records, git, and queued
events. It **must not invoke a model** just to compare status.

- healthy, unchanged → NOOP
- worker complete → queue `SUBAGENT_COMPLETE`
- stale last_seen → queue `STALE_WORKER`
- do not resume a worker merely to inspect it
- timebox + bounded retry; do not multiply zombies
- diagnose stale from durable evidence; rewrite brief or route to Cora
  only when the failure is contractual

### Two-primary implementation cap

`MAX ACTIVE PRIMARY IMPLEMENTATION PROGRAMS = 2` unless Dezocode
explicitly overrides (`.ai/_config/primary-programs.yaml`).

Count independent top-level implementation objectives. **Do not count:**
stacked PRs of those primaries; Runtime Intelligence / Grok+Hermes
subordinate PRs (Decision 0007); telemetry/graphing/memory sub-PRs;
read-only verification.

A third independent primary is **parked** (`CONCENTRATION_GATE`). Do not
fan out a third reasoning frontier.

### Terminal exit predicate

The logical primary may finish autonomously only when **all** hold:

- principal requirements resolved (ledger)
- contract/admin complete
- contractor work complete
- required CI green on the exact head
- real Saul Codex `APPROVE` of that exact head/revision
- Sai `APPROVE` of the same state
- no stale approvals, no P0/P1, no `REQUEST_CHANGES`, no expansion gate
- live orchestration smoke tests pass

Then `READY_FOR_HUMAN_REVIEW` and **stop for Dezocode**. Do not merge.
Do not mark ready. Subordinate Runtime Intelligence PRs do not block
unless they are an explicit blocking dependency.

### Trusted reviewer (unchanged fail-closed)

Candidate HEAD is never a trusted-reviewer success path (0006 / CTO-012).
Production path: `SAI_TRUSTED_REVIEWER_ROOT` or well-known
`/opt/sai/trusted-reviewer` on the Hostinger runner, else `git archive`
of an independently trusted base/default SHA.
`scripts/provision-trusted-reviewer-root` copies from an **explicit SHA**
and refuses symbolic/candidate HEAD unless a human `--confirm-trust`.
Unavailable → `BLOCKED` / `TRUSTED_REVIEWER_UNAVAILABLE`, skip Codex.

## Context

Comment 5287013791 required a standing primary orchestrator. A later
physical runtime proved native Cursor subagents, then exited while
`READY_FOR_HUMAN_REVIEW` was still false. Comment 5287297355 makes that
continuity failure a blocking requirement and demands `/resume-sai`,
named Cora/contractor identity, watchdog, and the two-primary cap.

Observed pstack 0.14.1: coordinator owns the program not the code;
plateau is not completion; standing orders survive resume; do not resume
workers merely to check them; long heartbeat is fallback not model
polling; humans are not asked "should I keep going?"

## Alternatives considered

- **Treat child-task completion as program completion** — rejected; that
  is the defect this record exists to close.
- **Silent GitHub→same-`bcId` wake** — unsupported by current Cursor
  API/docs; do not fake it with UI automation.
- **Copy pstack into `.ai/` expecting slash registration** — rejected by
  0004; `/resume-sai` is SAI-native under `.cursor/skills/`.
- **Restore candidate-HEAD trusted-reviewer fallback** — rejected by
  0006/CTO-012.
- **Cora continuously reading worker transcripts** — rejected; Cora
  supervises organizational state only.
- **Unbounded parallel primaries** — rejected; cap is 2.

## Rationale

Logical identity is what humans and Saul/Sai can reconstruct from Git.
Physical Cloud turns end. Skills and deterministic scripts are the
supported resume surface that does not require conversation replay.

## Consequences

- `.cursor/skills/resume-sai/SKILL.md` and `scripts/sai-resume`
- named worker registry + watchdog + primary-program cap
- Hostinger trusted-root provisioner (never HEAD by default)
- Requirement ledger `REQ-5287297355`
- Runtime Intelligence wiki/memory **projects** this decision; they do
  not replace it

## Amendment 2026-08-13 (blocker authority / max-effort continuation)

Discovery authority is not clearance authority.

Any authorized participant (Primary Cursor, Cora, contractor, verifier,
Runtime Intelligence, CI, Sai, Saul) may **append** an evidence-backed
blocker. They must not hide findings to keep the ledger small. Historical
blockers are never deleted.

`IMPLEMENTED` is not `PASSED`. Technical blockers become
`IMPLEMENTED_AWAITING_SAUL` until a **qualifying** Hostinger Saul/Codex
review (`codex_invoked=true`, `synthetic=false`, trusted reviewer source,
Saul persona from the trusted tree, exact head + revision, complete diff
and changed-path coverage) explicitly verifies the blocker is gone on
that exact state (`PASSED_BY_SAUL`). Cursor/Cora/contractor/RI/CI/Sai
cannot technically self-pass. Mechanical reject:
`TECHNICAL_CLEARANCE_REQUIRES_SAUL`.

Saul may discover additional CTO-N findings during every qualifying
review and those append automatically. Prior PASS on an older head is
stale if the new head changes relevant code.

Sai may append and, within CEO scope, clear **governance** blockers
(`PASSED_BY_SAI`). Sai must not impersonate Saul.

READY_FOR_HUMAN_REVIEW requires Saul technical APPROVE and Sai governance
APPROVE of the same exact state, CI green, no unresolved P0…Pn, trusted
reviewer independence proven. Then stop for Dezocode. Do not merge.

Preferred runtime: keep the same physical primary resident; ~15-minute
non-model wait (`scripts/sai-wait`, default 900s) only when the
machine-actionable frontier is empty (see 2026-08-14 amendment);
`/resume-sai` is recovery, not the normal cycle. Finishing the primary
while the predicate is false and machine work exists is
`PREMATURE_PRIMARY_TERMINATION`.

Trusted reviewer bootstrap (**replaces** the empty-dest first-writer
freeze previously recommended in this paragraph; Saul rejected that as
CTO-015 P0): never freeze a trusted root from a candidate PR on
`pull_request`. Fail closed `TRUSTED_REVIEWER_UNAVAILABLE` and skip
Codex. The provisioner (`trusted-reviewer-provision.yml`) is
operator/`main`-only. Do not restore candidate-HEAD trust (CTO-012).

CTO-021 (Saul run 31758118443, comment 5288037039): a PR-tree
`saul-review.yml` must not be the persistent-runner trust anchor.
Default-branch or another immutable trusted source is required (candidate
is DATA, never the executable trust tree). A-010 packages trusted
`pull_request_target` activation into PR #62 human merge (same SHA
retires the candidate-controlled Hostinger `pull_request` path). That
activation is **not** live on `origin/main` until Dezocode merges this
PR. Do not claim it is already on main. This officer record does not
PASS CTO-021 or CTO-025.

## Amendment 2026-08-14 (Cora-per-todo / Ralph / no-idle-Saul)

Sources (append-only; 0006/0007 and prior 0008 text stay in force):

- https://github.com/Dezocode/Sai/issues/62#issuecomment-5287857514
- https://github.com/Dezocode/Sai/issues/62#issuecomment-5287878905
- https://github.com/Dezocode/Sai/issues/62#issuecomment-5287885878

Canonical rule:

> Primary orchestrates. Named Cora evaluates authorization for every
> actionable todo. Named contractor subagents execute every actionable
> todo. Primary alone executes recursive `REASSESS BLOCKERS`.

Use **native Cursor subagents**, not simulated roleplay in the Primary
context. `.cursor/rules/sai-orchestration.mdc` (`alwaysApply`) must force
this for fresh Cloud agents. It must not depend on the human saying
"use subagents", "use Cora", or "use contractor".

### Per actionable todo (5287857514)

For every governed implementation todo except the terminal control todo
`REASSESS BLOCKERS`:

1. Named Cora (`ctr-admin`) evaluates contract / contractor / lease /
   scope for **this** todo. Reuse a valid contractor. Amend only on
   material delta. Cora does not implement.
2. Named contractor subagent executes the bounded todo, tests, and
   returns compact evidence to Primary.
3. Primary integrates, updates durable state, and selects the next todo.

Primary does not implement governed todos. Task title is not identity.

### `BLOCKERS>0` continues the Ralph loop (5287878905)

Any unpassed blocker → continue the Ralph-style primary loop. Worker
completion, a pushed SHA, local tests, CI, Cursor/Cora/contractor
judgment, an empty temporary todo list, or the end of a model turn is
not technical clearance or program completion.

`REASSESS BLOCKERS` is Primary-only. It ranks the P0→Pn frontier,
generates the next Cora→contractor wave, and re-appends itself while any
blocker remains unpassed.

Only Saul may technically PASS. This meta-P0 is last: Saul must not PASS
it while other applicable technical blockers remain unpassed.

### Never idle-wait on Saul (5287885878)

`SAUL_PENDING` is an external-review state, not an orchestration stop.
If any other machine-actionable work exists, continue through
Cora→contractor. The ~15-minute `scripts/sai-wait` is last resort after
`REASSESS BLOCKERS` confirms an empty machine-actionable frontier.

New commits while Saul reviews H1 mark that review stale for H2. Do not
misapply an old exact-head review.

### Blocker authority (restated)

- Anyone authorized may **append** an evidence-backed blocker.
  Discovery ≠ clearance. History is never deleted.
- `IMPLEMENTED` is not `PASSED`. Technical PASS requires a qualifying
  Hostinger Saul/Codex full CTO review (`codex_invoked=true`,
  `synthetic=false`, trusted reviewer source, Saul persona from the
  trusted tree, exact head + revision, complete diff coverage) →
  `PASSED_BY_SAUL`. Non-Saul technical PASS is
  `TECHNICAL_CLEARANCE_REQUIRES_SAUL`.
- Sai may PASS governance blockers (`PASSED_BY_SAI`). Sai must not
  impersonate Saul.
- Human (dezocode/monaecode) holds initial and final authority. After
  Saul technical APPROVE + Sai governance APPROVE of the same exact
  state, CI green, no unresolved P0…Pn: `READY_FOR_HUMAN_REVIEW`, stop
  for Dezocode. Do not merge. Do not mark ready.

### Unchanged from this record

Two-primary implementation cap. `/resume-sai` is recovery, not the
normal cycle. Prefer physical persistence + `sai-wait` when the frontier
is genuinely empty. Never merge or mark the PR ready.

## Amendment 2026-08-14 (architectural CTO / merge-activation / anti-bloat)

Sources (append-only; 0006/0007 and prior 0008 text stay in force):

- https://github.com/Dezocode/Sai/pull/62#issuecomment-5289020312
- Also still binds 5287857514, 5287878905, 5287885878

Principal P0 overnight-convergence (Cora A-010 → v10). Officer record
only. No Decision 0009. Does not PASS CTO-025 or any technical blocker.
Does not merge. Does not mark ready. Agents never merge PR #62.

### Two-plane Saul CTO review

Saul review has two planes. Both are required for technical APPROVE of
the exact head:

- **(A) Defect / security / authorization / CI / trust / tests.** Qualifying
  Hostinger Codex review as already required in this record. Only Saul
  may technically PASS.
- **(B) Architectural merge-readiness.** Trust topology, simplicity,
  transitional retirement, bounded PR, attack surface, rollback,
  operational ownership, and whether future agents can operate without
  duplicating machinery.

Saul may **AMEND/REFRAME** his own blockers when later evidence shows a
bootstrap paradox, unnecessary restrictiveness, redundant PRs, or
increased risk. Preserve original finding history. Do not weaken the
security invariant: candidate is DATA; never candidate-HEAD trust; never
checkout PR head into a trusted CWD then execute.

### CONDITIONAL_PASS_ON_HUMAN_MERGE (Saul-only)

Not a waiver. Not agent merge. Not Cora/contractor/Sai clearance.
Eligible only when all hold:

- artifact complete and reviewed
- only missing property is "now on protected main"
- human merge of this PR establishes that property
- candidate cannot exploit the transition
- secrets and privileged runners protected
- least privilege; fail closed
- rollback understood
- no hidden independent defect

Record condition, exact SHA, activation event, post-merge state, risk,
rollback, and verification. Agents must not treat this classification as
merge permission.

### CTO-025 merge-activation (do not PASS)

Prefer packaging the reviewed trusted `pull_request_target` workflow into
**this PR** so human merge activates it and retires the candidate-controlled
Hostinger `pull_request` path in the **same SHA**. Do not require an
intermediate human bootstrap PR when that merge-activation is safe.

If unsafe, Saul must give a concrete threat trace (attacker input, trust
crossing, privilege, execution path, damage) rather than a generic
"security sensitive" hold. This officer record does not PASS CTO-025.

Remaining this-PR reviews may use `workflow_dispatch`. Human merge of
PR #62 is the trusted-workflow activation event. Activation is **not**
live on `origin/main` until that merge.

### Anti-bloat

Classify work `REQUIRED_FOR_CURRENT_BLOCKER` |
`REQUIRED_FOR_FINAL_MERGE_QUALITY` | `DEFER_TO_FOLLOWUP`. Warning/triage
thresholds, not hard blocks without escape. Review-cost is first-class.
Do not invent perfectionism blockers.

- **P0** = trust / authority / security / correctness / fundamental behavior
- **P1** = significant reliability / maintainability that should not enter main

### READY_FOR_HUMAN_REVIEW (clarified)

May include Saul `APPROVE` **or** Saul `APPROVE` with narrow documented
merge-conditions (Saul-classified, including
`CONDITIONAL_PASS_ON_HUMAN_MERGE` when eligible) plus Sai `APPROVE` of
the same exact state, CI green, and merge package complete. Human action
is review+merge, not land another workflow then restart agents.

Do not merge. Do not mark ready. Agents never merge PR #62.
