# Verification — 20260714-0501-initialize-protocol-cursor-cloud-30d8

Environment: Cursor cloud-agent VM; scratch clone at a temporary path with a
local bare repo as stand-in remote; `SAI_AGENT_ID=init-lab-test` in the lab.
No real tokens used anywhere.

## Commands and results

| # | Check | Result |
|---|---|---|
| S1 | `bash -n` on `agent-init`, `verify-semantic-hierarchy`, `pre-push`, `install-agent-hooks` | PASS (4/4) |
| S2 | JSON parse of `registry.json`; YAML parse of `agent-audit.yml` | PASS |
| S3 | `verify-semantic-hierarchy` against the live tree | PASS (`OK`) |
| N1 | `agent-init` without `SAI_AGENT_ID` | PASS — exit 1, `FAIL agent-id` line |
| N2 | `agent-init` with dirty tree | PASS — exit 0, self-test skipped as WARN (work preserved) |
| N3 | `agent-init` on clean tree | PASS — all checks pass, live hook self-test produced queued events, throwaway branch removed; origin URL printed with credentials stripped (fix applied after first run leaked a placeholder token to stdout) |
| N4 | run dir violating task-id grammar | PASS — caught |
| N5 | run missing `metadata.json` | PASS — caught |
| N6 | `03_implement` without `02_plan`/plan_reference | PASS — caught |
| N7 | unknown stage dir (`07_deploy`) | PASS — caught |
| N8 | Slack-token-shaped secret inside `.ai/` | PASS — caught |
| N9 | clean tree re-check after removing violations | PASS (`OK`) |
| N10 | pre-push to protected `main` with valid trailers but semantic violation | PASS — **blocked**, verifier output shown to pusher |
| N11 | same commit to unprotected ref | PASS — allowed (gate is ref-scoped; CI still checks every push) |
| CI | `agent-audit` workflow on the pushed range | recorded post-push in handoff (both jobs must be green) |

## Skipped checks (with reasons)

- Phases 3–7 of `INITIALIZE.md` as a full live walkthrough by a *fresh*
  agent: requires a Cursor Desktop environment and a human principal to
  grant a name; the mechanical parts (Phase 2) are covered by N1–N3 and the
  Slack/GitHub verifications were exercised by this agent earlier in the
  branch's history.
- Cursor automation creation (Phase 6): not possible from a cloud VM;
  protocol requires agents to record `unavailable: <reason>` honestly,
  which the registry entry for this agent demonstrates.
