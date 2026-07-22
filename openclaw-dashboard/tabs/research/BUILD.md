# BUILD — Research tab

## Phase 1: Session model

1. Define `research-sessions/` store on VPS (JSON + markdown exports).
2. UI: new session bound to `contract_id` or free research.
3. Source importer: URL, file upload, NotebookLM export path.

## Phase 2: research-coordinator subagent

1. Author `.openclaw/agents/research-coordinator.md`.
2. Wire OpenClaw routing key per session.
3. Enforce PLAN before repo mutation proposals.

## Phase 3: Review gate

1. UI state: draft → pending_review → approved → vault.
2. Approved only: write to vault via vault-mcp.
3. Rejected: stay in session archive with reason.

## Phase 4: research-mcp

Tools:

- `archive_source(session_id, uri|file)`
- `propose_improvement(session_id, markdown, evidence[])`
- `link_to_vault(note_id, backlinks[])`
- `query_verified_findings(query)`

## Phase 5: Performance research

1. Add benchmarks under `research/benchmarks/` (CPU/GPU scripts).
2. Store results in vault with reproducible commands.
