# BUILD — Second brain tab

## Phase 1: Vault storage

1. Initialize `vault/` git repo (markdown + attachments/).
2. Wiki-link parser on save → SQLite backlink index.
3. Composio Drive sync job (optional, document BLOCKED if no auth).

## Phase 2: Editor UI

1. TipTap with markdown round-trip.
2. Sidebar: backlink panel, outline hierarchy.
3. Graph tab: force-graph from link index.

## Phase 3: Vector view

1. Chunk notes; embed via VPS local model or API (env config).
2. Second graph mode: semantic clusters (label as beta if approximate).

## Phase 4: vault-mcp

1. Implement MCP tools: `vault_read`, `vault_write`, `vault_search`, `vault_link`.
2. Register in OpenClaw Gateway MCP config on VPS.
3. Document in `services/vault-mcp/README.md`.

## Phase 5: NotebookLM ingest

1. Import `docs/sources/notebooklm-space-lobster/*` to vault.
2. Auto-backlink to contract + ICM-HANDBOOK.

## Auth

All human writes require GitHub OAuth session from `settings/auth/`.
