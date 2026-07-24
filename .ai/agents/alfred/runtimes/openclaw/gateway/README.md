# OpenClaw Gateway — Alfred (ctr-code-alfred1)

Required for `primary_runtime: openclaw-gateway-vps`. See `.ai/shared/references/openclaw-runtime.md`.

## Bootstrap (Hostinger VPS)

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
# Bind loopback only — see config/gateway-exposure-policy.md (Saul P1)
openclaw gateway --port 18789 --host 127.0.0.1
openclaw doctor
```

**Security:** Default `gateway-options.json` uses `127.0.0.1`. Remote dashboard
clients use Tailscale or TLS reverse proxy — never `0.0.0.0` without CTO approval.

## Host admin CLI → dashboard ingest (hard gate)

The SAI administrative dashboard CLI on Alfred's VPS must **live-feed** all
monitoring tabs. Contract SLO: **p99 ≤ 15ms** from CLI event emission to tab
render (measured on VPS; document tunnel baseline if remote clients used).

Implement under `openclaw-dashboard/services/activity-ingest/` per contract A3.

## Verification

```bash
openclaw-dashboard/scripts/verify-gateway-health.sh
openclaw-dashboard/scripts/verify-ingest-latency.sh   # must pass p99 <= 15ms
SAI_AGENT_ID=ctr-code-alfred1 scripts/agent-verify-caps \
  --tools-file .ai/agents/alfred/runtimes/openclaw/tools.json \
  --environment openclaw-gateway-vps
```

Alfred is **not** a Cursor runtime agent.
