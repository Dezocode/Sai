# Intake — Cora A-009 / v9 for PR #62

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`, acting for dezocode
(U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) via grant-pr62-queue-cora.

Exact requested outcome: consume Saul REQUEST_CHANGES run 31763018964
(comment 5288630796) on exact head
`9382d1fdbf3f878983db8b8beb4ce4bfb83f98b2`, contract revision 8,
codex_invoked true, synthetic false. Issue immutable A-009 → v9.
Reuse `ctr-code-pr62smoke` and `lease-c3a003pr62q1`. Do not expand
allowed_paths. denied_paths unchanged (keep `.ai/authorizations/**`).
Bump lease revision to v9. Keep lease.task_id
`20260813-2017-pr62-queue-ctr-code`. Set `cora_admin_complete: true`
on v9 (administration complete for this wave, not technical PASS).
Commit trailers MUST use original grant Task-ID
`20260813-2016-pr62-queue-cora`. Do not implement scripts. Do not
PASS. Do not merge. Do not write blockers items (contractor). Do not
write `.ai/authorizations` pins (Sai/officer). Do not write
`.ai/_config`.

## Repository facts (command-backed)

- Repository: Dezocode/Sai (origin fetch/push).
- Default branch: main (`40efe0a` at intake; origin/main has
  `.github/workflows/agent-audit.yml` only — no `saul-review.yml`).
- Working branch: `cursor/codebase-health-90ba`.
- Fetch: `git fetch origin cursor/codebase-health-90ba` then
  `git fetch origin main`.
- Qualifying Saul head: `9382d1fdbf3f878983db8b8beb4ce4bfb83f98b2`
  (CTO-028 officer-file loader on HEAD; Saul REQUEST_CHANGES for
  missing pin provenance).
- Assumed identity: `scripts/sai-assume-agent ctr-admin --task-id
  20260813-2016-pr62-queue-cora` → grant `grant-pr62-queue-cora`.
- icm-enforcement already SUCCESS on 9382d1f after Saul snapshot
  (agent-audit 31763018953 pull_request and 31763016803 push). That
  is not technical PASS.

## Constraints

- Cora writes contract/lease/run artifacts only.
- Reuse contractor + lease. No path expansion. denied_paths unchanged.
- Officer (Sai) already added `introduced_by_sha` / `source` /
  `source_head` on the pin file at `e84e5d7`. Cora does not write
  `.ai/authorizations`.
- Contractor enforces provenance in the verifier and appends CTO-029
  without PASS.
- CTO-025 stays open BLOCKED_EXTERNAL (main has no trusted workflow).
- CTO-026 stays uncleared.
- Preserve unstaged other-agent files (generated human-gate.yaml,
  prior Cora 04_verify/).

## Acceptance (this Cora slice)

A-009 and v9 exist; contract.json current_revision is v9; lease
reused and bound to v9; cora_admin_complete true; implements false;
do_not_merge true; no technical PASS claimed.
