# Intake — ralph-liveness-invariant

Requester: dezocode (U0BHYH0NMCY) via parent logical runtime pr62-primary.
Agent: ctr-code-pr62smoke. Role: Implementation. Contract v12 reuse.
Lease: lease-c3a003pr62q1. COMMIT_TASK_ID: 20260813-2017-pr62-queue-ctr-code.
Cora: `.ai/contracts/20260813-pr62-saul-smoke/reviews/cora-ralph-liveness-v12-reuse.yaml`.

## Requested outcome

Mechanically enforce Ralph continuation. Live bug on HEAD
`1185783ae3e98006aafab72a5d8828db0673d04a`: `scripts/sai-resume`
reconstructs pr62-primary, READY_FOR_HUMAN_REVIEW=false, continue=true,
liveness=WAITING_EXTERNAL, physical_runtime_continuity=false, workers
COMPLETE, but reassess_blockers=false. Ordinary CI green is not completion.

## Repository facts (command-backed)

```
git rev-parse --show-toplevel
/workspace
git remote -v
origin  https://github.com/Dezocode/Sai (fetch/push)
git branch -vv
* cursor/codebase-health-90ba 1185783 [origin/cursor/codebase-health-90ba]
git rev-parse HEAD
1185783ae3e98006aafab72a5d8828db0673d04a
git status
Untracked: .ai/runs/20260815-1935-pr62-queue-ctr-code/events.jsonl
(preserved; not this wave)
```

Canonical repo Dezocode/Sai. Default branch main (40efe0a). This worktree
is the PR #62 branch. Do not push (Primary pushes). Do not merge.

## Constraints

ALLOWED: .ai/runs/**, contract tree, tests/**, scripts/**, workflows,
.ai/_config/**, .ai/shared/schemas/**.
DENIED: .ai/agents/saul/**, decisions/**, authorizations/**, .cursor/**.
Reuse sai-resume, sai-watchdog, verify-saul-gated-ci, antiballoon.
No second Ralph engine. Do not grow code-health.py. YAML≤300 py≤500 md≤600
agent-audit.yml≤300. Never PASS. Cursor is never Saul. Decision 0009 exists.

## Preserve

Untracked 20260815-1935 events.jsonl. Same-agent sequential claim on
scripts/ under lease-c3a003pr62q1; Cora 20260815-2025 complete.
