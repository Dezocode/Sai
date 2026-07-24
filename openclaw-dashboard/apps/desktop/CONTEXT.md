# App: Mac desktop client

| Field | Value |
|---|---|
| **Deliverable** | A9 |
| **Requirement** | 100% success — zero blocking errors on smoke flows |

## Scope

Shell hosting all **tabs/** and **settings/** routes:

- Tauri 2 (preferred) or Electron + React + TypeScript
- WebSocket to VPS ingest + Gateway APIs
- Embedded browser MCP panel (settings/auth)
- GitHub OAuth session

## Structure

```
apps/desktop/
  src/tabs/tracking/
  src/tabs/second-brain/
  src/tabs/research/
  src/tabs/chat-room/
  src/tabs/github/
  src/tabs/config/
  src/settings/auth/
  ...
```

Build: [BUILD.md](./BUILD.md)
