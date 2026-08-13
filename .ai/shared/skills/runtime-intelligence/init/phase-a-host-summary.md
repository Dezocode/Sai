# Phase A host summary (no secrets)

| Component | Status | Notes |
|-----------|--------|-------|
| Host | ok | Ubuntu 24.04.4, srv1840454 |
| Docker | ok | 29.6.1 |
| Hermes gateway | degraded | active; Telegram timeout reconnects observed |
| Grok bridge systemd | ok | poll + worker + control-relay |
| Grok Docker | **missing** | host CLI only; Phase C required |
| OpenClaw container | ok | openclaw-fqy8-openclaw-1 |
| gh auth | ok | Dezocode |
| Codex CLI | ok | 0.147.0 |
| RI local memory | ok | /opt/sai/runtime-intelligence |
| Saul runner container | ok | hostinger-saul-codex |
| Organizational init | **PROVISIONAL** | Saul/Sai/human PENDING |

Grok models observed via CLI: `grok-4.6` (default), `grok-4.5`. Decision text
targets high-reasoning `grok-4.5` / latest stable reasoning — must re-verify at
Dockerization time. Bridge code fallbacks: model `grok-4.5`, effort `high`.
