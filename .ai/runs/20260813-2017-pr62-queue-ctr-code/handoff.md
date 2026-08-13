# Handoff — contractor (resume-sai control plane + trusted-root provisioner)

Contract `20260813-pr62-saul-smoke` v3, lease `lease-c3a003pr62q1`.
Base at start of this slice: `2ac83a149bfa69c2ce7e0c7675c492b45dba82f2`.

## What landed

- `scripts/sai-resume` reconstructs the latest nonterminal logical primary
  from `coordinator-state.json` and **refreshes live HEAD**. Empty workers
  do not satisfy the exit predicate.
- `scripts/sai-runtime-registry` named identity (Cora `ctr-admin` vs task
  title). Cora does not wake on healthy progress.
- `scripts/sai-watchdog` 1500s heartbeat: healthy NOOP, complete queues
  `SUBAGENT_COMPLETE`, stale queues `STALE_WORKER`, no model.
- Two-primary cap in `.ai/_config/primary-programs.yaml`; RI/stacked exempt.
- `scripts/provision-trusted-reviewer-root` refuses symbolic/candidate HEAD
  unless `--confirm-trust`. `saul-review.yml` also reads
  `/opt/sai/trusted-reviewer`. Provision workflow never runs on pull_request.
- Ledger `REQ-5287297355`. Orphan refs for cue/event/saul test modules.

## Next

Sai commit: Decision 0008, `/resume-sai` skill, architecture projection.
Do not merge. Do not mark ready. Saul remains BLOCKED until Hostinger
root is provisioned from a trusted SHA.
