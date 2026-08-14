# Handoff — Cora A-006 / v6 for PR #62

Consumed qualifying Saul REQUEST_CHANGES run 31758118443
(comment 5288037039) on head 0df32c7446b95bda1f83137f8384a03135a959f6.
codex_invoked true, synthetic false. Issued immutable A-006 → v6 for
CTO-021 P0. authority_expanding false.

Contractor ctr-code-pr62smoke reused. lease-c3a003pr62q1 bumped to v6
with the same allowed_paths and denied_paths. Did not edit
blockers/ledger.yaml or requirements/ledger.yaml.

origin/main currently has NO saul-review.yml (only agent-audit.yml).
Activating pull_request_target requires the trusted workflow on default
branch; merging to main is a human security gate. Contractor next:
trusted-pr-orchestration-from-default-branch and
regression-candidate-saul-review-yml-cannot-change-runner-commands on
this PR. Do not call that PASSED. Do not restore candidate-HEAD trust.

Saul saying CTO-015..020 were remediated on 0df32c7 is not clearance of
those blockers on later heads. Do not mark them PASSED.

Cora did not implement. Do not merge. Do not mark ready.
