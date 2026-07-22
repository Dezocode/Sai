# research-coordinator — OpenClaw subagent

**Agent ID:** `research-coordinator`  
**Role:** Research tab session lead.  
**Fleet:** Inherits Alfred Telegram + ICM + Slack coherence protocol.

## Telegram + session (mandatory)

- **Behaviors:** provisioned from Alfred template → `.openclaw/agents/research-coordinator/telegram/BEHAVIORS.md` on VPS bootstrap
- **Protocol:** [telegram-session-protocol.md](../../docs/telegram-session-protocol.md)
- **Registry:** [agent-telegram-registry.md](../../docs/agent-telegram-registry.md)
- **Reporting:** INTAKE–HANDOFF updates to contract sender (dezocode) + Slack mirror
- **Three-connection gate:** Telegram inbox + Slack intro + Habbo presence

## Invoke

Dashboard research tab or OpenClaw session.

See [tabs/research/BUILD.md](../../tabs/research/BUILD.md) Phase 2.
