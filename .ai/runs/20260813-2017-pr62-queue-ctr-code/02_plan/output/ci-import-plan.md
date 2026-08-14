# Plan — Hostinger bootstrap import path (CI agent-audit)

CI `agent-audit` 31825204732 failed:

```
ModuleNotFoundError: No module named 'sai_auth'
```

in `scripts/saul-hostinger-bootstrap-review` line 17.

Root cause: the script inserts `Path(__file__).parent.parent / "lib"`
(`REPO/lib`), not `scripts/lib`. `--self-test` is invoked by
`sai-blockers --self-test` before `saul-attest` sets `PYTHONPATH`.
Local green was a polluted shell from a prior `saul-attest`.

## Fix (smallest)

1. `scripts/saul-hostinger-bootstrap-review`: put `scripts/lib` on
   `sys.path` (`Path(__file__).resolve().parent / "lib"`). Handle
   `--self-test` after stdlib imports and **before** importing
   `sai_auth`. Cursor/CI still exit 2 `NOT_HOSTINGER_SAUL`.
2. `sai_auth_saul_identity_test.py` bootstrap subprocess: set
   `PYTHONPATH` to `scripts/lib` so the fixture stays hermetic if
   import order regresses.

Do not restore `saul-review.yml`. Do not PASS. Do not push.
Keep Python files ≤500 lines; keep the bootstrap script small.

## Verify

- `unset PYTHONPATH; scripts/sai-blockers --self-test`
- `scripts/saul-hostinger-bootstrap-review --self-test`; `$?` must be 2
- `scripts/saul-attest --self-test`
