# Composio Google Drive connector

**Deliverable:** A2 — Composio connections  
**Use:** Second-brain Drive mirror for the dashboard vault.

## Files

- `connector.js` — stub; loads `COMPOSIO_API_KEY` from env, exposes `connect()`, `listFiles()`, `download()`, `upload()`, `syncMirror()`.
- No env files in repo; only the variable name `COMPOSIO_API_KEY` is referenced.

## Auth flow

1. Dashboard Auth hub → **Connect Google Drive** → Composio `googledrive` toolkit.
2. User OAuth via Composio Connect Link.
3. Connector uses Composio action endpoints to read/write Drive.
4. Mirror writes to `openclaw-dashboard/vault/mirror/` (local staging) and syncs to Drive.

## Verification

- [ ] Live test call after dezocode toolkit approval.
- [ ] No tokens in repo.
