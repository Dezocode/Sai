# OpenClaw Gateway runtime — SAI agent adapter (Layer 3)

> Canonical requirement for **OpenClaw-primary** agents
> (`primary_runtime: openclaw-gateway-vps`). Contract Administrator scaffolds
> via `scripts/agent-scaffold --primary-runtime openclaw` and
> `scripts/agent-contract-scaffold --runtime openclaw`.

## What OpenClaw-primary means

OpenClaw-primary agents **do not** use Cursor Desktop or Cursor Cloud as their
primary runtime. They operate on a **self-hosted OpenClaw Gateway** (typically
Hostinger VPS) and expose:

- Multi-channel messaging (Slack, Telegram, …) through the Gateway
- Host CLI + admin dashboard servers on the VPS
- Live activity ingest to dashboard tabs (see contract latency gate)

Repo artifacts (`.ai/agents/<name>/`, contracts, ICM runs) are still edited via
Git; implementation and dispatch happen on the Gateway host.

## Invoke path

1. Read repo-root **`OPENCLAW.md`** (Layer 0 entry for OpenClaw sessions).
2. Load `.ai/agents/<name>/AGENT.md`, `skills.md`, `hooks.json`.
3. Execute binding contract `first-message-to-openclaw.md` when present.
4. Gateway config: `~/.openclaw/openclaw.json` on the VPS (never commit secrets).
5. **Loopback bind default** — `gateway/config/gateway-exposure-policy.md`; no `0.0.0.0` without CTO approval.

Official docs: [docs.openclaw.ai](https://docs.openclaw.ai/)

## Required scaffold paths

Every OpenClaw-primary agent must have:

```
.ai/agents/<name>/runtimes/openclaw/
  tools.json                    # verified capabilities (Phase 5B on VPS)
  automation/profile.md         # Gateway cron/webhooks truth table
  gateway/
    README.md                   # bootstrap + health + ingest contract
    config/gateway-options.json # channels, models, dashboard bind, latency SLO
```

CI enforces presence via `scripts/verify-agent-setup`.

## Phase 5B — capability survey

On the **Gateway host** (not necessarily the Cursor cloud VM):

```bash
SAI_AGENT_ID=<agent-id> scripts/agent-verify-caps \
  --tools-file .ai/agents/<name>/runtimes/openclaw/tools.json \
  --environment openclaw-gateway-vps
```

Record verified entries only. Typical capabilities:

| ID | Kind | Evidence |
|---|---|---|
| `openclaw-cli` | shell | `openclaw --version`, `openclaw doctor` |
| `openclaw-gateway` | service | systemd active; Control UI HTTP 200 |
| `activity-ingest` | service | WebSocket feed p99 ≤ contract SLO (default 15ms) |
| `slack-channel` | channel | OpenClaw Slack plugin configured |
| `telegram-channel` | channel | pairing approved |

## Phase 7 — automation

Document **real** Gateway mechanisms in `runtimes/openclaw/automation/profile.md`:

- `openclaw onboard --install-daemon`
- Gateway cron / webhooks ([Capabilities docs](https://docs.openclaw.ai/))
- Dashboard admin CLI ingest process

Do **not** claim Cursor Automations UI as Alfred's primary automation.

## Organization onboarding hard gates (dezocode PR #45)

OpenClaw-primary contractors (Alfred) must satisfy before `active` / main merge:

1. **100% production completion** — all contract deliverables; smoke suite zero blocking errors.
2. **Host CLI live feed** — SAI admin dashboard CLI on VPS feeds all monitoring tabs.
3. **Latency SLO** — p99 **≤ 15ms** from host CLI event to dashboard tab render (measured on VPS LAN or documented tunnel baseline).
4. **ICM + Sai verification** — full `.ai` verifier suite PASS; Sai `[SAI][VERIFY] PASS`.
5. **Auth regulation** — Composio/native OAuth; no secrets in Git; dashboard auth hub reachable.

## References

- [OpenClaw documentation](https://docs.openclaw.ai/)
- [Agent runtimes index](./agent-runtimes.md)
- Alfred contract: `.ai/contracts/20260722-openclaw-dashboard-dezocode/`
