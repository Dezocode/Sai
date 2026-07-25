# BUILD — Auth settings

## Phase 1: Auth matrix doc

Maintain `docs/auth-matrix.md` — provider × status × owner × env var name (no values).

## Phase 2: GitHub OAuth

1. OAuth App; callback `sai-dashboard://auth/github` or localhost handler.
2. Store refresh token encrypted on VPS; session cookie to desktop.

## Phase 3: Composio

1. Wire `integrations/composio/` Connect flows for telegram, googledrive, googleai.
2. Dashboard tiles: Connected | Blocked | Pending with retry.

## Phase 4: Browser MCP

1. VPS Playwright/CDP pool for OAuth pages user cannot complete in webview.
2. Stream view to desktop `apps/desktop/src/auth/BrowserMcpPanel.tsx`.

## Phase 5: Availability gate

1. Health check: all required providers reachable or explicit BLOCKED with ticket.
2. Block organization onboarding if auth hub offline while Gateway up.
