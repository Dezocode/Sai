# Smoke test — design compliance

Alfred must PASS before UI PR merge.

## Checks

1. `design/tokens.json` validates as JSON (schema v2 fields present: `layout.modes`, `liveData`, `components.select`)
2. Every tab route imports `@/design-system/tokens` (grep gate)
3. No raw hex in `apps/desktop/src/tabs/` except token file
4. `AppShell` renders on all tab routes; Chat route uses `layoutMode=immersive-game`
5. iOS `DesignTokens.swift` generated from `tokens.json` — token count parity
6. All interactive controls use shared components: `CursorButton`, `CursorInput`, `CursorSelect` (no native `<select>` unstyled)
7. Chat tab: `GameCanvas` fills viewport height ≥ 80% of content area (Mac snapshot test)
8. Live data badges present on tracking + status bar (VPS WebSocket or honest disconnected state)

## Commands

```bash
openclaw-dashboard/tests/smoke/design-tokens.sh
openclaw-dashboard/tests/smoke/design-compliance.sh
```

Exit 0 when compliant; exit 1 with file:line violations.

See [DESIGN-LANGUAGE.md](../../design/DESIGN-LANGUAGE.md) for the unified language spec.
