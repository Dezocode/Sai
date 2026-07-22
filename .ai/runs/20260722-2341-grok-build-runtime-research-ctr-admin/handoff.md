# Handoff — 20260722-2341-grok-build-runtime-research-ctr-admin

## Status

Research complete. **Verdict: Grok Build needs a new SAI runtime suite**
when adopted as a first-class org runtime. **No contract drafted.**

## Deliverables

| Path | Content |
|---|---|
| `03_implement/output/research-report.md` | Full verdict, harness map, critique, adoption plan |
| `03_implement/output/proposed-decision-000N-grok-build-runtime.md` | Draft decision extending 0002 |
| `03_implement/output/scaffolding-critique-matrix.md` | Agent × runtime maturity matrix |
| Slack | INTAKE + PLAN posted to #agentupdates |

## Evidence highlights

- Public docs: TUI / `grok -p` / `grok agent stdio`; rules load AGENTS +
  Claude/Cursor compat; hooks trust; `/loop` automation.
- Repo: contract schema and `agent-scaffold` only allow cursor/claude/codex.
- Caps snapshot: cora 25/25, sai 20/20, saul 17/17, mimi 25 (19 verified),
  alpha 0 — Claude SDK harness incomplete vs docs.

## Risks

- Stale `in_progress` run `20260715-1620-contractor-charters-ctr-admin`
  still claims contract/agent paths.
- No live `~/.grok` on research VM.
- Cloud branch prefix differs from charter `ctr-admin/`.

## Next safe action

1. Co-founders (+ Sai) review research report and accept/reject the draft
   decision.
2. On accept: new task to file decision + implement `GROK.md` /
   `runtimes/grok/` scaffolding / schema enum / templates (separate from
   any contractor contract).
3. On reject: record rejection reason in a follow-up HANDOFF; keep using
   Grok informally without registry `primary_runtime`.
4. Do **not** register a Grok-primary agent or open a Grok contractor
   contract until step 2 lands and Phase 5B can run against a real `grok`
   binary.

## Drive

pending
