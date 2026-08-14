# Verify note — SHA-bound authorization (not HEAD-union)

Self-tests in `scripts/lib/sai_auth_rebind_test.py` (wired from
`scripts/verify-agent-authorization --self-test`):

1. Uncommitted/working-tree grant task_ids MUST NOT authorize an older SHA
2. Later-HEAD grant.task_ids without a SHA-bound record MUST NOT authorize
   an older SHA
3. SHA-bound record for sha S with matching agent+task_id DOES authorize S
4. SHA-bound record must not authorize a different sha
5. Path/principal checks still fail-closed
6. sai-blockers --clear as cursor still REJECT

Commit-time lease `task_ids[]` still authorize. HEAD/working-tree unions
do not. Pins load from `git show HEAD:.ai/_config/authorization.yaml`.

`self_pass: false`. `do_not_merge: true`.
