# NotebookLM source context

| Field | Value |
|---|---|
| **Title** | Beyond the Chatbox: 6 Surprising Lessons from Building a Self-Hosted AI "Space Lobster" 🦞 |
| **Notebook URL** | https://notebooklm.google.com/notebook/89dadba9-7fba-4b0f-9960-65998062e865/artifact/adb6128d-8029-4192-873d-d0a43d815f80 |
| **Ingested by** | Cora (Contract Administrator), 2026-07-22 |
| **Status** | Partial — full artifact requires owner Google auth export |

## What we confirmed without full auth

The owner-provided NotebookLM artifact is a research synthesis on **OpenClaw**
(the self-hosted multi-channel AI agent gateway, community nickname "space
lobster"). It aligns with official OpenClaw documentation and the product
positioning at [openclaw.ai](https://openclaw.ai/) and
[docs.openclaw.ai](https://docs.openclaw.ai/).

## OpenClaw facts relevant to Alfred's contract

From official docs ([OpenClaw index](https://docs.openclaw.ai/)):

1. **Gateway-centric architecture** — one Gateway process routes chat apps
   (Slack, Telegram, Discord, WhatsApp, iMessage, …) to agent sessions.
2. **Self-hosted** — runs on user hardware or VPS; config at
   `~/.openclaw/openclaw.json`.
3. **Quick start** — `npm install -g openclaw@latest`, `openclaw onboard
   --install-daemon`, `openclaw dashboard` (default `http://127.0.0.1:18789/`).
4. **Multi-agent routing** — isolated sessions per agent, workspace, or sender.
5. **Platforms** — macOS app, iOS/Android nodes, Web Control UI, CLI.
6. **Skills/plugins** — ClawHub marketplace; channel plugins install on demand.
7. **Slack** — Socket Mode (default) or HTTP Request URLs; relay mode for
   managed deployments ([Slack channel docs](https://docs.openclaw.ai/channels/slack)).
8. **Telegram** — BotFather token, pairing flow, grammY long-polling
   ([Telegram channel docs](https://docs.openclaw.ai/channels/telegram)).

## Alfred action on first session

1. Ask dezocode/monaecode to **export** the NotebookLM notebook (PDF, Markdown,
   or Google Doc) into `openclaw-dashboard/docs/sources/notebooklm-space-lobster/`.
2. Index exported sources into the **second brain** vault (deliverable A4).
3. Cross-link lessons to each deliverable in `research-integration-methods.md`.

## Six lessons (placeholder until full export)

Until the owner exports the notebook body, Alfred must treat these as **hypothesis
headings** to validate against exported text:

| # | Likely theme (validate on export) | Contract link |
|---|---|---|
| 1 | Gateway beats chatbox-only UX | A0, A7 |
| 2 | Multi-channel routing changes ops | A1, A6, A10 |
| 3 | Self-hosting + VPS tradeoffs | A0, A11 |
| 4 | Skills/plugins vs monolith | A2, A5 |
| 5 | Mobile nodes + voice (Whisper) | A9 |
| 6 | Security/pairing defaults matter | A10, A11 |

Replace placeholders with verbatim lesson titles after export.
