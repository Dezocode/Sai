# OpenClaw operations
Operators bootstrap a loopback OpenClaw Gateway, run fail-closed fleet/telegram/secrets gates, and keep VPS services at documented stubs until implemented.
## Sub-features
- `oc-gateway-bind` `openclaw-dashboard/scripts/verify-gateway-bind.sh` host `127.0.0.1`, `loopback_default`.
- `oc-gateway-opts` `.ai/agents/alfred/runtimes/openclaw/gateway/config/{gateway-options.json,gateway-exposure-policy.md}`
- `oc-gateway-health` `openclaw-dashboard/scripts/verify-gateway-health.sh [--self-test|--port]`
- `oc-deps` `openclaw-dashboard/scripts/verify-all-dependencies.sh [--self-test]`
- `oc-vps` `openclaw-dashboard/docs/vps-bootstrap.md` + `host/systemd/openclaw-gateway.service` + `host/README.md`
- `oc-fleet` `openclaw-dashboard/tests/smoke/fleet-coherence-gate.sh` + `docs/fleet-coherence-gate.md`
- `oc-telegram-verify` `openclaw-dashboard/scripts/verify-agent-telegram.sh [--self-test|--scope …]`
- `oc-telegram-registry` `openclaw-dashboard/docs/agent-telegram-registry.md` + `docs/blocked-agents.md`
- `oc-telegram-session` `docs/telegram-session-protocol.md` + Alfred `telegram/{BEHAVIORS,session-memory}.md` + smoke `telegram-session-reporting.sh` (stub exit 2 until run `telegram-session.jsonl`)
- `oc-telegram-mcq` `integrations/telegram/mcq-actions.md` + Alfred `telegram/BLOCKED-MCQ-CONTINUATION.md` + smoke `telegram-mcq.sh` (stub exit 2)
- `oc-connection-gate` `tests/smoke/subagent-connection-gate.sh` fail-closed; `subagent-connection-gate-negative.sh` self-test
- `oc-secrets` `scripts/verify-secrets-compliance.sh` + smoke `tests/smoke/secrets-compliance.sh` + `docs/secrets-security.md` + `auth-matrix.md` + `.ai/agents/alfred/runtimes/openclaw/gateway/config/secrets-store.schema.json`
- `oc-ingest-slo` `scripts/verify-ingest-latency.sh` stub exit 2 until `services/activity-ingest` exists
- `oc-smoke-all` `tests/smoke/all-gates.sh` orchestrator fails while child stubs fail; `run-all.sh` stub exit 2
- `oc-svc-ingest` `services/activity-ingest/README.md`
- `oc-svc-presence` `services/agent-presence/README.md`
- `oc-svc-github` `services/github-watch/README.md`
- `oc-svc-research` `services/research-mcp/README.md`
- `oc-svc-telegram` `services/telegram-session/{CONTEXT,BUILD}.md`
- `oc-svc-vault` `services/vault-mcp/README.md`
- `oc-svc-sessions` `services/sessions-api/*` hermes-sessions API contract, app, Dockerfile, and tests.
- `oc-composio` `integrations/composio/README.md`
- `oc-subagents` `openclaw-dashboard/.openclaw/agents/{config-expert,research-coordinator}.md`
- `oc-onboard-docs` `docs/subagent-onboarding-protocol.md` `alfred-smoke-runbook.md` `fulfillment-evidence.md` `sai-icm-integration.md` `icm-protocol-handbook.md`
- `oc-notebooklm` `openclaw-dashboard/docs/sources/notebooklm-space-lobster/README.md`
## How to get to it (user POV)
- VPS: `openclaw-dashboard/docs/vps-bootstrap.md` then `verify-all-dependencies.sh` and `verify-gateway-health.sh` CI/local bind: `openclaw-dashboard/scripts/verify-gateway-bind.sh` Fleet: `tests/smoke/all-gates.sh` / `fleet-coherence-gate.sh` Telegram evidence: `docs/agent-telegram-registry.md` (connected=yes only with valid links)
## Driving it with verify-sai
- **Bind.** ::exec openclaw-dashboard/scripts/verify-gateway-bind.sh
- **Deps.** ::exec openclaw-dashboard/scripts/verify-all-dependencies.sh --self-test
- **Health.** ::exec openclaw-dashboard/scripts/verify-gateway-health.sh --self-test
- **Telegram.** ::exec openclaw-dashboard/scripts/verify-agent-telegram.sh --self-test
- **Conn-neg.** ::exec openclaw-dashboard/tests/smoke/subagent-connection-gate-negative.sh
- **Secrets.** ::exec openclaw-dashboard/scripts/verify-secrets-compliance.sh
- **Fleet.** ::exec openclaw-dashboard/tests/smoke/fleet-coherence-gate.sh
- **Ingest stub.** ::exec openclaw-dashboard/scripts/verify-ingest-latency.sh expect=2
- **Run-all stub.** ::exec openclaw-dashboard/tests/smoke/run-all.sh expect=2
- **Session stub.** ::exec openclaw-dashboard/tests/smoke/telegram-session-reporting.sh expect=2
- **MCQ stub.** ::exec openclaw-dashboard/tests/smoke/telegram-mcq.sh expect=2
## Gotchas
- Live `verify-gateway-health.sh` without OpenClaw CLI is `verified-unreachable` (need `openclaw` + loopback gateway). `telegram-mcq.sh`, ingest SLO, and `telegram-session-reporting.sh` are stubs (exit 2) until wired — prove the stub, do not skip. `subagent-connection-gate.sh` (non-negative) fail-closes until registry evidence exists. Never bind gateway to `0.0.0.0`.
