# Plan — 20260813-1512-ceo-init-standards-ceo

## Diagnosis (Saul VERIFY 20260813-1511)

| Finding | Root cause in INITIALIZE.md |
|---|---|
| PR #61: unregistered `cursor-cloud` provenance | Phase 1 did not forbid generic ephemeral IDs |
| PR #62: verify artifacts cite stale `5e40d45` not current tip | Phase 5 / runs README lacked exact-head + CI run URL rule |
| Historical malformed `events.jsonl` | Phase 3 lacked schema-valid event trail guidance |

## Scope

- `.ai/INITIALIZE.md` — Phase 1 registered-ID gate; Phase 3 event audit trail; Phase 5 metadata/head_sha/verify rules; standing obligations for `Agent:` trailer and head_sha refresh
- `.ai/runs/README.md` — metadata and verify artifact requirements

## Out of scope

- PR #61/#62 merge, close, or mark-ready
- Rewriting historical runs that used `cursor-cloud`
- Drive sync (SAI_DRIVE_REMOTE unset)
