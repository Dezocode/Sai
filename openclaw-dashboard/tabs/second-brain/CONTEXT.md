# Tab: Second brain — Obsidian-class vault

| Field | Value |
|---|---|
| **Deliverable** | A4 |
| **Research** | [§5](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#5-second-brain-obsidian-clone) |
| **Services** | `services/vault-mcp/` |
| **Desktop route** | `/second-brain` |

## Owner requirement

Store and organize files/text; **Obsidian/Notion-class** editor with:

- `[[wiki-links]]` backlinks
- Hierarchy graph + semantic "general relativity" vector view
- GitHub OAuth for human edit/search
- NotebookLM exports ingested to `docs/sources/notebooklm-space-lobster/`

## Tech stack

| Layer | Choice |
|---|---|
| Vault store | Git repo `vault/` + Composio Drive mirror |
| Editor | TipTap (ProseMirror) |
| Graph | force-graph (structural) + embedding view (optional UMAP) |
| Search | ripgrep index + optional local embeddings on VPS |
| MCP | `vault-mcp` read/write/search tools |

## Dependencies

- A11 auth (GitHub OAuth)
- A2 Composio Google Drive (optional sync)
- A5 research tab writes approved notes here

## Verification

- [ ] Create note, backlink, graph edge < 2s
- [ ] GitHub user can edit via OAuth
- [ ] MCP tool `vault_search` returns backlinked context

Build: [BUILD.md](./BUILD.md)
