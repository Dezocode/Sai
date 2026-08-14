# Intake — Cora A-008 / v8 for PR #62

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`, acting for dezocode
(U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) via grant-pr62-queue-cora.

Exact requested outcome: consume Saul REQUEST_CHANGES run 31761796169
(comment 5288500483) on exact head
`f4443fa0b00ec950768ba7aff14020732e338e9d`, contract revision 7,
codex_invoked true, synthetic false. Issue immutable A-008 → v8.
Reuse `ctr-code-pr62smoke` and `lease-c3a003pr62q1`. Do not expand
allowed_paths. Optionally add denied_paths `.ai/authorizations/**`
(narrow). Bump lease revision to v8. Keep lease.task_id
`20260813-2017-pr62-queue-ctr-code`. Set `cora_admin_complete: true`
on v8 (administration complete for this wave, not technical PASS).
Commit trailers MUST use original grant Task-ID
`20260813-2016-pr62-queue-cora`. Do not implement scripts. Do not
PASS. Do not merge. Do not write blockers items. Do not write
`.ai/authorizations` (Sai/officer). Do not write `.ai/_config`.

## Repository facts (command-backed)

- Repository: Dezocode/Sai (origin fetch/push).
- Default branch: main (`40efe0a` at intake; origin/main has
  `.github/workflows/agent-audit.yml` only — no `saul-review.yml`).
- Working branch: `cursor/codebase-health-90ba`.
- Fetch: `git fetch origin cursor/codebase-health-90ba` then
  `git fetch origin main`.
- Qualifying Saul head: `f4443fa0b00ec950768ba7aff14020732e338e9d`
  (contractor SHA-bound `_config` pins; Saul REQUEST_CHANGES).
- Officer SHA after fetch while Cora oriented:
  `2a578424f4879f2bad4e4391deff5f30231db19f`
  (`Record officer SHA-bound pins for CTO-028`). Cora does not
  rewrite that tree.
- Assumed identity: `scripts/sai-assume-agent ctr-admin --task-id
  20260813-2016-pr62-queue-cora` → grant `grant-pr62-queue-cora`.

## Constraints

- Cora writes contract/lease/run artifacts only.
- Contractor already lacks `.ai/authorizations/**` in allowed_paths;
  adding it to denied_paths is a narrow, not an expand.
- Officer pins already exist at 2a57842 under
  `.ai/authorizations/sha-bound-authorization.yaml`.
- CTO-025 stays open BLOCKED_EXTERNAL (main has no trusted workflow).
- CTO-026 stays uncleared.
- CTO-027 P1: icm-enforcement SUCCESS on f4443fa (agent-audit runs
  31761796108 pull_request and 31761793891 push); still not technical
  PASS.
- Preserve unstaged other-agent files (Sai events.jsonl, prior Cora
  events.jsonl, generated human-gate.yaml).

## Acceptance (this Cora slice)

A-008 and v8 exist; contract.json current_revision is v8; lease
reused and bound to v8; cora_admin_complete true; implements false;
do_not_merge true; no technical PASS claimed.
