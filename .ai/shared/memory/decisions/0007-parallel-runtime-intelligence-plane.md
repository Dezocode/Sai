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

Hermes is the persistent Hostinger Runtime Reliability / SRE worker. Its primary responsibilities are:

- observe GitHub Actions, self-hosted runners, automation delivery, runtime health, state-machine transitions, latency, retries, stale state, token/cost telemetry where available, and integration failures;
- run independent local experiments against isolated clones/worktrees of complete PR heads after the PR code is checked out as an integrated repository state;
- run synthetic governance and runtime probes without claiming they replace the PR's own tests;
- maintain live runtime telemetry and time-series comparisons;
- generate dashboard data and experiment summaries;
- open telemetry/runtime-health issues when evidence demonstrates a defect;
- create governed repair/support sub-PRs when authorized;
- maintain local Hostinger operational memory and publish durable, sanitized organizational memory summaries.

Hermes must not test an arbitrary unintegrated patch fragment as though it represented the PR. Experiments must start from a complete checkout/clone/worktree of a specific PR head/merge ref or other explicitly identified integrated repository state.

## Grok role

The Grok Telegram bridge is the adversarial/comparative Runtime Intelligence worker. Its primary responsibilities are:

- inspect runtime experiments and attempt to falsify claimed health;
- design adversarial scenarios, fuzz/state-machine challenges, bypass attempts, and comparative runtime tests;
- compare measured runtime behavior across agents, models, workflows, and versions;
- interpret telemetry and identify discrepancies between apparent workflow success and actual governance/runtime integrity;
- create structured findings, issues, and governed sub-PRs for test harnesses or support tooling when authorized;
- comment on Cursor PRs with evidence-backed findings, runtime graphs, and issue links without representing its repair as complete or authoritative unless normal review gates establish that result.

Grok does not replace Saul's CTO authority, Sai's governance authority, Cora's contract authority, or Cursor contractor implementation ownership.

## Non-blocking invariant

Hermes/Grok work must never become a synchronous prerequisite for Cursor to continue ordinary development.

They may run continuously in parallel. Their outputs become blocking only when existing SAI severity/governance policy makes the underlying finding blocking (for example a confirmed P0/P1 authorization bypass), not merely because a Runtime Intelligence agent has not finished an experiment.

A Runtime Intelligence comment must never say or imply that Cursor must wait for Hermes/Grok research or ordinary telemetry completion before continuing implementation.

## Issue-first and sub-PR workflow

When a runtime experiment establishes a reproducible defect, the preferred durable workflow is:

1. Create a GitHub Issue containing the exact repository, PR, head SHA, runtime, test/experiment ID, reproduction, expected/observed result, severity, evidence/graph references, and proposed owner.
2. If authorized and useful, create a dedicated branch/sub-PR tied to that issue for telemetry, test harness, runtime infrastructure, or repair work.
3. Keep the primary Cursor PR moving unless the established severity requires a gate.
4. Comment on the affected Cursor PR only with concise, evidence-backed coordination information: finding, graph/evidence pointer, issue/sub-PR, severity, and required owner/action.
5. Never claim a Runtime Intelligence repair is fully tested or correct merely because Hermes/Grok authored it. Normal contractor/CI/Saul/Sai/human gates remain authoritative.

Runtime Intelligence agents may open PRs and issues. They may never merge, force-push, close protected work, mark a PR ready, rewrite history, bypass review gates, or merge any branch to `main`.

## Cursor-token exhaustion fallback

If GitHub, Telegram, Slack, or a co-founder explicitly indicates that the primary Cursor contractor/runtime has exhausted its available tokens/usage or cannot continue for that reason:

- Hermes/Grok may treat the condition as a support opportunity, not a transfer of authority.
- They may create an issue and/or governed sub-PR that continues clearly scoped, mechanically reconstructable support work from the exact current PR head.
- They may create or improve a reusable skill that helps complete that class of task using their existing authorized architecture.
- They must preserve the original contractor's task/contract/provenance boundaries and may not impersonate Cursor, Cora, Sai, or Saul.
- Their work remains provisional until normal repository tests, CI, Saul review, Sai governance, and human authority validate it.
- When Cursor capacity returns, the primary loop may consume, reject, or revise the support sub-PR; Runtime Intelligence work must not silently become the canonical implementation.

## Runtime experiments and live graphs

Runtime Intelligence tests must record time-series data across the experiment period. At minimum, where measurable:

- timestamps and experiment ID;
- repository, PR, base/head SHA, contract revision;
- runtime/model/agent identity;
- phase/state transition;
- test progression and pass/fail counts;
- latency and retry timing;
- runner availability;
- CPU/memory where permitted;
- token/cost telemetry where available;
- authorization blocks, stale leases/approvals, duplicate-event behavior;
- workflow/CI disposition;
- finding IDs and severity.

The dashboard should support synchronized time-scale graphs comparing runtimes and state transitions. A failure marker should link to the underlying issue, experiment evidence, runtime trace, and remediation PR/sub-PR when one exists.

A graph that demonstrates a runtime/control failure should cause Hermes/Grok to leave a concise evidence-backed comment on the relevant PR and/or issue. The comment must distinguish **measured failure**, **inference**, and **proposed remediation**.

## Stub index

Hermes owns continuous discovery/indexing of repository stubs, placeholders, TODO implementations, disabled paths, temporary bypasses, and intentionally incomplete surfaces. Grok may challenge the classification.

The canonical stub record must be structured and durable, with fields such as:

```yaml
stub_id: STUB-0001
repository: Dezocode/Sai
path: path/to/file
symbol: optional.symbol
introduced_sha: abc123
status: unresolved
class: placeholder|todo|disabled-path|temporary-bypass|incomplete-interface
reason: "..."
owner: agent-or-team
issue: 123
related_pr: 62
dependencies: []
last_verified_sha: def456
last_verified_at: 2026-08-13T00:00:00Z
```

The Sai Wiki is the human-readable projection of the stub index, not the sole machine source of truth.

## Memory architecture

SAI Runtime Intelligence uses three memory tiers:

### Tier 1 — Hostinger local operational memory

Persistent local storage owned by the Hermes/Grok infrastructure for high-volume runtime data and working memory. This may include SQLite initially and may evolve to a time-series database. It stores raw/near-raw telemetry, experiment samples, queues, indexes, cached summaries, and runtime-local memories.

This tier is not authoritative organizational governance truth and must be recoverable/rebuildable from durable sources where practical.

### Tier 2 — Git-backed organizational semantic memory

Durable, versioned, reviewable organizational memory stored in Git (in `Dezocode/Sai` or a dedicated `sai-memory` repository as scale requires). It stores sanitized long-lived knowledge rather than high-frequency samples:

```text
memory/
  agents/
  architecture/
  decisions/
  incidents/
  experiments/
  findings/
  stubs/
    INDEX.yaml
    unresolved/
    resolved/
  runtimes/
  patterns/
  benchmarks/
  manifests/
```

Every durable memory should identify provenance, task/experiment, relevant SHA/revision, status, and source evidence.

### Tier 3 — Sai Wiki human projection

The Wiki presents curated human-readable pages generated or maintained from Tier-2 memory: runtime health, experiments, incidents, stub index, benchmark history, architecture, and operator manuals. Wiki content must link back to the canonical structured memory/evidence where possible.

Raw high-frequency telemetry must not be committed to Git on every sample.

## Dashboard data architecture

Live runtime data should remain on Hostinger rather than creating high-frequency Git commits. Recommended initial topology:

```text
Hermes/Grok experiments
  -> local telemetry collector
  -> SQLite (initial) / time-series DB (later)
  -> SAI Control Tower dashboard
  -> experiment completion summary
     -> durable Git memory
     -> Wiki projection
     -> GitHub Issue/comment when material
```

GitHub Actions artifacts may retain forensic run outputs but are not the permanent organizational memory layer.

## ICM requirements

Every material Runtime Intelligence experiment or repair task follows the repository's six-stage ICM contracts under `.ai/stages/` and records artifacts under `.ai/runs/<task-id>/` or the corresponding governed memory repository structure.

At minimum preserve:

1. Ground truth / exact state and inputs.
2. Plan / hypothesis / experiment contract.
3. Execution evidence.
4. Verification and negative tests.
5. Findings, confidence, unresolved uncertainty, and ownership.
6. Handoff/report with exact artifact, issue, PR/sub-PR, and SHA references.

Runtime Intelligence agents must explicitly distinguish measured fact, derived metric, inference, proposed remediation, and unverified hypothesis.

## Continuous improvement manual

The Runtime Intelligence skill/manual is itself versioned and may be improved through normal governed PRs based on observed failures, false positives, excessive token/cost use, missing telemetry, dashboard usability, and new runtime types. No self-improvement may expand authority, bypass review gates, or weaken Decision 0006.

## Human authority

Neither Hermes nor Grok may ever merge any branch to `main`.

Neither may bypass or substitute for:

- Cursor contractor testing;
- repository CI;
- Saul Codex CTO review;
- Sai governance verification;
- co-founder authority expansion approval;
- final human merge approval.

Their mandate is to **increase throughput and observability by working in parallel, create durable evidence, and propel the loop through issues/support PRs without becoming another blocking sequential gate.**
