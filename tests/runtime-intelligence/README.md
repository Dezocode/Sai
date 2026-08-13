# Runtime Intelligence tests

## Negative authority
```bash
python3 tests/runtime-intelligence/test_negative_authority.py
```

These prove policy invariants and refuse self-declaration of ACTIVE without
Saul + Sai + human approvals in the environment. Live merge/force-push is never
attempted by these tests.
