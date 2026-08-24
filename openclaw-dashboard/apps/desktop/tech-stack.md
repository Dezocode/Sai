# Mac desktop — tech stack

**Design:** [design/DESIGN-LANGUAGE.md](../../design/DESIGN-LANGUAGE.md)  
**Context:** [CONTEXT.md](./CONTEXT.md)

## Stack (native + smooth)

| Layer | Choice | Version pin in BUILD |
|---|---|---|
| Shell | **Tauri 2** | Latest stable |
| UI | React 19 + TypeScript | Strict |
| Styling | Tailwind CSS 4 + `design/tokens.json` CSS vars | Generated at build |
| State | Zustand + TanStack Query | — |
| Routing | TanStack Router | Tab routes = activity bar |
| Charts | lightweight-charts | Themed via tokens |
| Editor | TipTap 2 | ObsidianEditor wrapper |
| Graph | react-force-graph | GraphPanel |
| Game | Phaser 3.80+ | Chat room panel |
| Browser | Tauri WebView + VPS CDP WebSocket | EmbeddedBrowser |
| TTS | `@tauri-apps/plugin-napi` → NSSpeechSynthesizer | Agent responses |
| Auth | Keychain via tauri-plugin-store | GitHub session handle only |
| Realtime | native WebSocket to VPS ingest | <15ms p99 path |

## Project structure

```
apps/desktop/
  src/
    design-system/     ← shared Cursor clone components
    shell/             ← AppShell, ActivityBar, TabBar, StatusBar
    tabs/              ← mirror openclaw-dashboard/tabs/* routes
    settings/
    services/          ← API clients to VPS
  src-tauri/           ← Rust bridge for TTS, Keychain, window
```

## Performance targets

- Cold start < 2s on M-series Mac
- Tab switch < 100ms
- LiveGraph refresh at ingest rate without jank (RAF batching)
- Phaser room 60fps with ≤20 avatars

## Build tool

- Vite 6
- `pnpm` workspace (when monorepo root added)

See [BUILD.md](./BUILD.md)
