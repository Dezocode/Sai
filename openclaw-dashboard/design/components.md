# Component catalog — Cursor/Obsidian unified

All components live under `apps/desktop/src/design-system/`. iOS equivalents under `apps/ios-whisper/DesignSystem/`.

## AppShell

- Activity bar (48px), sidebar (260px collapsible), main, optional right panel, status bar (22px)
- Props: `activeTab`, `userSession`, `gatewayHealth`, `ingestP99`

## TabBar

- Height 35px; active tab bottom border `#007acc` 2px
- Icons: 16px monochrome, active `#cccccc`

## CursorButton

Variants: `primary` | `secondary` | `ghost` | `danger`  
States: default, hover, disabled, loading

## LiveGraph

- lightweight-charts with tokens from `color.graph`
- Props: `series[]`, `live`, `latencyBadge` (shows p99 from ingest)
- Used by: tracking (canonical), github failure rates

## ObsidianEditor

- TipTap; wiki-link autocomplete `[[`
- Toolbar: minimal (bold, link, heading) — Cursor-style icon buttons

## GraphPanel

- force-graph; node colors from agent registry role
- Second brain + research shared workspace graph mode

## EmbeddedBrowser

- Desktop: Tauri webview + VPS CDP stream fallback
- Toolbar: back, forward, reload, URL bar (mono 12px), auth badge
- Used in: settings/auth, research sources, Composio OAuth

## GameCanvas (Habbo)

- Phaser 3; 320×240 logical room scaled to panel
- Avatar sprites from `assets/agents/`
- Chat bubble UI uses `ChatTranscript` styling

## ChatTranscript + TtsPlayer

- Message list with agent avatar, timestamp mono
- TTS toggle per thread; streams agent replies
- Mac: NSSpeechSynthesizer; iOS: AVSpeechSynthesizer

## McqActionCard

- Telegram/Slack multiple-choice approval UI
- Renders options as Cursor secondary buttons in bottom panel
- See `integrations/telegram/mcq-actions.md`

## WorkspaceSwitcher

- Research tab: dezocode vs monaecode shared workspace picker
- Filtered by GitHub OAuth org membership

## InboxPanel

- Unified Telegram DMs + agent messages
- TTS auto-play setting (responsive mode)

Import tokens only from `@/design-system/tokens` — never inline hex in tab routes.
