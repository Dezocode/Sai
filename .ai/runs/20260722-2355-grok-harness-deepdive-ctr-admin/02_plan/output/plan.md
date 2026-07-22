# Plan — 20260722-2355-grok-harness-deepdive-ctr-admin

## Current → desired

| Current | Desired |
|---|---|
| Prior run recommends peer `runtimes/grok/` but scaffold depth is high-level | Explicit Tier S/A/B/C → future SAI file inventory |
| Scaffolding critique is agent×suite maturity scores | File-level critique vs `agent-runtimes.md` + `claude-agent-sdk.md` with evidence |
| Draft decision exists but unfiled | Keep draft; refine consequences using harness map; still no contract |

## Proposed file changes (this task only)

All under `.ai/runs/20260722-2355-grok-harness-deepdive-ctr-admin/`:

1. `01_intake/output/intake.md` — requester, repo facts, constraints
2. `02_plan/output/plan.md` — this plan
3. `03_implement/output/research-addendum.md` — deepened verdict + harness→scaffold map
4. `03_implement/output/runtime-maturity-rubric.md` — objective scoring rubric
5. `03_implement/output/scaffolding-critique-filelevel.md` — per-agent file critique
6. `03_implement/output/proposed-grok-suite-inventory.md` — future `runtimes/grok/` file list (not created)
7. `04_verify` / `05_review` / `06_publish_sync` + `handoff.md` / `events.jsonl`

**Explicit non-edits:** `.ai/agents/**`, schemas, scripts, `GROK.md`, contracts, decisions/.

## Justification

Operator provided ranked harness inventory. Co-founders need a scaffold
blueprint before authorizing enum/schema work or contractor contracts.
Cora charter: contract intake gathers `primary_runtime` — cannot honestly
offer `grok` until suite shape is decided.

## Verification

- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit -n 10 HEAD` (after commit)
- `scripts/verify-merge-handoff origin/main..HEAD`
- JSON lint on metadata / manifests / events

## Risks / rollback

- Risk: research drift vs prior PR #47 — mitigate by citing parent task and
  restating same verdict with refinements only.
- Rollback: abandon run dir + HANDOFF if co-founders reject follow-up scope.

## Review gates

- Architecture decision filing: **human gate** (not this task).
- PLAN Slack posted before implement artifacts (done).

## Claims

`.ai/runs/20260722-2355-grok-harness-deepdive-ctr-admin/` only.
