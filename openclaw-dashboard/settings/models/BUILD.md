# BUILD — Models settings

1. Read model section from sanitized gateway config.
2. UI: provider list, default model, per-agent overrides.
3. Writes go through config-expert approval API (tabs/config).
4. Test harness: send probe message via Telegram channel config.
5. Document supported providers per https://docs.openclaw.ai/

Never store API keys in git — VPS environment only.
