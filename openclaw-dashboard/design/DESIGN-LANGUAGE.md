# Design language — SAI Dashboard (Cursor + Obsidian unified)

**Applies to:** All tabs, settings pages, Mac desktop, iOS companion  
**Tokens:** [tokens.json](./tokens.json)  
**Components:** [components.md](./components.md)

---

## Design intent

The dashboard is a **native Cursor Desktop clone** for shell chrome (activity bar,
sidebar tabs, editor panels, status bar, typography, buttons) combined with
**Obsidian-class** affordances in second-brain and research (wiki links, graph,
split panes). Every tab shares one visual system — no one-off styling.

| Principle | Rule |
|---|---|
| **One shell** | Mac/iOS use same tokens; iOS adapts layout responsively |
| **Cursor chrome** | `#1e1e1e` base, `#007acc` accent, 13px UI text, 35px tabs |
| **Obsidian depth** | Graph/backlink panels reuse sidebar + editor split patterns |
| **Live data** | Graphs use shared `LiveGraph` component (tracking tab is canonical) |
| **Embedded browse** | VPS live browser uses same tab frame + auth toolbar |
| **Chat/game** | Habbo room runs inside **panel** region — not a separate app skin |

---

## Shell layout (Mac desktop)

```
┌──┬──────────┬─────────────────────────────────────┬──────────┐
│ A│ Sidebar  │  Tab bar (Cursor-style)             │          │
│ c│ (Obsidian│├─────────────────────────────────────┤ Optional │
│ t│  file    │  Main surface (editor / graph /     │  right   │
│ i│  tree)   │  game canvas / live browser)        │  panel   │
│ v│          ├─────────────────────────────────────┤          │
│ i│          │  Bottom panel (terminal / ingest /   │          │
│ t│          │  chat transcript / MCQ actions)      │          │
│ y│          └─────────────────────────────────────┘          │
├──┴──────────┴─────────────────────────────────────┴──────────┤
│ Status bar: Gateway ●  ingest p99  GitHub  Slack  user GitHub  │
└───────────────────────────────────────────────────────────────┘
```

**Activity bar icons (fixed order):** Tracking | Second brain | Research | Chat | GitHub | Config | Settings

---

## Typography & controls

| Element | Spec |
|---|---|
| Body UI | 13px SF Pro / system, `#cccccc` |
| Monospace (logs, CI, ingest) | SF Mono 12px |
| Tab label | 13px medium, inactive `#969696`, active `#cccccc` |
| Button primary | 28px height, `#007acc`, 4px radius |
| Button secondary | `#3c3c3c` border `#454545` |
| Input | 28px, bg `#3c3c3c`, focus ring `#007acc` |
| Links | `#3794ff`, underline on hover |

All tabs import tokens from `design/tokens.json` — **no hardcoded colors in tab code**.

---

## Shared React component library (`apps/desktop/src/design-system/`)

| Component | Used in |
|---|---|
| `AppShell` | All routes |
| `TabBar`, `ActivityBar`, `StatusBar` | Global |
| `CursorButton`, `CursorInput`, `CursorSelect` | All tabs |
| `LiveGraph` | Tracking, GitHub failure rates |
| `ObsidianEditor` | Second brain, research notes |
| `GraphPanel` | Second brain, research graph |
| `EmbeddedBrowser` | Auth flows, research sources |
| `ChatTranscript` | Chat room, inbox, Telegram mirror |
| `McqActionCard` | Telegram/Slack approval prompts |
| `WorkspaceSwitcher` | Research shared workspaces |

iOS SwiftUI mirrors via `DesignTokens.swift` generated from `tokens.json`.

---

## Platform tech stack (smooth native)

| Platform | Stack | Why |
|---|---|---|
| **macOS** | Tauri 2 + React 19 + TypeScript + Tailwind (token-driven) | Native window, small footprint, WebView for embedded browse |
| **macOS TTS** | `NSSpeechSynthesizer` + optional cloud voice | Agent responses in inbox + chat |
| **iOS** | SwiftUI + Observation + AVFoundation | Native Cursor-like navigation stacks |
| **iOS input** | Speech (WhisperFlow) + on-device Speech framework | Voice → Gateway |
| **iOS TTS** | `AVSpeechSynthesizer` | Responsive agent replies in inbox/Habbo |
| **Game** | Phaser 3 in desktop WebView panel; SpriteKit lite on iOS | Habbo chat rooms |
| **Charts** | lightweight-charts themed via `tokens.graph` | Stock-meter tracking |
| **Browser** | VPS Playwright/CDP → stream to `EmbeddedBrowser` | Full OAuth + live browse |
| **Auth** | Sign in with Apple + GitHub OAuth + Composio Connect | See `settings/auth/providers.md` |

---

## Tab-specific surfaces (same language)

| Tab | Main surface | Cursor pattern | Obsidian pattern |
|---|---|---|---|
| Tracking | Live graph + ticker | Bottom panel metrics | — |
| Second brain | Markdown editor | Editor | Graph + backlinks sidebar |
| Research | Session + shared workspace | Split editor | Graph + sources panel |
| Chat room | Phaser canvas | Panel | — |
| GitHub | Branch table + CI sparklines | Sidebar repo list | — |
| Config | JSON5 form | Settings editor | — |

---

## iOS companion parity

- Tab bar maps to activity bar icons (5 max visible + More)
- WhisperFlow FAB → voice command sheet
- Inbox: Telegram + agent TTS responses
- Habbo: simplified top-down or static room view + chat sheet (same tokens)
- Embedded browse: `SFSafariViewController` for OAuth; VPS stream via WebKit for authenticated browse

---

## Verification

Design compliance checked in smoke tests:

- `tests/smoke/design-tokens.sh` — all tabs import tokens
- `tests/smoke/visual-shell.sh` — shell regions render
- Per-tab BUILD.md Phase 0: read this file before UI work

See [tests/smoke/design-compliance.md](../tests/smoke/design-compliance.md).
