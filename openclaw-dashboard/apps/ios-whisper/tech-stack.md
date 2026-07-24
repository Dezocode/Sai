# iOS companion — tech stack (WhisperFlow + TTS)

**Design:** [design/DESIGN-LANGUAGE.md](../../design/DESIGN-LANGUAGE.md)  
**Context:** [CONTEXT.md](./CONTEXT.md)

## Stack (native SwiftUI)

| Layer | Choice |
|---|---|
| UI | SwiftUI + NavigationStack (Cursor-like dark theme from `DesignTokens.swift`) |
| Voice in | Speech framework + Whisper API optional via VPS |
| Voice out | **AVSpeechSynthesizer** — responsive TTS for agent replies |
| Auth | Sign in with Apple + ASWebAuthenticationSession (GitHub) |
| Composio | SafariView Connect flows |
| OpenClaw | iOS node pairing per docs.openclaw.ai |
| Realtime | URLSession WebSocket → VPS ingest |
| Habbo lite | Phaser WKWebView **full viewport** or SpriteKit full screen | Same avatar assets; room fills Chat tab |
| Storage | Keychain for tokens |

## WhisperFlow UX

1. Global mic FAB (Cursor accent `#007ACC`)
2. Hold → waveform overlay → release → transcript preview
3. Send to Gateway session / active chat room agent
4. Agent reply → inbox thread + optional auto-TTS

## Inbox

- Telegram DMs mirrored via OpenClaw channel
- Agent registry threads
- TTS per-thread toggle (`responsive` mode = speak within 300ms of text arrival)

## Parity matrix

| Feature | Mac | iOS |
|---|---|---|
| Tracking graph | Full LiveGraph | Sparkline + detail drill-in |
| Second brain edit | Full TipTap | Read + quick note |
| Research workspace | Full | Session list + editor |
| Habbo chat | Phaser **full-screen** immersive | Phaser/SpriteKit **full-screen** + chat sheet |
| Live browse | CDP stream | SafariView / WKWebView |
| MCQ actions | Bottom panel | Push notification + action sheet |

Generate `DesignTokens.swift` from `design/tokens.json` in CI.

See [BUILD.md](./BUILD.md)
