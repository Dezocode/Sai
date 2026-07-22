# Amendment: dezocode PR #45 review (4751008157)

| Field | Value |
|---|---|
| **Date** | 2026-07-22 |
| **Reviewer** | dezocode (U0BHYH0NMCY) |
| **PR** | https://github.com/Dezocode/Sai/pull/45 |
| **Review** | https://github.com/Dezocode/Sai/pull/45#pullrequestreview-4751008157 |
| **Applied by** | Cora (ctr-admin) |

## Owner requirements (verbatim summary)

1. **OpenClaw is not a Cursor runtime agent** — implement new OpenClaw runtime scaffold in agent directory and agent generators (`agent-scaffold`, `agent-contract-scaffold`).
2. Alfred must pass **all ICM and Sai `.ai` verifications**.
3. **100% production completion** of dashboard + OpenClaw CLI host dependencies + auth regulation on VPS.
4. Dashboard servers hosted from Alfred's VPS; **host admin CLI live-feeds** activity into dashboard tabs.
5. **p99 ≤ 15ms latency** for all live data (monitoring/reporting capability of host CLI).
6. Hard must-complete criteria for **organization onboarding**.

## Contract changes applied

- `primary_runtime` → `openclaw-gateway-vps` (removed Cursor-primary)
- Added `organization_onboarding_gate` with latency SLO and 100% production gate
- Linked `.ai/shared/references/openclaw-runtime.md`, repo `OPENCLAW.md`
- Alfred profile migrated to `runtimes/openclaw/gateway/`

## Filesystem / generator changes

| Path | Change |
|---|---|
| `.ai/shared/references/openclaw-runtime.md` | New canonical OpenClaw adapter |
| `OPENCLAW.md` | Repo entry point |
| `scripts/agent-scaffold --primary-runtime openclaw` | Gateway scaffold |
| `scripts/agent-contract-scaffold --runtime openclaw` | Contract template + onboarding |
| `scripts/verify-agent-setup` | Enforces openclaw gateway paths |
| `scripts/verify-semantic-hierarchy` | `openclaw-gateway-vps` in VALID_RUNTIMES |
| `.ai/contracts/_templates/openclaw-contract-template.*` | New template |

## Alfred next actions (unchanged isolation)

Work on `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap` only until fulfillment gate.
