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
- `oc-telegram-session` `docs/telegram-session-protocol.md` + Alfred `telegram/BEHAVIORS.md` + smoke `telegram-session-reporting.sh` (stub exit 2 until run `telegram-session.jsonl`)
- `oc-telegram-mcq` `integrations/telegram/mcq-actions.md` + smoke `telegram-mcq.sh` (stub exit 2)
- `oc-connection-gate` `tests/smoke/subagent-connection-gate.sh` fail-closed; `subagent-connection-gate-negative.sh` self-test
- `oc-secrets` `scripts/verify-secrets-compliance.sh` + smoke `tests/smoke/secrets-compliance.sh` + `docs/secrets-security.md` + `auth-matrix.md` + vault schema
- `oc-ingest-slo` `scripts/verify-ingest-latency.sh` stub exit 2 until `services/activity-ingest` exists
- `oc-smoke-all` `tests/smoke/all-gates.sh` orchestrator fails while child stubs fail; `run-all.sh` stub exit 2
- `oc-svc-ingest` `services/activity-ingest/README.md`
- `oc-svc-presence` `services/agent-presence/README.md`
- `oc-svc-github` `services/github-watch/README.md`
- `oc-svc-research` `services/research-mcp/README.md`
- `oc-svc-telegram` `services/telegram-session/{CONTEXT,BUILD}.md`
- `oc-svc-vault` `services/vault-mcp/README.md`
- `oc-composio` `integrations/composio/README.md`
- `oc-subagents` `openclaw-dashboard/.openclaw/agents/{config-expert,research-coordinator}.md`
- `oc-onboard-docs` `docs/subagent-onboarding-protocol.md` `alfred-smoke-runbook.md` `fulfillment-evidence.md` `sai-icm-integration.md` `icm-protocol-handbook.md`
- `oc-notebooklm` `openclaw-dashboard/docs/sources/notebooklm-space-lobster/README.md`
## How to get to it (user POV)
- VPS: `openclaw-dashboard/docs/vps-bootstrap.md` then `verify-all-dependencies.sh` and `verify-gateway-health.sh`
- CI/local bind: `openclaw-dashboard/scripts/verify-gateway-bind.sh`
- Fleet: `tests/smoke/all-gates.sh` / `fleet-coherence-gate.sh`
- Telegram evidence: `docs/agent-telegram-registry.md` (connected=yes only with valid links)
## Driving it with verify-sai
Preconditions: repo root. Gateway/Telegram live services optional.
- **Bind.** `openclaw-dashboard/scripts/verify-gateway-bind.sh`; exit 0.
- **Self-tests.** `openclaw-dashboard/scripts/verify-all-dependencies.sh --self-test`; `verify-gateway-health.sh --self-test`; `verify-agent-telegram.sh --self-test`; `tests/smoke/subagent-connection-gate-negative.sh`
- **Secrets.** `openclaw-dashboard/scripts/verify-secrets-compliance.sh`; exit 0.
- **Fleet files.** `openclaw-dashboard/tests/smoke/fleet-coherence-gate.sh`; exit 0 if contract fields present.
- **Stub SLO.** `openclaw-dashboard/scripts/verify-ingest-latency.sh`; expect exit 2; do not treat as success.
- **Stub smoke.** `openclaw-dashboard/tests/smoke/run-all.sh`; expect exit 2. `all-gates.sh` fails while those stubs fail.
- **Stub session.** `openclaw-dashboard/tests/smoke/telegram-session-reporting.sh`; expect exit 2.
- **Proof.** `go run ./cmd/sai-verify relevant --path openclaw-dashboard/scripts/verify-gateway-bind.sh --tool Shell` lists `openclaw-ops`.
## Gotchas
- Live `verify-gateway-health.sh` without OpenClaw CLI is `verified-unreachable` (need `openclaw` + loopback gateway).
- `telegram-mcq.sh`, ingest SLO, and `telegram-session-reporting.sh` are stubs (exit 2) until wired — prove the stub, do not skip.
- `subagent-connection-gate.sh` (non-negative) fail-closes until registry evidence exists.
- Never bind gateway to `0.0.0.0`.
