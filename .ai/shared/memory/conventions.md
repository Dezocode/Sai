# SAI — Coding and workflow conventions

> Durable, verified conventions only. Supersede rather than silently rewrite.

## Git

- One logical change per commit, descriptive outcome-oriented message.
- Commit trailers where supported: `Task-ID:`, `Agent:`, `Plan:`,
  `Report-Event:`.
- Branch naming: `ceo/<slug>`, `dezo/<slug>`, `monae/<slug>`,
  `cursor/<slug>-<suffix>` (cloud agents).
- No force-push, merge, close, or ready-for-review without explicit
  co-founder authorization.
- Default merge target: `Dezocode/Sai:main`.

## Task IDs

`YYYYMMDD-HHMM-<issue-or-purpose>-<agent-id>` (UTC), e.g.
`20260714-0418-sai-agent-framework-cursor-cloud-30d8`.

## Run artifacts

Under `.ai/runs/<task-id>/`: `metadata.json`, `events.jsonl`, `handoff.md`,
and one `NN_stage/output/` directory per executed stage. Do not commit large
generated artifacts, secrets, machine-specific paths, or noisy transcripts.

## Documents

- Plain Markdown and JSON as stage interfaces; no binary formats.
- Every intermediate output must be human-readable and editable.
- Preserve provenance: outputs link to inputs, decisions, commits, agents.

## Application code

No application code conventions exist yet (no code as of 2026-07-14). Add
them here via decision records when the stack is chosen.
