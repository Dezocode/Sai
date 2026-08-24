# Component catalog — unified design system

All components live under `apps/desktop/src/design-system/`.  
iOS equivalents under `apps/ios-whisper/DesignSystem/` — **same tokens, same dimensions**.

**Rule:** Every tab, settings page, menu, and button uses these components. No ad-hoc styling.

---

## AppShell

- **Mode `shell`:** Activity bar (48px), sidebar (260px collapsible), main, optional right panel, status bar (22px)
- **Mode `immersive-game`:** Activity bar + full-viewport game + HUD overlays; sidebar collapsed by default
- Props: `layoutMode`, `activeTab`, `userSession`, `gatewayHealth`, `ingestP99`, `liveDataStatus`

## TabBar

- Height 35px; active tab bottom border `#007acc` 2px
- Icons: 16px monochrome; transition 200ms on switch
- Chat tab sets `layoutMode=immersive-game` on enter

## CursorButton

Variants: `primary` | `secondary` | `ghost` | `danger`  
Height: **28px** always. Padding X: 12px. Gap icon+label: 8px.  
States: default, hover (120ms), focus ring, press (scale 0.98), disabled, loading spinner

## CursorInput

Height 28px, padding 8px, radius 4px. Used for search, forms, URL bar.

## CursorSelect (dropdown)

- Trigger: 28px — identical to `CursorInput` + chevron 12px right
- Menu: max 320px height, scroll, 6px radius, shadow `elevation.menu`
- Item: 28px row, 4px pad, hover `rowHover`
- Placement: below trigger, flip if clipped; keyboard ↑↓ Enter Esc
- **Same component** on every tab — workspace picker, model select, room switcher

## MetricHero (Robinhood-style)

- Hero number: 28px semibold `fontFamily.metric`
- Delta: 13px `robinhood.metricUp` / `metricDown` with +/- prefix
- Count-up animation 400ms on VPS push
- Used by: tracking tab (canonical), status bar optional mini metric

## ProcessTable (Activity Monitor-style)

- Header 32px `activityMonitor.headerBg`; rows 28px zebra `rowStripe`
- Sortable columns; live bar column uses `activityMonitor.barFill`
- Mono timestamps 11px in time column
- Used by: tracking event list, host-health, GitHub CI failure table

## LiveGraph

- lightweight-charts with `color.graph` + Robinhood live scroll
- Props: `series[]`, `live`, `latencyBadge`, `vpsStreamUrl`
- New point pulse 15ms on `graph.livePulseMs`
- Used by: tracking (canonical), GitHub failure sparklines

## LiveDataBadge

- Shows connection state to VPS WebSocket
- States: `live` (green dot), `stale` (amber), `reconnecting` (pulse)
- Appears in status bar and any tab header with live metrics

## ObsidianEditor

- TipTap; wiki-link autocomplete `[[`
- Notion-like blocks: 8px vertical gap, hover `⋯` ghost handle
- Toolbar: Cursor-style icon ghost buttons 28×28

## GraphPanel

- force-graph; node colors from agent registry role
- Second brain + research shared workspace graph mode

## EmbeddedBrowser

- Desktop: Tauri webview + VPS CDP stream fallback
- Toolbar: back, forward, reload, URL bar (mono 12px), auth badge — all `CursorButton`/`CursorInput`
- Used in: settings/auth, research sources, Composio OAuth

## ImmersiveGameShell (Chat tab only)

- Wraps `GameCanvas`; fills **entire main viewport** below tab bar (Mac) or safe area (iOS)
- Top chrome: 35px room title bar — `CursorButton` back, room name 13px medium
- Left HUD: `AgentRolodex` slide panel 280px, glass `game.hudBg`
- Bottom HUD: `ChatTranscript` max 40vh, same tokens as inbox
- **Does not** use game engine fonts for HUD — dashboard tokens only

## GameCanvas (Habbo — full screen)

- **Mac:** Phaser 3 scales to window content area — not a small panel
- **iOS:** Full-screen Phaser (WKWebView) or SpriteKit scene — same assets
- Logical room 320×240 isometric; scale-to-fit with letterbox if needed
- Avatar sprites from `assets/agents/`
- Walk-up proximity → open bottom `ChatTranscript` HUD
- In-game speech bubbles use `game.chatBubbleAgent` / `chatBubbleUser` but **text** is 13px UI font

## ChatTranscript + TtsPlayer

- Message list: 13px body, 11px mono timestamps
- TTS toggle per thread
- Mac: NSSpeechSynthesizer; iOS: AVSpeechSynthesizer

## AgentRolodex + FriendsList

- Row 28px; name 13px medium; activity age 11px mono
- Status dot 6px; icons 16px
- **Identical** in shell sidebar and immersive HUD overlay
- Data: VPS `activity-ingest` + `agent-presence`

## McqActionCard

- Telegram/Slack MCQ — options as `CursorButton` secondary in bottom panel
- Slide-up animation 200ms

## WorkspaceSwitcher

- `CursorSelect` variant for research shared workspaces
- Filtered by GitHub OAuth org membership

## InboxPanel

- Unified Telegram DMs + agent messages
- Same row density as ProcessTable (28px)

---

## Import rule

```typescript
import { tokens } from '@/design-system/tokens';
// Never: style={{ color: '#007acc' }}
```

Smoke: `tests/smoke/design-tokens.sh` + `design-compliance.sh`
