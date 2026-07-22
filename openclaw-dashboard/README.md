# OpenClaw SAI Dashboard

**Contract:** `20260722-openclaw-dashboard-dezocode`  
**Agent:** Alfred (`ctr-code-alfred1`) — The OpenClaw Administrator  
**Status:** Scaffold only — implementation on `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap`

## Start

1. Paste [first-message-to-openclaw.md](../.ai/contracts/20260722-openclaw-dashboard-dezocode/first-message-to-openclaw.md) into fresh OpenClaw session.
2. Read [research-integration-methods.md](../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md).

## Planned layout

```
openclaw-dashboard/
  host/              # VPS systemd, gateway templates
  scripts/           # verify-gateway-health.sh, verify-all-dependencies.sh
  docs/              # vps-bootstrap, sai-icm-integration, composio-auth
  apps/
    desktop/         # Mac dashboard (Tauri/Electron)
    ios-whisper/     # iPhone Whisper companion
  services/
    activity-ingest/ # Tracking tab backend
    vault-mcp/       # Second brain MCP
    research-mcp/    # Research tab MCP
    github-watch/    # Branch + CI ingest
    agent-presence/  # Habbo chat room presence
  integrations/
    composio/        # Telegram, Drive, Notebook connectors
  vault/             # Git-backed second brain (runtime data, not committed secrets)
  tests/smoke/       # Merge gate smoke suite
  .openclaw/agents/  # config-expert, research-coordinator subagents
```

Alfred creates these paths during bootstrap (deliverable A0).
