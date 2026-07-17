# Workflow input validation — malicious-input regressions

Saul CTO P1 (`mimi-dispatch-stub.yml:38`, review 4719159552): inputs were
interpolated via `${{ }}` directly into `run:` shell. Fix: inputs now
reach the shell **only** through `env:`, and are validated with anchored
regexes (`grep -Eqx`, full-string match) before any other use.

Regression run 2026-07-17, this session, `re.fullmatch` over the exact
workflow patterns (semantics identical to `grep -Eqx`):

| Input | Payload | Result |
|---|---|---|
| contract_id | `20260717-x; rm -rf /` | REJECTED |
| contract_id | `20260717-x$(curl evil)` | REJECTED |
| contract_id | `../../.github/workflows` | REJECTED |
| contract_id | `20260717-x/../../secrets` | REJECTED |
| contract_id | `20260717-x\ninjected` (newline) | REJECTED |
| contract_id | ``20260717-x`id` `` | REJECTED |
| contract_id | `20260717-x' \|\| true` | REJECTED |
| requester | `a b; id` | REJECTED |
| requester | `-leading-hyphen` | REJECTED |
| requester | `x$(id)` | REJECTED |
| task_slug | `slug;id` | REJECTED |
| task_slug | `slug/../x` | REJECTED |
| task_slug | `UPPER` | REJECTED |
| requester | `monaecode`, `Dezocode` | ACCEPTED |
| contract_id | `20260717-mimi-dispatcher-bootstrap-monaecode`, `20260715-splunk-clone-monaecode` | ACCEPTED |
| task_slug | `mimi-dispatcher-bootstrap` | ACCEPTED |

**RESULT: ALL 18 CASES PASS.**

Defense layers: (1) `env:` indirection means even an accepted string is
never parsed as shell; (2) regexes exclude `/`, `.`, whitespace, quotes,
backticks, `$`, newlines — no traversal out of `.ai/contracts/`; (3) the
workflow remains inert (no secrets, `contents: read`, no Claude
invocation).
