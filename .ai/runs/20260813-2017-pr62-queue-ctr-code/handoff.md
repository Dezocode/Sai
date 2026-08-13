# Handoff — contractor remediation (CTO-009/010/011)

Landed under contract `20260813-pr62-saul-smoke` v3 lease
`lease-c3a003pr62q1`:

- CTO-009: officer writes after d113fa0 need a tracked grant; forged
  `Agent: ceo` fixture fails.
- CTO-010: `saul-review.yml` materializes a trusted reviewer tree and
  invokes `"$SAI_TRUSTED_TREE/scripts/invoke-saul-review"`. Candidate is
  data. Residual: GitHub still loads `pull_request` YAML from the PR
  until this workflow exists on main.
- CTO-011: bootstrap `until_sha` closed at d113fa0.
- Queue: `scripts/sai-dispatch-transition --self-test` proves 10 duplicate
  evals create one claim.

Do not merge. Await Saul rereview of the new HEAD.
