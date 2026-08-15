# Verify — architecture-review

Commands actually run (both exit 0):

```
python3 scripts/lib/sai_auth_review_architecture_test.py
scripts/verify-saul-architecture-quality --self-test
```

SELFTEST PASS lines:

- arch-local-impact-good
- arch-system-missing-bad
- arch-shards-missing-bad
- arch-domain-stale-bad
- arch-fail-creates-blocker-good
- arch-system-required-now-good

Also: `python3 -m json.tool` on the schema; wrapper is executable;
CLI without `--from-json` exits 2 (`no implicit PR/contract/branch/SHA`);
production source has no current branch/contract/lease/PR defaults;
no live `ARCH-*` ledger files written. Sample FAIL payload
`ARCH-AUTHORIZATION-001`; cursor clear → REJECT
`ARCH_CLEARANCE_REQUIRES_AUTHENTIC_SAUL`.

Line counts: engine 440, tests 248, wrapper 9, schema 169.

Do not PASS B-SAUL-QUALITY-LOOP-001. Do not commit. Do not push.
