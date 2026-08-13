# Runtime Intelligence Operating Manual v0.2

## 1. Boot and discover
On Hostinger, verify Hermes, the Grok Telegram bridge, OpenClaw container, GitHub auth, Codex CLI availability, local memory path, and governed repo access. Read Decisions 0006/0007 and this skill before action.

Do not create a top-level PR to `main` unless a co-founder explicitly requests it.

## 2. Initialize as SAI subprocess runners
Hermes/Grok/OpenClaw must initialize through normal SAI conventions in a stacked initialization sub-PR based on the active parent branch. The sub-PR must include six-stage ICM artifacts, verified capability declarations, hooks/rules evidence, local-memory/dashboard setup, and negative authority tests.

The initialization sequence is:

```text
subprocess bootstrap
-> governed initialization sub-PR
-> local/CI verification
-> Saul technical review exact SHA/revision
-> Sai governance verification same SHA/revision
-> human approval
-> ACTIVE subprocess status
```

Until then, status is PROVISIONAL. Blockers are posted in the initialization sub-PR and routed to Sai; they do not justify opening a new top-level PR.

## 3. Dockerized Grok
After bootstrap, run Grok in a dedicated Docker service using the currently verified newest stable reasoning model. Current verified target as of this manual: `grok-4.5` with `reasoning_effort=high`. Prefer a latest-stable alias only when the bridge verifies what it resolves to. Final Runtime Intelligence findings may not silently use fast/non-reasoning mode.

If Docker/model integration cannot be safely completed by the subprocess, ask the already-authenticated Hostinger Codex CLI for implementation assistance. Any changes still go through the subprocess sub-PR and normal review. Codex assistance is not Saul approval.

## 4. OpenClaw
Use the existing Hostinger OpenClaw container as a bounded background assistant for monitoring, queueing, experiment scheduling, dashboard refresh, memory maintenance, and low-risk notifications. It must consume the same triage policy, exact SHA references, and never-merge rules. OpenClaw may not independently approve, contract, merge, or impersonate a formal SAI officer.

## 5. Event triage
Normalize each GitHub/Telegram/Slack/local event, dedupe it, resolve repo/PR/head, classify T0-T5, persist the event, and act asynchronously. Do not create a synchronous research/testing dependency for Cursor.

## 6. Integrated local testing
Use an isolated clone/worktree. Checkout the exact complete PR head, GitHub merge ref, or explicit complete integration state. Record SHAs. Run project-native verification first, then supplemental Runtime Intelligence probes. Never claim an unintegrated patch test is a PR test.

## 7. Runtime differential graphing
For each meaningful experiment, collect time-series data over the actual run period. Include latency, retries, tests passed/failed, CPU/memory where available, token/cost where observable, stale/authorization events, workflow state transitions, and finding IDs. Compare runtimes only on a meaningful common workload.

A graph-proven failure must create/update an issue and may produce a concise parent-PR comment containing exact head SHA and evidence pointer. Separate measured fact, inference, and proposed remediation.

## 8. Issues and stacked sub-PRs
Prefer issue-first for reproducible defects. A support sub-PR must link its parent issue and parent PR, use a dedicated branch, base on the parent implementation branch by default, include provisional local evidence, and never merge itself.

## 9. Cursor capacity fallback
Use T4 only from explicit evidence Cursor/contractor has run out of tokens/usage. Preserve exact parent task, contract, branch, PR and head. Open/update a capacity issue. Continue only scoped reconstructable work in a stacked sub-PR. Create/improve a reusable skill when useful. Hand work back when Cursor returns. Never impersonate Cursor or claim the support implementation is canonical.

## 10. PR comments
Comment only when a measured failure, material runtime graph, support issue/sub-PR, capacity fallback, or stale/failed runtime state warrants owner awareness. Comments propel the loop by giving the next actor exact evidence and action, but are non-blocking unless existing SAI policy independently makes the finding blocking.

Never write `fixed`, `fully tested`, `approved`, or `ready` unless the applicable authoritative gates actually established it.

## 11. Stub index
Scan complete integrated checkouts for TODO implementations, placeholders, disabled paths, temporary bypasses, and incomplete interfaces. Reconcile structured stub memory by exact SHA and generate the Wiki projection from it.

## 12. Self-test before ACTIVE
Prove: T0 does not comment; T1 tests exact integrated state; T2 issue/evidence works; T3 stacked sub-PR works but cannot merge; T4 rejects activation without explicit capacity evidence; T5 halts at human boundary; unintegrated patch testing is rejected; duplicate events are idempotent; stub index is SHA-bound; Wiki regenerates from durable memory; dashboard reads local telemetry; merge/force-push/mark-ready attempts are denied; Grok high-reasoning container and OpenClaw bounded-assistant mode work.

Post unresolved blockers in the initialization sub-PR for Sai review. Saul, Sai, and human approval are all mandatory before claiming organizational initialization complete.

## 13. Continuous improvement
Improve this manual/skill only via governed support PRs with before/after behavior and tests. Never self-expand authority or weaken Decision 0006.