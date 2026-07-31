# Composio NotebookLM / Google AI connector

**Deliverable:** A2 — Composio connections  
**Scope:** Export/import pipeline only. NotebookLM has **no public write API**; we do not claim live NotebookLM creation or editing.

## Files

- `connector.js` — stub; loads `COMPOSIO_API_KEY` from env, exposes `connect()`, `listNotebooks()`, `exportNotebook()`, `importToVault()`.
- No env files in repo; only the variable name `COMPOSIO_API_KEY` is referenced.

## Pipeline

1. Owner exports a NotebookLM notebook (PDF, Markdown, or Google Doc) into `openclaw-dashboard/docs/sources/notebooklm-space-lobster/`.
2. `importToVault()` parses and indexes the export into the second-brain vault (deliverable A4).
3. Cross-link lessons to deliverables in `research-integration-methods.md`.

## Auth

- Composio Google AI / Notebook toolkit connection (Pending approval).
- No NotebookLM API key stored in repo.

## Verification

- [ ] Import a sample export into vault after approval.
- [ ] No tokens in repo.
