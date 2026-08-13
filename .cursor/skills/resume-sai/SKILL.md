---
name: resume-sai
description: Reconstruct and resume the latest active SAI primary program from durable repo/control-plane state. Use for session pickup, after a physical Cloud turn ends, or when asked to /resume-sai. Do not replay the conversation or redo completed work.
---

# /resume-sai

You are picking up the **same logical SAI primary**, not starting a new architecture program.

## Do this first

Run (no model required for the reconstruction itself):

```bash
scripts/sai-resume
```

Read the JSON. That object is the reconstructed state.

Then run a read-only watchdog pass (still no status-model):

```bash
scripts/sai-watchdog
```

## Required fields you now own

Use the script output, then refresh anything the script marks stale against **live** git/GitHub (never reset to an older SHA):

- primary logical ID
- last physical bcId
- repo, primary PR, branch, head SHA
- contract / revision
- requirement ledger
- Cora admin state
- contractor state
- worker/subagent tree (organizational identity, not task titles)
- latest Saul disposition
- latest Sai disposition
- CI
- event inbox
- expected next state
- last material transition
- exit predicate
- liveness

## Continue matching playbook

| `playbook` / `liveness` | You do |
|---|---|
| `orchestrate-drain-workers` / `WAITING_WORKER` | Drain completion events. Integrate. Recompute exit predicate. Do **not** terminate because children finished. |
| `orchestrate-waiting-external` / `WAITING_EXTERNAL` | Do not model-poll. Persist pickup. If a new material event exists, drain it. |
| `poteto-continue-frontier` / `ACTIVE` | Frame, brief, spawn bounded workers, integrate. Primary owns the program, not every code slice. |
| `READY_FOR_HUMAN_REVIEW` | Stop for Dezocode. Do not merge. Do not mark ready. |

## Hard rules

- Inherit prior state. Do not rederive completed investigation or implementation.
- Verify inherited claims against current repo truth (`git fetch`, PR head, Saul comment).
- Empty todo list ≠ exit. Worker completion is a queue event.
- Task title ≠ SAI identity. Persist `agent_id`, `name`, `role`, parents, contract, lease/grant, work-item, base SHA, model, state.
- Cora (`ctr-admin`) is a named bounded subagent for contract administration only. Do not make Cora implement. Do not stream worker transcripts to Cora.
- Do not resume a worker merely to inspect it. Read durable status.
- Heartbeat is `scripts/sai-watchdog` (default 1500s). It must not invoke a model just to compare status.
- At most **two** active primary implementation programs unless Dezocode overrides. Stacked / Runtime Intelligence / telemetry / read-only verification PRs do not consume a slot.
- Physical same-`bcId` follow-up exists only as `POST /v1/agents/{id}/runs` or SDK `Agent.resume`+`send` **with a prompt**. Silent GitHub→same-turn wake is unsupported. If physical resume is unavailable, this skill **is** the logical P1 pickup.
- READY_FOR_HUMAN_REVIEW requires real Hostinger Saul Codex APPROVE + Sai APPROVE of the exact head/revision, CI green, no P0/P1, no REQUEST_CHANGES, no expansion gate. Documentation is not that proof.
- Do not merge. Do not mark the PR ready.
