# Tab: Config — OpenClaw mirror + config expert

| Field | Value |
|---|---|
| **Deliverable** | A7 |
| **Research** | [§8](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#8-openclaw-config-mirror) |
| **Subagent** | `.openclaw/agents/config-expert.md` |
| **Desktop route** | `/config` |

## Owner requirement

- Mirror OpenClaw host `~/.openclaw/openclaw.json` in dashboard
- Model configuration for integrated Telegram messaging
- **config-expert** agent on Alfred's team for guided changes

## Tech stack

| Layer | Choice |
|---|---|
| Read/write | Gateway RPC or guarded file sync API on VPS |
| UI | JSON5 editor with schema validation + masked secrets |
| Agent | OpenClaw subagent config-expert |

## Dependencies

- A0 Gateway
- settings/models for provider keys (env references only)

## Verification

- [ ] Read live config from Gateway
- [ ] Apply change with config-expert approval flow
- [ ] Reload gateway without secret leak to client logs

Build: [BUILD.md](./BUILD.md) | Models: [settings/models/](../settings/models/CONTEXT.md)
