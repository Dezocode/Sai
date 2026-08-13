# Verification — authorization loop

Continued in `.ai/runs/20260813-1752-saul-runner-cursor-cloud/04_verify/output/verification.md`.
Production Codex REQUEST_CHANGES: GitHub run **31729666256** on runner
`hostinger-saul-codex`, `codex_invoked: true`. Not READY.

## Local commands

```
scripts/verify-semantic-hierarchy          → OK
scripts/verify-code-health --self-test     → all fixture evaluations passed
scripts/verify-code-health                 → 37 PASS (after rebase)
scripts/verify-agent-setup                 → OK
scripts/verify-scaffold-safety             → OK
scripts/verify-agent-authorization origin/main..HEAD → OK
scripts/invoke-saul-review --self-test     → BLOCKED/CODEX_UNAVAILABLE; refused fake APPROVE
scripts/consume-saul-contract-review --self-test → v2 amend + expanding human gate
python3 tests/authorization/e2e.py         → A–F K–N S V W X Y PASS locally
```

## Matrix A–Y

| Item | Result | Evidence |
|---|---|---|
| A no impl agent | PASS | e2e CONTRACT_REQUIRED |
| B CONTRACT_REQUIRED | PASS | `.ai/requests/` + e2e request.yaml |
| C assume Cora | PASS | `sai-assume-agent ctr-admin` |
| D contract v1 | PASS | revisions/v1.yaml + provisional lease |
| E assume contractor | PASS | in-scope session |
| F provisional change | PASS | pre-commit rc=0 |
| G GitHub event | PASS | PR event fired `saul-cto-review` 31717665860 and 31717844582 |
| H Actions invokes Codex | FAIL | runner had empty OPENAI_API_KEY/CODEX_API_KEY; `codex_invoked: false` |
| I Saul Codex profile loaded | FAIL | Codex was not executed |
| J real REQUEST_CHANGES | FAIL | no Codex review YAML from Saul |
| K Cora consume | PASS | local consume of machine-readable REQUEST_CHANGES |
| L contract v2 + TRACE | PASS | CTO-001 → A-002 → v2 |
| M v1 lease stale | PASS | assume blocked STALE_OR_MISSING_LEASE |
| N reload v2 | PASS | new lease assume |
| O second GH event | PASS | second PR event run 31717844582 on f69a483 |
| P Saul APPROVE exact | FAIL | disposition BLOCKED not APPROVE |
| Q Sai APPROVE exact | FAIL | ceo has not recorded verification on this head |
| R CI green exact SHA | PASS* | agent-audit green on f69a483 (31717840048 push, 31717844578 PR); saul-cto-review is red by design |
| S human gate BLOCKED until dual | PASS | BLOCKED without Saul+Sai exact-head APPROVE |
| T extra commit stale | FAIL | cannot prove stale Saul/Sai implementation approval — none exist |
| U fresh READY | FAIL | never reached READY |
| V expanding not auto-granted | PASS | human-approval-required.yaml |
| W wrong-path / trailer / unbound | PASS | fixtures + e2e wrong-path; CI replay does not trust session |
| X idempotent skip | PASS | local second invoke same key; workflow does not amend (no loop) |
| Y Codex missing BLOCKED | PASS | run 31717844582 `reason: CODEX_UNAVAILABLE`; status `saul-cto-review` failure |

\* agent-audit is green; the independent CTO check is fail-closed red until Codex is provisioned.

## GitHub Actions

| Run | SHA | Event | Workflow | Conclusion |
|---|---|---|---|---|
| 31717662188 | 4a1e557 | push | agent-audit | success |
| 31717665794 | 4a1e557 | pull_request | agent-audit | success |
| 31717665860 | 4a1e557 | pull_request | saul-cto-review | failure (NO_ARTIFACT then BLOCKED) |
| 31717840048 | f69a483 | push | agent-audit | success |
| 31717844578 | f69a483 | pull_request | agent-audit | success |
| 31717844582 | f69a483 | pull_request | saul-cto-review | failure BLOCKED CODEX_UNAVAILABLE |

## Credential boundary

Provision GitHub Actions repository secrets (do not commit values):

1. `OPENAI_API_KEY` — OpenAI API key used by Codex CLI
2. `CODEX_API_KEY` — optional alias; copied to OPENAI_API_KEY if the former is unset

Then re-run `saul-review.yml`. Do not claim READY until a run has
`codex_invoked: true` and Saul APPROVE of the exact revision and SHA.
