# Handoff — Cora A-011 / v11 for PR #62

Ingested operational evidence on exact head
`6ad1dc6bf6b0727b1bd4581695667ed6cfd7c2dc`: Cloud `gh workflow run
saul-review.yml` HTTP 403; accepted permissions actions=read; no
Saul run on 6ad1dc6; ICM agent-audit SUCCESS (31770830268
pull_request, 31770828271 push). Not a Saul consume. Did not run
`scripts/consume-saul-contract-review`. Did not put tokens in files.
Issued immutable A-011 → v11: restore narrow `on: pull_request` plus
post-merge skip-guard `TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN`. Keep
`workflow_dispatch`. A-010 full trigger removal is operationally
incompatible with actions=read. REQUIRED_FOR_CURRENT_BLOCKER, not a
waiver, not path expansion. authority_expanding false.
cora_admin_complete true on v11 is administration complete, not
technical PASS. technical_pass false.

Contractor ctr-code-pr62smoke reused. lease-c3a003pr62q1 bumped to
v11. allowed_paths unchanged. denied_paths unchanged. Kept task_id
20260813-2017-pr62-queue-ctr-code and existing task_ids. Did not
edit blockers/ledger.yaml or blockers/items. Did not write
`.ai/authorizations`, decisions, `.cursor`, scripts, workflows,
or `.ai/_config`.

Latest qualifying Saul remains run 31764010391 on `c51c9cf`,
REQUEST_CHANGES, event `pull_request`. No Saul run on 6ad1dc6.
A-011 authorizes Saul continuity + skip-guard; Cora did not PASS
CTO-025 or B-META-P0-001. CONDITIONAL_PASS_ON_HUMAN_MERGE is
Saul-only.

This commit uses original grant Task-ID
20260813-2016-pr62-queue-cora so authorization PASSES without
HEAD-union and without a contractor HEAD pin. This Cora wave does
not push.

Contractor next (do not PASS): restore narrow pull_request on
saul-review.yml; keep workflow_dispatch; add fail-closed skip-guard
when trusted file exists on origin/main; replace
candidate-pr-trigger-retired; add hermetic skip-guard fixture;
update threat-trace + merge-readiness notes; optional short note on
CTO-025 item that A-011 amends the retirement mechanism (trigger
kept, invocation skipped post-merge). Do not fake trusted file on
origin/main. Do not restore candidate-HEAD trust. Do not add
allow-unsafe-pr-checkout. Do not grow sai_auth_review.py. Do not
rework IMPLEMENTED_AWAITING_SAUL items. Do not merge. Do not mark
ready.

Officer next (Sai, not Cora): optional one-sentence Decision 0008
note. Decision 0008 already covers merge-activation at 121430d.

Cora did not implement. implements false. Do not merge. Do not
push. Do not mark ready. Not a technical PASS.
