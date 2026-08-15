# 0010 — CEO self-trigger loop guard for PR-triggered automations

- Date: 2026-08-15
- Task-ID: 20260815-2059-ceo-selftrigger-loop-guard-ceo
- Status: accepted
- Approver: n/a (governance/protocol fix within Sai CEO charter, Section H
  "Automation Health / Self-Healing"); flagged for dezocode/monaecode review
  via `#agentupdates`.

## Decision

The Sai CEO automation, and any other CEO/primary logical identity operating
under `.cursor/rules/sai-orchestration.mdc`, must not push a
governance-bookkeeping-only commit (one that updates only
`.ai/runs/**/coordinator-state.json`, `.ai/runs/**/events.jsonl`, or
`.ai/runs/**/handoff.md`, with no change to implementation head, contract
revision, Saul disposition, or required-CI conclusion) to a branch watched by
a PR `synchronize`/`opened`/`reopened` automation trigger, unless that push
is bundled with an actual material transition. When a wake is caused by
exactly such a self-authored bookkeeping commit, the event must be classified
`NOOP / DUPLICATE` on inspection and must not itself produce another
standalone bookkeeping commit.

## Context

While processing the PR `synchronize` trigger for
[Dezocode/Sai#62](https://github.com/Dezocode/Sai/pull/62) at head
`39849733cdae9b072761a6a091afdf085bbdac10`, this Sai CEO run found that the
new head was itself authored by the CEO agent identity
(`Task-ID: 20260813-2015-pr62-queue-ceo`, commit message "Keep pr62-primary
nonterminal after Ralph liveness integrate") and only touched
`.ai/runs/20260813-2015-pr62-queue-ceo/{coordinator-state.json,events.jsonl,handoff.md}`.
The recorded `implementation_head` (contractor SHA `c5a05b1`), Saul
disposition (`pending`/`WAITING_EXTERNAL_REAL_SAUL`, structurally blocked by
the known `SAUL-BOOTSTRAP-TREE-001` bootstrap condition until a human merges
PR #62), and required CI conclusion (`icm-enforcement`: `SUCCESS`) were
unchanged from the prior recorded state in
`.ai/runs/20260813-2015-pr62-queue-ceo/coordinator-state.json`.

Pushing that "still nonterminal" bookkeeping commit to
`cursor/codebase-health-90ba` (the PR #62 head branch) is itself a push to a
`pull_request`-watched branch, which re-fires this same PR `synchronize`
automation. If each firing again concludes "still nonterminal" and commits
that conclusion, the loop is self-sustaining and produces unbounded CEO
reasoning runs with no corresponding material state transition — precisely
the regression the Material-Event Wake Policy (Decision 0009) calls out as
an orchestration defect to fix, not tolerate.

## Alternatives considered

1. **Do nothing; rely on the existing material-event wake policy text.** The
   policy already defines "implementation HEAD SHA changed" as material, but
   does not distinguish a contractor implementation SHA from a CEO's own
   bookkeeping-only SHA on the same branch, which is exactly the gap that let
   this loop occur. Insufficient on its own.
2. **Never let the CEO commit anything to a PR-watched branch.** Too broad —
   legitimate governance transitions (e.g. recording a genuine Saul
   disposition change) do need to be committed and are part of the audited
   trail.
3. **Add an explicit guard distinguishing self-authored, bookkeeping-only,
   non-material commits from real transitions, and require batching or
   suppression of standalone pushes for the former.** Chosen: narrow, keeps
   the audit trail for real transitions, and is squarely a governance/
   protocol fix within the CEO charter (no contractor/Cora/Saul role
   assumed).

## Rationale

Sai's own governing text (Section P, "No busy loops / no token-wasting
polling", and the Metrics section, "A regression where Sai reasoning runs
increase without corresponding material state transitions must be treated
as an orchestration defect") already commits Sai to detecting and fixing
exactly this class of problem when found within its own charter. This
decision operationalizes that commitment as a concrete, checkable rule
instead of leaving it as prose that a future CEO run can rationalize past.

## Consequences

- Future CEO/primary runs must check commit authorship + changed-path scope
  before treating a new head SHA on a watched branch as material, in
  addition to comparing the state key fields.
- This does not weaken any Saul/Sai/human review gate: it only suppresses a
  redundant bookkeeping re-commit when nothing reviewable changed.
- This decision does not supersede 0001–0009.
