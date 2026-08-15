# Verify — human principal commit Agent-trailer allowlist

Contractor `ctr-code-pr62smoke`. Task-ID `20260813-2017-pr62-queue-ctr-code`.
Contract v12. Do not PASS. Do not merge. Do not push.

## Line counts (caps yaml ≤300, py ≤500)

```
228 .ai/_config/authorization.yaml
458 scripts/lib/sai_auth.py
462 scripts/lib/sai_auth_verify.py
```

## Fixtures (`python3 scripts/lib/sai_auth_human_commit_test.py`)

```
SELFTEST PASS  human-principal-listed-good
SELFTEST PASS  human-principal-wrong-author-bad
SELFTEST PASS  human-principal-unknown-sha-bad
SELFTEST PASS  agent-trailer-not-skipped-bad
sai_auth_human_commit_test: OK
```

## `scripts/verify-agent-authorization --self-test`

exit 0. Same four `SELFTEST PASS` lines present. Existing synthetic/cue/event/rebind fixtures still executed.

## Live `scripts/verify-agent-authorization origin/main..HEAD`

exit 0. `verify-agent-authorization: OK`.

The seven human Dezocode SHAs all printed PASS:

- PASS 516893c68d8d authorization
- PASS 25e48fcdb4aa authorization
- PASS 1fcd983ba333 authorization
- PASS 8ba1641d2ef8 authorization
- PASS 474c4fc15eb2 authorization
- PASS f66c299e33dd authorization
- PASS ff1005f6afa3 authorization

Identity cutoff remains `d113fa0`. No force-push. No `.ai/authorizations/**`.
No blocker PASS.
