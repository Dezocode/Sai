# Runs — per-task working artifacts (Layer 4)

One directory per task, named by task ID:
`YYYYMMDD-HHMM-<issue-or-purpose>-<agent-id>` (UTC), e.g.
`20260714-0418-sai-agent-framework-cursor-cloud-30d8`.

## Required contents

```
<task-id>/
  metadata.json      <- task id, agent, repository, branch, claimed files, status
  events.jsonl       <- every emitted event, one JSON object per line
                        (schema: .ai/shared/schemas/agent-event.schema.json)
  handoff.md         <- final state, evidence, risks, next safe action
  01_intake/output/  <- one output directory per executed stage
  02_plan/output/
  03_implement/output/
  04_verify/output/
  05_review/output/
  06_publish_sync/output/
```

Stages that did not run may be omitted. Each completed stage should also
write `output/manifest.json`
(schema: `.ai/shared/schemas/stage-output.schema.json`).

## Rules

- Run artifacts are the audit trail: commit them with the change they
  document.
- Do **not** commit large generated artifacts, secrets, machine-specific
  paths, or noisy transcripts. Summarize instead and note what was omitted.
- Another agent's run directory is read-only to you; coordinate through
  events and #agentupdates, not by editing someone else's run.
- Humans may edit any `output/` file between stages — that is the ICM review
  gate working as designed. The next stage picks up whatever is on disk.
