# Plan — Cora A-012 / v12 for PR #62

Qualifying Saul run 31771910025 comment 5289717183 on exact head
`4503f55250efde4166e4877473d4a9268b37c166`: REQUEST_CHANGES,
codex_invoked true, synthetic false, runner hostinger-saul-codex,
contract_revision 11, event pull_request. ICM agent-audit SUCCESS
after Saul (31771910146 pull_request, 31771907870 push) is not
technical PASS.

Issue immutable A-012 → v12 in A-011 style. Do not run
`scripts/consume-saul-contract-review` (mechanical output would
omit contractor-authorization notes and stale the lease). Record
the real Saul YAML as consumed-08c26942e30d3e7c.yaml. Reuse
contractor ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand
allowed_paths. denied_paths unchanged. Bump lease + contract.json
to v12 only. Keep lease.task_id `20260813-2017-pr62-queue-ctr-code`
and existing task_ids. authority_expanding false.

This commit uses original grant Task-ID `20260813-2016-pr62-queue-cora`
so authorization PASSES without HEAD-union and without a contractor
HEAD pin.

A-012 is REQUIRED_FOR_CURRENT_BLOCKER (CTO-021 persistent-runner
trust boundary after trusted pull_request_target activation). A-011
skip-guard inside candidate-controlled `saul-review.yml` is
insufficient: a future collaborator PR can delete or bypass the
guard. Not a waiver. Not path expansion.

Findings bound, not PASSED:

- CTO-030 P0 saul_review_workflow narrow: merge-activated state
  must have no candidate-controlled persistent-runner invocation
  path. Preferred: delete `.github/workflows/saul-review.yml`, OR
  convert it so it has neither `runs-on: self-hosted` nor any
  trigger that can acquire Hostinger (`pull_request` /
  `workflow_dispatch` + self-hosted). Keep/harden
  `.github/workflows/saul-cto-review.default-branch.yml` as the
  only self-hosted Saul workflow: `pull_request_target` (executable
  from default branch after merge) + `workflow_dispatch` with a
  **job-level `if:`** evaluated before runner assignment so a
  feature-branch dispatch does not acquire Hostinger.
  `pull_request_target` from same-repo PRs remains allowed. Do not
  add `on: pull_request` to the trusted file. Candidate remains
  DATA (`path: candidate-data`, persist-credentials false, never
  execute candidate scripts). No allow-unsafe-pr-checkout. No
  candidate-HEAD trust. Retarget tests that parse `saul-review.yml`
  at the trusted default-branch file and/or assert `saul-review.yml`
  is absent or cannot acquire self-hosted. Do not grow
  `sai_auth_review.py` (500) or `sai_auth_test.py` (~497) — only
  tiny path edits or move fixtures to `sai_auth_saul_test.py` /
  `sai_auth_workflow_trust_test.py`. Contractor updates
  `.ai/_config/authorization.yaml` workflow pointer.
- CTO-025: may stay IMPLEMENTED_AWAITING_SAUL with a history note
  that CTO-030 supersedes the skip-guard as the remaining
  runner-boundary defect. Do not PASS.
- CTO-031 P1 human_gate: green required CI for exact head 4503f55
  is not technical PASS. Package said pending. After A-012, new
  SHA will need its own CI. Do not PASS.
- CTO-026: keep uncleared. Do not rework 015..021/024/028/029.
- REQ-5289020312: this-PR Hostinger continuity is last qualifying
  Saul 31771910025 on 4503f55. After removing the candidate
  self-hosted `pull_request` workflow, this Cloud `gh` cannot
  `workflow_dispatch` (actions=read / 403). Do not leave Dezocode
  a required dispatch chore as the only path. The merge-activated
  trusted `pull_request_target` is the post-merge review path. Do
  not fake origin/main.

Cora does not implement. Cora does not write blockers items,
scripts, workflows, tests, decisions, `.cursor`, `.ai/_config`,
or `.ai/authorizations`. YAML ≤300 lines. Do not restore
candidate-HEAD trust. Do not merge. Do not push. Do not mark ready.

Files claimed: A-012.yaml, v12.yaml, contract.json, lease
(revision bump only), requirements/ledger.yaml (append
REQ-CTO-030), consumed-08c26942e30d3e7c.yaml, this run directory,
standing-run handoff append.
