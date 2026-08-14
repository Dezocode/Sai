# Implement — SAUL-BOOTSTRAP P0

Bound candidate HEAD to immutable `--head` in new
`scripts/lib/sai_auth_bootstrap.py`. Deleted operator fallback that
assigned invoke/attest from `root/scripts` when trusted copies were
missing. `SAI_CANDIDATE_TREE` is required (no default to repo root).
Trusted missing → `TRUSTED_REVIEWER_UNAVAILABLE` exit 1, distinct from
`NOT_HOSTINGER_SAUL` exit 2. TOCTOU re-check immediately before invoke.

Did not write production keys. Did not create `/opt/sai/trusted-reviewer`.
Did not restore `saul-review.yml`. Did not PASS. Did not push.
P1-D remains DEFERRED_NONBLOCKING (no blocker).
