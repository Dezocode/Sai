# SAI — Coding and workflow conventions

> Durable, verified conventions only. Supersede rather than silently rewrite.

## Git

- One logical change per commit, descriptive outcome-oriented message.
- Commit trailers where supported: `Task-ID:`, `Agent:`, `Plan:`,
  `Report-Event:`.
- Branch naming: `ceo/<slug>`, `dezo/<slug>`, `monae/<slug>`,
  `cursor/<slug>-<suffix>` (cloud agents), `ctr-admin/<slug>` (contract
  administrator), `proj/<project-slug>/<ctr-agent-id>/<task-slug>`
  (contractors).
- Contractor agent IDs: `ctr-code-<suffix>` (coding), `ctr-design-<suffix>`
  (design). Contract administrator: `ctr-admin` or `ctr-admin-<suffix>`.
- No force-push, merge, close, or ready-for-review without explicit
  co-founder authorization.
- Default merge target: `Dezocode/Sai:main`.

## Task IDs

`YYYYMMDD-HHMM-<issue-or-purpose>-<agent-id>` (UTC), e.g.
`20260714-0418-sai-agent-framework-cursor-cloud-30d8`.

## Run artifacts

Under `.ai/runs/<task-id>/`: `metadata.json`, `events.jsonl`, `handoff.md`,
and one `NN_stage/output/` directory per executed stage. Do not commit large
generated artifacts, secrets, machine-specific paths, noisy transcripts, or
personal email addresses. Identify people by username and Slack ID only.

## Cursor plugins

- Enable marketplace plugins in committed `.cursor/settings.json`
  (`plugins.<slug>.enabled: true`) so Cloud Agents and local Cursor share
  the same `/` command input.
- Index each enabled plugin under `.ai/plugins/<slug>/` (manifest + README).
  `.ai/plugins/` is documentation, not a Cursor loader.
- Do not copy plugin skill trees into `.cursor/skills/` (duplicate slash
  names) or into `.ai/` expecting `/` registration.
- Do not put plugins in `environment.json`.

## Documents

- Plain Markdown and JSON as stage interfaces; no binary formats.
- Every intermediate output must be human-readable and editable.
- Preserve provenance: outputs link to inputs, decisions, commits, agents.

## Application code

No accepted application stack yet (DR-20260724). Until a stack decision
exists, every change still runs `scripts/verify-code-health` (bloat,
duplicates, orphans, CI coverage). When the stack is chosen, promote the
deferred rows in `.ai/_config/code-health.yaml` and record language
conventions here in the same commit.
