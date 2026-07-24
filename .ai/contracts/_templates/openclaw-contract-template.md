# OpenClaw Gateway contractor contract template

Use with `scripts/agent-contract-scaffold --runtime openclaw`.

## Runtime-specific notes

- **primary_runtime:** `openclaw-gateway-vps`
- **Capability survey:** on Gateway host — `scripts/agent-verify-caps --environment openclaw-gateway-vps`
- **Scaffold:** `runtimes/openclaw/gateway/` per `.ai/shared/references/openclaw-runtime.md`
- **Invoke:** `OPENCLAW.md` → `AGENT.md` → contract `first-message-to-openclaw.md`

## ONBOARDING focus

1. Fresh `openclaw onboard` on contracted VPS.
2. Implement gateway scaffold + dashboard host CLI ingest.
3. Meet latency SLO (default p99 ≤ 15ms) for live tab data.
4. Pass all ICM verifiers before Sai audit.

## Branch pattern

`proj/<project-slug>/<ctr-agent-id>/<task-slug>`
