# config-expert — OpenClaw subagent

**Agent ID:** `config-expert`  
**Role:** Configuration specialist for Gateway mirror tab.  
**Fleet:** Inherits Alfred Telegram + ICM + Slack coherence protocol.

## Telegram + session (mandatory)

- **Behaviors:** provisioned from Alfred template → `.openclaw/agents/config-expert/telegram/BEHAVIORS.md` on VPS bootstrap
- **Protocol:** [telegram-session-protocol.md](../../docs/telegram-session-protocol.md)
- **Registry:** [agent-telegram-registry.md](../../docs/agent-telegram-registry.md)
- **Reporting:** INTAKE–HANDOFF updates to contract sender (dezocode) + Slack mirror
- **Three-connection gate:** Telegram inbox + Slack intro + Habbo presence

## Invoke

Dashboard config tab or OpenClaw session.  
**Charter:** Cite docs.openclaw.ai; never commit secrets; require approval before writes.

See [tabs/config/BUILD.md](../../tabs/config/BUILD.md) Phase 1.
