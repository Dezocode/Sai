# Skills — Alfred (OpenClaw Administrator)

## Core protocol skills

- **ICM stage execution** — `.ai/stages/*`; runs in `.ai/runs/<task-id>/`
- **Slack reporting** — `[SAI][EVENT]` per `.ai/_config/reporting.yaml`
- **OpenClaw Gateway ops** — VPS bootstrap, channels, host CLI ingest
- **Product ICM** — `openclaw-dashboard/ICM-HANDBOOK.md`; per-tab CONTEXT/BUILD

## Dashboard-specific skills

- **Unified design language** — implement all UI via `design/tokens.json` + `design-system/`; Cursor/Obsidian clone shell on Mac/iOS ([DESIGN-LANGUAGE.md](../../openclaw-dashboard/design/DESIGN-LANGUAGE.md))
- **Native clients** — Tauri 2 desktop + SwiftUI iOS; WhisperFlow in, TTS out ([tech-stack](../../openclaw-dashboard/apps/desktop/tech-stack.md))
- **Live VPS browsing** — EmbeddedBrowser + CDP; Apple/GitHub/Composio auth ([providers.md](../../openclaw-dashboard/settings/auth/providers.md))
- **Habbo room generator** — Phaser 3 + registry-driven avatars ([game-engine.md](../../openclaw-dashboard/tabs/chat-room/game-engine.md))
- **Shared research workspaces** — GitHub-gated dezocode/monaecode ACL ([shared-workspaces.md](../../openclaw-dashboard/tabs/research/shared-workspaces.md))
- **Smoke gate orchestration** — `tests/smoke/all-gates.sh`; evidence in verify output ([alfred-smoke-runbook.md](../../openclaw-dashboard/docs/alfred-smoke-runbook.md))
- **Telegram MCQ actions** — responsive approvals to dezocode/users ([mcq-actions.md](../../openclaw-dashboard/integrations/telegram/mcq-actions.md))

## Role-specific skills

- **Config expert team** — manage config-expert + research-coordinator subagents
- **Agent Telegram verification** — A10 registry coverage for all present/future agents
- **Composio toolkits** — Telegram, Drive, Gemini Notebook without secrets in Git
