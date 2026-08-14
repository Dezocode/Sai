# Plan — Cora A-011 / v11 for PR #62

Operational evidence on exact head
`6ad1dc6bf6b0727b1bd4581695667ed6cfd7c2dc`: Cloud `gh workflow run
saul-review.yml` HTTP 403; accepted permissions actions=read; no
Saul run on 6ad1dc6; ICM agent-audit SUCCESS (31770830268
pull_request, 31770828271 push). Latest qualifying Saul remains
31764010391 on `c51c9cf`, event `pull_request`. Not a Saul consume.
Do not run `scripts/consume-saul-contract-review`. Do not put tokens
in files.

Issue immutable A-011 → v11 (copy A-010/v10 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand
allowed_paths. denied_paths unchanged. Bump lease + contract.json
to v11 only. Keep lease.task_id `20260813-2017-pr62-queue-ctr-code`
and existing task_ids. authority_expanding false.

This commit uses original grant Task-ID `20260813-2016-pr62-queue-cora`
so authorization PASSES without HEAD-union and without a contractor
HEAD pin.

A-011 is REQUIRED_FOR_CURRENT_BLOCKER (Saul continuity +
merge-activation invariant), not a waiver and not path expansion.
A-010 assumed remaining this-PR Saul reviews could use
workflow_dispatch. That assumption is false for this runtime. Empty
frontier while needing Saul would force a human to dispatch —
principal P0 5289020312 forbids leaving Dezocode an intermediate
chore.

Findings bound, not PASSED:

- REQ-A011-DISPATCH-403: restore narrow `on: pull_request` (types
  opened/synchronize/reopened/ready_for_review) on
  `.github/workflows/saul-review.yml` AND keep `workflow_dispatch`.
  Add fail-closed skip: if
  `origin/main:.github/workflows/saul-cto-review.default-branch.yml`
  exists (or default_branch equivalent), do not invoke Codex; record
  reason `TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN`; exit 0 without
  failing the PR. During this PR, origin/main still lacks that file,
  so Codex still runs (Saul continuity).
- CTO-025: A-011 amends the A-010 retirement mechanism (trigger
  kept, invocation skipped post-merge). Do not PASS. Trusted
  `pull_request_target` file still merges as the activation path.
  Do not fake the trusted file onto origin/main. Do not restore
  candidate-HEAD trust. Do not add allow-unsafe-pr-checkout. Keep
  candidate DATA on the trusted workflow.
- REQ-5289020312 / B-META-P0-001: do not leave Dezocode an
  intermediate dispatch chore. Do not PASS B-META-P0-001.
- Fixtures: replace `candidate-pr-trigger-retired` — candidate MAY
  declare pull_request again; MUST have skip-guard; MUST keep
  workflow_dispatch; trusted MUST still have pull_request_target;
  keep evil-run isolation; keep cto021-not-faked-on-main. Add a
  hermetic fixture proving skip-guard logic without mutating
  origin/main.
- Threat-trace + merge-readiness notes: A-010 full trigger removal
  is operationally incompatible with actions=read; invocation
  auto-retires after merge via skip-guard; residual = future PR
  deleting the guard (collaborator; DEFERRED_NONBLOCKING /
  runner-group UNKNOWN).
- Do not rework CTO-015..021/024/028/029. Do not PASS CTO-025 or
  B-META-P0-001. Contractor may append a short note on the CTO-025
  item. Cora does not write blockers/items.
- Do not grow sai_auth_review.py.
- Officer: Decision 0008 already covers merge-activation at
  `121430d`. Optional one-sentence 0008 note is Sai's job, not
  Cora's. Do not write decisions/.cursor.

Cora does not implement. Cora does not write blockers items,
scripts, workflows, tests, decisions, `.cursor`, or
`.ai/authorizations`. YAML ≤300 lines. Do not restore
candidate-HEAD trust. Do not merge. Do not push. Do not mark ready.

Files claimed: A-011.yaml, v11.yaml, contract.json, lease
(revision bump only), requirements/ledger.yaml (append
REQ-A011-DISPATCH-403), operational evidence receipt
reviews/a011-dispatch-403.yaml, this run directory, standing-run
handoff append.
