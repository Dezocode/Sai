# BUILD — Mac desktop app

## Phase 1: Shell

1. Init Tauri 2 + React router mirroring `tabs/` and `settings/` folders.
2. VPS connection config (URL, tokens from auth settings).

## Phase 2: Tab integration

Implement routes in dependency order:

1. host-health + auth (settings)
2. tracking (needs ingest)
3. github, config, reporting-sop
4. second-brain, research
5. chat-room (needs presence + Telegram)

## Phase 3: Browser MCP embed

1. Panel component for OAuth flows.
2. Connect to VPS CDP bridge documented in settings/auth.

## Phase 4: Smoke

`tests/smoke/desktop-mac.sh` — launch app, navigate each route, zero console errors.

Organization gate: **100% production** on approved smoke list.
