# OPENCLAW.md — OpenClaw Gateway entry point for this repo

Read this when operating a **registered OpenClaw-primary SAI agent** on a
self-hosted Gateway (VPS), not when using Cursor or Claude Code as primary.

## Read first

1. `.ai/CONTEXT.md` — workspace identity
2. `.ai/shared/references/openclaw-runtime.md` — OpenClaw adapter contract
3. `.ai/agents/<name>/AGENT.md` — your agent profile
4. Contractor? Execute `.ai/ONBOARDING.md` after your contract first message

## Alfred (OpenClaw Administrator)

- Profile: `.ai/agents/alfred/`
- Binding first message: `.ai/contracts/20260722-openclaw-dashboard-dezocode/first-message-to-openclaw.md`
- Gateway bootstrap: `openclaw onboard --install-daemon` on Hostinger VPS

## Non-negotiable

Same as `.ai/CONTEXT.md`: no secrets in Slack/logs/commits; evidence-backed
`runtimes/openclaw/tools.json`; human review gates; one agent per working tree.
