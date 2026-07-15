# Plan — runtime adapters (CEO)

## Goal

Add ICM-compliant multi-runtime agent adapters (Cursor, Claude Code, Codex
Desktop) without duplicate registries, without breaking Cursor generation,
and with Drive-indexable canonical paths in `.ai/shared/`.

## Scope

1. Decision record 0002 + `agent-runtimes.md` reference index.
2. Layer 0 entry routers: `CODEX.md`; expand `CLAUDE.md`; fix `CONTEXT.md`
   Phase 9 wording.
3. `runtimes/{cursor,claude,codex}/` under `sai/` and `mimi/` with canonical
   capability files; root `tools.json` as manifest.
4. Registry `primary_runtime` + `entry_points` for active agents.
5. `agent-scaffold --primary-runtime` + trailing-comma fix.
6. `verify-semantic-hierarchy` enforcement for new structure.

## Out of scope (follow-ups)

- Merge PR #5 (parallel track).
- `agent-automation-spec --runtime` generator (document path only).
- Slack @Claude → Mimi bridge.
- Live Codex Desktop initialization (stub suite only).

## Verification

`verify-semantic-hierarchy`, `verify-agent-audit origin/main..HEAD`,
`bash -n` on modified scripts.
