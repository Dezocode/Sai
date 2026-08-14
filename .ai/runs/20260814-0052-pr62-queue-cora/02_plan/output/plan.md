# Plan — Cora A-006 / v6 for PR #62

Qualifying Saul run 31758118443 (comment 5288037039) on head
0df32c7446b95bda1f83137f8384a03135a959f6 is REQUEST_CHANGES,
codex_invoked true, synthetic false. CTO-015..020 were remediated on
THAT head, but persistent-runner trust is incomplete. New finding
CTO-021 P0, authority_expanding false.

Issue immutable A-006 → v6 (copy v5 style). Reuse contractor
ctr-code-pr62smoke and lease-c3a003pr62q1. Do not expand allowed_paths.
Do not change denied_paths. Bump lease + contract.json to v6.

origin/main currently has NO saul-review.yml (only agent-audit.yml).
Activating pull_request_target requires the trusted workflow to exist
on default branch; merging to main is a human security gate. Contractor
implements the trusted workflow artifact + regression test on this PR.
Do not call that PASSED. Do not restore candidate-HEAD trust. Do not
mark CTO-015..020 PASSED on later heads.

Cora does not implement. Do not merge. Do not mark ready.
