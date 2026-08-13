# Verification — authorization loop

## Local commands (this workspace)

```
scripts/verify-semantic-hierarchy          → OK
scripts/verify-code-health --self-test     → all fixture evaluations passed
scripts/verify-code-health                 → 35 PASS
scripts/verify-agent-setup                 → OK
scripts/verify-scaffold-safety             → OK
scripts/verify-agent-authorization origin/main..HEAD → OK (pre-policy commits skipped)
scripts/verify-agent-authorization --self-test → 12 authorization fixtures PASS
scripts/invoke-saul-review --self-test     → BLOCKED/CODEX_UNAVAILABLE + idempotent skip + refused fake APPROVE
scripts/consume-saul-contract-review --self-test → ordinary amend v2 + expanding human gate
python3 tests/authorization/e2e.py         → A–F,K–N,S,V,W,X,Y PASS; G–J,O–U PENDING (GitHub/Codex)
```

## Matrix (local)

| Item | Result | Notes |
|---|---|---|
| A no impl agent | PASS | CONTRACT_REQUIRED |
| B CONTRACT_REQUIRED | PASS | request.yaml |
| C assume Cora | PASS | sai-assume-agent ctr-admin |
| D contract v1 | PASS | revisions/v1.yaml + lease |
| E assume contractor | PASS | in-scope only |
| F provisional change | PASS | pre-commit rc=0 |
| G GitHub event | PENDING | after push, saul-review.yml |
| H Actions invokes Codex | PENDING | needs OPENAI_API_KEY or CODEX_API_KEY |
| I Saul profile loaded | PENDING | same |
| J real REQUEST_CHANGES | PENDING | same |
| K Cora consume | PASS | local fixture review |
| L contract v2 + TRACE | PASS | CTO-001 → A-002 → v2 |
| M v1 lease stale | PASS | assume blocked |
| N reload v2 | PASS | new lease |
| O second GH event | PENDING | |
| P Saul APPROVE exact | PENDING | never faked |
| Q Sai APPROVE exact | PENDING | ceo identity |
| R CI green exact SHA | PENDING | after push |
| S human gate BLOCKED until dual | PASS | BLOCKED as expected |
| T extra commit stale | PENDING | |
| U fresh READY | PENDING | |
| V expanding not auto-granted | PASS | human-approval-required.yaml |
| W wrong-path blocked | PASS | |
| X idempotent skip | PASS | |
| Y Codex missing BLOCKED | PASS | CODEX_UNAVAILABLE |

## Credential boundary

GitHub secrets `OPENAI_API_KEY` and/or `CODEX_API_KEY` are not provisioned.
Do not invent credentials. Until a real `saul-review.yml` run has
`codex_invoked: true`, the loop is **BLOCKED**, not READY FOR HUMAN REVIEW.
