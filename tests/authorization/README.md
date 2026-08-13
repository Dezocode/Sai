# Authorization loop tests (decision 0006)

```bash
scripts/verify-agent-authorization --self-test
scripts/verify-contract-authorization --self-test
scripts/invoke-saul-review --self-test
scripts/consume-saul-contract-review --self-test
tests/authorization/run-e2e
```

Lifecycle matrix A–Y is printed by `e2e.py`. Items that require a real
GitHub→Codex invocation stay PENDING/FAIL until `OPENAI_API_KEY` or
`CODEX_API_KEY` is provisioned on Dezocode/Sai and a `saul-review.yml`
run records `codex_invoked: true`.
