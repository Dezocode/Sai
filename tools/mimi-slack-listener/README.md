# mimi-slack-listener — event-driven @mimi (Path A)

True inbound trigger for Mimi: a ~150-line Slack **Socket Mode** listener
that, on a real `@mimi` mention in a public SAI channel, spawns headless
Claude Code in the `monaecode/Sai` repo and replies in thread as the full
Mimi profile. Outbound WebSocket only — **no inbound port, no Funnel, no
public URL**.

Target host: `desktop-akn48te` (Linux/WSL2, tailnet `monaecode.github`,
100.98.182.124). **That machine is dezocode's, shared into the tailnet —
get dezocode's ack before deploying Mimi infrastructure on it.**

## Human steps (credential gates — Mimi cannot do these)

1. **Slack app**: api.slack.com/apps → Create New App → *From an app
   manifest* → paste `manifest.yaml` → create in the SAI workspace.
   Enable Socket Mode (copy the `xapp-` token), install to workspace
   (copy the `xoxb-` bot token). Invite the bot to the public channels it
   should serve (`/invite @mimi` in #agentupdates at minimum).
2. **On the host** (`ssh monaecode@100.98.182.124` over the tailnet):

   ```bash
   sudo mkdir -p /opt/mimi-listener && cd /opt/mimi-listener
   sudo cp <repo>/tools/mimi-slack-listener/listener.py .
   python3 -m venv venv && venv/bin/pip install slack-bolt
   # repo clone the agent will run in:
   git clone https://github.com/monaecode/Sai.git ~/Sai
   # current Claude Code + one-time auth (interactive):
   npm install -g @anthropic-ai/claude-code
   claude setup-token       # or place ANTHROPIC_API_KEY in the env file
   ```

3. **Secrets**: `cp .env.example /etc/mimi-listener.env`, fill real
   values, `sudo chmod 600 /etc/mimi-listener.env`.
4. **Service**: install `mimi-listener.service` per its header comment
   (WSL2 needs systemd enabled in `/etc/wsl.conf`).
5. **Verify honestly**: post `@mimi hello` in #agentupdates; the
   in-thread reply's permalink is the promotion evidence — record it in
   `.ai/agents/mimi/hooks.json` (flip the event-driven slack trigger to
   `verified`) and retire or slow the `mimi-slack-dispatch-poll`
   scheduled task.

## Security properties (Saul review scope)

- Mention text enters the agent prompt only inside an
  `<untrusted_slack_message>` envelope, length-capped; the prompt orders
  validation against repo state and forbids merge/push/registry/channel/
  contract/credential actions (same gates as the polling routine).
- Public channels only; bot messages ignored (loop guard); per-event
  dedupe persisted across restarts; single-flight semaphore; subprocess
  timeout; failure replies carry no stack traces or env.
- Secrets only in `/etc/mimi-listener.env` (0600), never in the repo.
- The headless session still runs under the repo's `.claude/settings.json`
  (deny list + force-push PreToolUse guard).

## Relationship to other triggers

| Path | File | Status |
|---|---|---|
| 15-min poll (interim) | scheduled task `mimi-slack-dispatch-poll` | active, caveated |
| **This listener (event-driven)** | `tools/mimi-slack-listener/` | implemented, awaiting deployment + tokens (human gate) |
| GitHub @mimi | `.github/workflows/mimi-dispatch-stub.yml` | inert stub |
