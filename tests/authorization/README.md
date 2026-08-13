# Authorization loop tests (decision 0006)

```bash
scripts/verify-agent-authorization --self-test
scripts/verify-contract-authorization --self-test
scripts/invoke-saul-review --self-test
scripts/consume-saul-contract-review --self-test
tests/authorization/run-e2e
```

Lifecycle matrix A–Y is printed by `e2e.py`. Local fixtures cover identity,
contract, Cora consume, stale lease, and fail-closed missing-Codex.
Production GitHub→self-hosted runner→local Codex rows require a real
`saul-review.yml` run with `codex_invoked: true`.
