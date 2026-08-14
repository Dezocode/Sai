# Intake — Cora A-011 / v11 for PR #62

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`, acting for dezocode
(U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) via grant-pr62-queue-cora.
This named child: Cora, agent_id `ctr-admin`, physical runtime
`bc-861780d2-a032-5b8e-9b41-b8bff05bee89`.

Exact requested outcome: issue immutable A-011 → v11 (copy A-010/v10
style). Not a Saul consume. Do not run
`scripts/consume-saul-contract-review`. Reuse `ctr-code-pr62smoke`
and `lease-c3a003pr62q1`. Do not expand allowed_paths. denied_paths
unchanged. Bump lease + contract.json to v11 only. Keep lease.task_id
`20260813-2017-pr62-queue-ctr-code`. Set `cora_admin_complete: true`
on v11 (administration complete for this wave, not technical PASS).
Commit trailers MUST use original grant Task-ID
`20260813-2016-pr62-queue-cora`. Do not implement scripts/workflows.
Do not PASS. Do not merge. Do not push. Do not mark ready. Do not
write blockers items. Do not write decisions or `.cursor`. Do not
write `.ai/authorizations`. Do not put tokens in files.

## Why A-011 (not a waiver)

A-010 assumed remaining this-PR Saul reviews could use
`workflow_dispatch`. That assumption is false for this runtime.
Primary attempted `gh workflow run saul-review.yml --ref
cursor/codebase-health-90ba` and got HTTP 403 Resource not accessible
by integration. Token accepted permissions are actions=read only
(`X-Accepted-Github-Permissions: actions=read`). This Cloud `gh`
cannot create workflow_dispatch events. All prior qualifying Saul
runs were `event: pull_request` (GitHub auto-trigger), never agent
dispatch. Empty frontier while needing Saul would force a human to
dispatch — principal P0 5289020312 forbids leaving Dezocode an
intermediate chore. Restore a narrow `on: pull_request` so GitHub
auto-starts Saul on the next SHA, AND add a post-merge skip guard so
once the trusted file exists on origin/main, the transitional job
must NOT invoke Codex. Trusted `pull_request_target` file still
merges as the activation path. REQUIRED_FOR_CURRENT_BLOCKER (Saul
continuity + merge-activation invariant), not path expansion.

## Repository facts (command-backed)

- Repository: Dezocode/Sai (origin fetch/push).
- Default branch: main (`40efe0a` at intake). origin/main
  `.github/workflows/` contains only `agent-audit.yml` — no trusted
  `saul-cto-review.default-branch.yml`.
- Working branch: `cursor/codebase-health-90ba`.
- HEAD: `6ad1dc6bf6b0727b1bd4581695667ed6cfd7c2dc` (matches origin).
- A-010/v10 already issued. Sai amended Decision 0008 at `121430d`.
  Contractor packaged merge-activation at `6ad1dc6`.
- ICM `agent-audit` SUCCESS on `6ad1dc6`: run 31770830268
  (pull_request) and 31770828271 (push).
- No Saul run exists on `6ad1dc6`. Latest Saul is still 31764010391
  on old head `c51c9cf`, event `pull_request`.
- Assumed identity: ctr-admin under grant-pr62-queue-cora.
- Do not rework IMPLEMENTED_AWAITING_SAUL items.

## Constraints

- Cora writes contract/lease/run artifacts only.
- Reuse contractor + lease. No path expansion. denied_paths
  unchanged (`.ai/agents/saul/**`, `.ai/shared/memory/decisions/**`,
  `.ai/authorizations/**`).
- Decision 0008 already covers merge-activation; a one-sentence 0008
  note is OPTIONAL and is Sai's job, not Cora's.
- YAML files must stay ≤300 lines.
- Contractor may append a short note on the CTO-025 item; Cora does
  not write blockers/items.

## Acceptance (this Cora slice)

A-011 and v11 exist; contract.json current_revision is v11; lease
reused and bound to v11; cora_admin_complete true; implements false;
do_not_merge true; do_not_push true; technical_pass false; no
technical PASS claimed; CTO-025 and B-META-P0-001 not PASSED; no
path expansion; A-011 reason = dispatch 403 / actions=read.
