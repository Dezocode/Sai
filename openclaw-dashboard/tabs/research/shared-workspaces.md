# Research — shared workspaces (dezocode + monaecode)

**Tab:** [tabs/research/CONTEXT.md](./CONTEXT.md)  
**Auth:** GitHub OAuth — org membership determines workspace access

## Workspace model

| Workspace ID | GitHub gate | Shared assets |
|---|---|---|
| `ws-dezocode` | Member of Dezocode org OR dezocode GitHub user allowlist | Sessions, vault folder `vault/research/dezocode/` |
| `ws-monaecode` | Member of monaecode org OR allowlist | `vault/research/monaecode/` |
| `ws-sai-shared` | Both cofounders approved | Cross-org decision records only |

### Hierarchy (GitHub context)

```
ws-dezocode/
  projects/
    openclaw-dashboard/
    splunk-clone/          # when active
  agents/
    sai/
    saul/
ws-monaecode/
  projects/
    mimi-dispatcher/
    splunk-clone/
  agents/
    mimi/
```

Each node links to:

- `.ai/contracts/<id>/`
- `.ai/projects/<slug>/`
- Open PRs from `tabs/github/` ingest

## UI (Cursor + Obsidian)

- **WorkspaceSwitcher** in research tab header (Cursor tab dropdown style)
- Split pane: session list | ObsidianEditor | GraphPanel (shared backlink graph)
- Live browser panel for source capture (`EmbeddedBrowser`)

## Collaboration rules

1. Sessions created inside a workspace inherit ACL.
2. Approved notes promote to workspace vault + second brain backlinks.
3. MCP `research-mcp` enforces workspace_id on all tool calls.
4. dezocode cannot write monaecode workspace without explicit share grant (MCQ via Telegram).

## Verification

- [ ] dezocode GitHub user sees ws-dezocode only (+ shared if granted)
- [ ] monaecode user sees ws-monaecode
- [ ] Cross-workspace note blocked at MCP layer

Build: [BUILD.md](./BUILD.md) Phase 2b
