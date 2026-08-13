# 0007 — Parallel Runtime Intelligence Plane for Hermes + Grok

- Date: 2026-08-13
- Task-ID: `20260813-runtime-intelligence-plane`
- Status: accepted by co-founder intent; subject to normal PR #62 review/merge gates
- Approver: dezocode
- Depends on: Decision 0006 (repo-native authorization, Cora/contractor/Saul/Sai separation)

## Decision

SAI adopts a **parallel Runtime Intelligence plane** on the Hostinger infrastructure. Hermes and the existing Grok Telegram bridge are support agents that operate **asynchronously beside** the Cursor/Cora/contractor build loop. They may observe, test, instrument, visualize, open issues, and build governed sub-PRs, but they must never become a synchronous dependency that stalls Cursor's development loop and must never merge any branch to `main`.

The build plane remains authoritative for implementation:

```text
Human
  -> Sai governance/orchestration
  -> Cora contract administration
  -> authorized Cursor contractor implementation + its own tests
  -> Saul/Codex independent CTO review
  -> Sai exact-state governance review
  -> Human final merge authority
```

The Runtime Intelligence plane runs in parallel:

```text
GitHub/runner events
  -> Hermes runtime/SRE lane
  -> Grok adversarial/comparative lane
  -> runtime experiments + telemetry + findings
  -> issues / governed sub-PRs / PR comments / memory summaries
  -> Sai routes material findings to the correct owner
```

Runtime Intelligence **supplements but never replaces** Cursor contractor testing, repository CI, Saul CTO review, Sai governance review, or human merge authority.

## Hermes role

Hermes is the persistent Hostinger Runtime Reliability / SRE worker. Its primary responsibilities are runtime health, GitHub Actions observation, experiment orchestration, telemetry, time-series comparisons, dashboard data, local operational memory, issue creation, and governed support sub-PRs.

## Grok role

The Grok Telegram bridge is the adversarial/comparative Runtime Intelligence worker. It challenges measured health, designs bypass/fuzz/state-machine tests, compares runtimes on common workloads, interprets telemetry, and may create structured findings/issues/support sub-PRs. It does not replace Saul, Sai, Cora, or Cursor contractor authority.

## Non-blocking invariant

Hermes/Grok work never becomes a synchronous prerequisite for ordinary Cursor development. Its outputs become blocking only when existing SAI severity/governance policy makes the underlying finding blocking.

## Issue-first and support sub-PR workflow

Reproducible defects use issue-first coordination. If authorized and useful, Runtime Intelligence creates a dedicated support branch and **stacked/sub-PR** tied to the issue and parent implementation PR.

Unless a co-founder explicitly requests otherwise, Hermes/Grok/OpenClaw are subprocess runners and may not create a top-level PR targeting `main`. Their code-changing PRs default to the active parent implementation branch as base. They may comment on the parent PR with evidence and next-action handoffs, but never treat that comment as approval.

Runtime Intelligence agents never merge, force-push, close protected work, mark PRs ready, rewrite history, bypass review gates, or merge any branch to `main`.

## Cursor-token exhaustion fallback

If GitHub, Telegram, Slack, Cursor, or a co-founder explicitly indicates the primary Cursor contractor/runtime exhausted token/usage capacity, Runtime Intelligence may continue clearly scoped, mechanically reconstructable support work from the exact task/contract/PR/head in a stacked sub-PR. It may create/improve reusable skills, but may not impersonate Cursor or silently become canonical implementation. Work remains provisional until normal tests, CI, Saul, Sai, and human validation.

## Runtime experiments and graphs

Tests must begin from a complete exact PR head, GitHub merge ref, or explicitly integrated worktree. Loose/unintegrated patches may not be represented as PR tests.

Experiments record time-series data where measurable: timestamps, experiment ID, repo/PR/base/head, contract revision, runtime/model/agent, state transitions, tests, latency/retries, runner state, CPU/memory, token/cost, authorization/stale events, workflow disposition, and finding IDs/severity.

A graph-proven failure opens/updates an issue and may generate a concise parent-PR comment that distinguishes measured fact, inference, and proposed remediation.

## Stub index

Runtime Intelligence maintains a SHA-bound structured index of TODO implementations, placeholders, disabled paths, temporary bypasses, and incomplete interfaces. The Sai Wiki is a human-readable projection, never the sole machine source of truth.

## Memory architecture

- Tier 1: Hostinger local operational memory for raw/high-frequency telemetry and runtime working memory.
- Tier 2: Git-backed durable semantic organizational memory for incidents, experiments, findings, stubs, benchmarks, patterns, and architecture lessons.
- Tier 3: Sai Wiki human projection generated from structured memory.

High-frequency samples are not committed to Git per sample. Hostinger telemetry feeds the live SAI Control Tower; material completed results are promoted to semantic Git memory and Wiki/issue/PR evidence.

## ICM

Every material Runtime Intelligence experiment/support task follows the six-stage ICM contracts and distinguishes measured fact, derived metric, inference, proposal, and uncertainty.

## Amendment 2026-08-13 — subprocess initialization, Grok reasoning container, OpenClaw

Hermes, Grok, and OpenClaw are formally **subprocess Runtime Intelligence runners**, not top-level SAI officers.

Their canonical coordination files live under:

```text
.ai/shared/skills/runtime-intelligence/
  SKILL.md
  TRIAGE.yaml
  MEMORY_ARCHITECTURE.md
  OPERATING_MANUAL.md
  TELEGRAM_BOOTSTRAP_PROMPT.md
```

### Grok execution

After bootstrap, substantive Runtime Intelligence Grok execution must run in a dedicated Dockerized service using the newest stable reasoning-capable Grok model actually supported at runtime, not a fast/non-reasoning model for final findings. As of this amendment, xAI documentation identifies `grok-4.5` / `grok-4.5-latest` as the current general coding/agentic model and supports high reasoning effort. Runtime setup must verify the current production target rather than assume a stale model name.

If Hermes/Grok cannot safely complete Docker/model setup, they may ask the already-authenticated local Hostinger Codex CLI for implementation assistance inside the governed initialization/support sub-PR. Such assistance is not Saul approval.

### OpenClaw

The existing Hostinger OpenClaw container is a bounded background assistant for heartbeat monitoring, event normalization/deduplication, experiment scheduling, queueing, local-memory maintenance, dashboard refresh, and low-risk notifications. It receives no independent approval, contract, top-level PR, merge, or officer authority.

### Organizational initialization gate

Hermes/Grok/OpenClaw must initialize through SAI conventions in a stacked initialization sub-PR and remain PROVISIONAL until the exact initialized state proves:

- `.ai` initialization, hooks/rules, verified capabilities, and ICM artifacts;
- Dockerized high-reasoning Grok path and bounded `/deep` integration;
- bounded OpenClaw role;
- Hostinger local memory and dashboard;
- integrated-state test harness;
- negative tests denying merge/force-push/mark-ready/top-level-authority behavior;
- **Saul technical approval** of the exact initialization revision/SHA via the formal Codex CTO path;
- **Sai governance approval** of that same exact state;
- **explicit human/co-founder approval** for organizational admission.

Blockers are recorded in the initialization sub-PR and routed to Sai for governance triage. A blocker never authorizes the subprocess to open a new top-level PR or bypass the parent loop.

## Human authority

Neither Hermes, Grok, nor OpenClaw may ever merge any branch to `main` or substitute for Cursor contractor tests, CI, Saul review, Sai verification, authority-expansion approval, or final human merge approval.

Their mandate is to increase throughput and observability in parallel, preserve durable evidence/memory, and propel the primary loop through intelligent issues, comments, and stacked support PRs without becoming another sequential gate.