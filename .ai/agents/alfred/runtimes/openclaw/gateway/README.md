# OpenClaw Gateway — Alfred (ctr-code-alfred1)

Required for `primary_runtime: openclaw-gateway-vps`. See `.ai/shared/references/openclaw-runtime.md`.

## Bootstrap (Hostinger VPS)

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
openclaw gateway --port 18789
openclaw doctor
```

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
