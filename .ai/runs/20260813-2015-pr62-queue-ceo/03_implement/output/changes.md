# Implement — grant task_id aliases (HEAD)

Officer-only. No scripts, workflows, or blocker PASS.

| File | Change |
|---|---|
| `.ai/authorizations/grants/grant-pr62-queue-ceo.yaml` | Keep `task_id: 20260813-2015-pr62-queue-ceo`. Add `task_ids` listing that id plus `20260814-0052-pr62-queue-ceo`. |
| `.ai/authorizations/grants/grant-pr62-queue-cora.yaml` | Keep `task_id: 20260813-2016-pr62-queue-cora`. Add `task_ids` listing that id plus `20260814-0041-pr62-queue-cora` and `20260814-0052-pr62-queue-cora`. |
| `.ai/runs/20260813-2015-pr62-queue-ceo/handoff.md` | Append alias note. |

Why: later queue Task-IDs must be listed on HEAD grants so contractor
HEAD-union aliasing can authorize them. History is not rewritten.
The alias commit itself uses the original grant `task_id` so it matches
the grant at parent SHA.
