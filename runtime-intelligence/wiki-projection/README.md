# Runtime Intelligence Wiki projection

Generated: 2026-08-13T19:53:02Z

**Canonical machine truth is SQLite + Git memory, not this page.**

## Organizational status

- status: **PROVISIONAL**
- Saul: PENDING
- Sai: PENDING
- Human: PENDING
- sub-PR: https://github.com/Dezocode/Sai/pull/64

## Runtime health

- `host-os`: **ok** — Ubuntu 24.04.4 LTS linux 6.8.0-137-generic
- `docker`: **ok** — Docker 29.6.1
- `hermes-gateway`: **degraded** — active but telegram TimedOut reconnect warnings in journal
- `grok-telegram-poll`: **ok** — systemd active
- `grok-telegram-worker`: **ok** — systemd active; host CLI not containerized
- `grok-docker`: **missing** — NO dedicated Grok Docker container — Phase C required
- `openclaw`: **ok** — container openclaw-fqy8-openclaw-1 running
- `gh-cli`: **ok** — authenticated as Dezocode
- `codex-cli`: **ok** — codex-cli 0.147.0 at /root/.local/bin/codex
- `skill-lab-dash`: **ok** — 127.0.0.1:8765
- `ri-memory`: **ok** — /opt/sai/runtime-intelligence initialized
- `saul-runner`: **ok** — hostinger-saul-codex container Up
- `grok-docker`: **ok** — sai-grok-ri:provisional status model=grok-4.5 effort=high grok 1.0.3
