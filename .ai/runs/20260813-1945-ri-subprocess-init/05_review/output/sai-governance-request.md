# Sai exact-state governance REQUEST

**Status: REQUESTED — not recorded as APPROVE**

| Field | Value |
|-------|-------|
| Requested of | Sai (`ceo`) |
| Implementation head | `6c50e0b2c55b9741bcd5284511c16c65eccd08ca` |
| Contract | `20260813-ri-subprocess-init` revision v1 |
| Init sub-PR | https://github.com/Dezocode/Sai/pull/64 |
| Parent PR | https://github.com/Dezocode/Sai/pull/62 |
| Saul formal run | https://github.com/Dezocode/Sai/actions/runs/31738840708 (workflow_dispatch) |
| Package | `.ai/runs/20260813-1945-ri-subprocess-init/04_verify/output/saul-package-6c50e0b2c55b/` |

## Rule (Decision 0006)
Sai must independently record governance verification of the **same exact** contract revision and implementation SHA via `scripts/record-sai-verification` while assumed as `ceo`. Subprocess runners must not invent Sai APPROVE.

## Preconditions for Sai
1. Formal Saul disposition exists for head `6c50e0b2c55b9741bcd5284511c16c65eccd08ca` (Codex path).
2. CI/auth state reviewed (pre-contract commits still fail Contract-ID — honest).
3. Org remains PROVISIONAL until human admission after Saul+Sai.

## Disposition required from Sai
`APPROVE` | `REQUEST_CHANGES` | `BLOCKED` bound to head `6c50e0b2c55b9741bcd5284511c16c65eccd08ca` and contract revision v1.
