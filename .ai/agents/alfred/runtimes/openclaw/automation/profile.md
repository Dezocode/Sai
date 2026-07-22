# OpenClaw Gateway automation — Alfred

Primary runtime: `openclaw-gateway-vps` on **Hostinger VPS**. **Not** Cursor Automations.

| Mechanism | Status | Evidence |
|---|---|---|
| systemd `openclaw-gateway.service` | building | pending VPS bootstrap |
| Gateway cron / webhooks | building | per https://docs.openclaw.ai/ |
| Host admin CLI → dashboard ingest | building | p99 ≤ 15ms SLO (dezocode hard gate) |
| Telegram session → contract sender | required | BEHAVIORS.md; every INTAKE–HANDOFF |
| Fleet coherence provisioner | building | subagent telegram template copy |
| `[SAI][EVENT]` via OpenClaw Slack or `scripts/agent-report` | required | #agentupdates C0BH15HDN2Z |

Regenerate after Phase 5B on VPS. Do not claim Cursor @alfred as primary dispatch.
