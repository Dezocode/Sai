# Handoff — ctr-code-pr62smoke (CTO-024 SHA-bound)

Lease `lease-c3a003pr62q1`, contract v6, Task-ID
`20260813-2017-pr62-queue-ctr-code`.

Saul run 31760665414 / comment 5288363871 rejected HEAD/working-tree
retrospective authorization. Replay now uses commit-time grants/leases plus
SHA-bound rows from committed HEAD only.

Pinned wave SHAs (full 40 hex): f2ab0b55, ff0a18f6, 97527f38 (contractor
0052); 854e578c, b9f13f09, eab6b0c0 (ceo 0052);
ec183590 (cora 0052); bb519c29 (cora 0041). Did not pin 5ad0b94 / 7b03b97
/ 5684304.

CTO-025 remains BLOCKED_EXTERNAL (main merge required). Candidate
`saul-review.yml` pull_request self-hosted job is still enabled.
CTO-026 TRIAGED meta. CTO-027 assigned ctr-admin.

Cora has an untracked A-007/v7 run; this commit keeps v6 trailers.

`self_pass: false`. `do_not_merge: true`. Next: Cora v7 if pushed, then
fresh Saul review. Do not merge.
