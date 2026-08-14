# Intake — Cora A-012 / v12 for PR #62

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`, acting for dezocode
(U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) via grant-pr62-queue-cora.
This named child: Cora, agent_id `ctr-admin`, physical runtime
`bc-062b379c-1aa5-57c0-9323-7f22010f1104`.

Exact requested outcome: consume qualifying Saul YAML from run
31771910025 comment 5289717183 on exact head
`4503f55250efde4166e4877473d4a9268b37c166` and issue immutable
A-012 → v12 in A-011 style. Reuse `ctr-code-pr62smoke` and
`lease-c3a003pr62q1`. Do not expand allowed_paths. denied_paths
unchanged. Bump lease + contract.json to v12 only. Keep
lease.task_id `20260813-2017-pr62-queue-ctr-code`. Set
`cora_admin_complete: true` on v12 (administration complete for
this wave, not technical PASS). Commit trailers MUST use original
grant Task-ID `20260813-2016-pr62-queue-cora`. Do not implement
scripts/workflows. Do not PASS. Do not merge. Do not push. Do not
mark ready. Do not write blockers items.

## Why not consume-script auto-amend

`scripts/consume-saul-contract-review` maps CTO ids to a mechanical
A-012/v12 without contractor-authorization notes, without
lease-reuse (it stales leases), and without A-011-style bind of
merge-activated state, job-level `if:`, test retarget, or
`.ai/_config/authorization.yaml` pointer. A-009 was a real Saul
consume written by hand in that richer style. This wave does the
same. The Saul YAML is still recorded as
`reviews/consumed-08c26942e30d3e7c.yaml`.

## Qualifying Saul (command-backed)

- Comment: https://github.com/Dezocode/Sai/pull/62#issuecomment-5289717183
- Run 31771910025; head `4503f55250efde4166e4877473d4a9268b37c166`
- disposition REQUEST_CHANGES; codex_invoked true; synthetic false
- runner hostinger-saul-codex; contract_revision 11
- idempotency_key 08c26942e30d3e7c; saul_review_key 90688f9c7a497a46
- github_event pull_request
- Findings: CTO-030 P0 (authority_expanding false), CTO-031 P1
  (authority_expanding false)

## Repository facts (command-backed)

- Repository: Dezocode/Sai (origin fetch/push).
- Default branch: main. origin/main `.github/workflows/` contains
  only `agent-audit.yml` — no trusted
  `saul-cto-review.default-branch.yml`.
- Working branch: `cursor/codebase-health-90ba`.
- HEAD: `4503f55250efde4166e4877473d4a9268b37c166` (matches origin).
- A-011/v11 already issued. Contractor skip-guard landed at 4503f55.
- ICM `agent-audit` SUCCESS on 4503f55 after Saul: run 31771910146
  (pull_request) and 31771907870 (push). That is not technical PASS.
- Assumed identity: ctr-admin under grant-pr62-queue-cora.
- Do not rework IMPLEMENTED_AWAITING_SAUL items 015..021/024/028/029.
- Keep CTO-026 uncleared.

## Constraints

- Cora writes contract/lease/run artifacts only.
- Reuse contractor + lease. No path expansion. denied_paths
  unchanged (`.ai/agents/saul/**`, `.ai/shared/memory/decisions/**`,
  `.ai/authorizations/**`).
- YAML files must stay ≤300 lines.
- Contractor appends CTO-030 / CTO-031 blocker items; Cora does
  not write blockers/items.
- Contractor updates `.ai/_config/authorization.yaml` workflow
  pointer; Cora does not write `_config`.

## Acceptance (this Cora slice)

A-012 and v12 exist; contract.json current_revision is v12; lease
reused and bound to v12; cora_admin_complete true; implements false;
do_not_merge true; do_not_push true; technical_pass false; no
technical PASS claimed; CTO-030/CTO-031/CTO-025 not PASSED; no
path expansion; consumed review recorded.
