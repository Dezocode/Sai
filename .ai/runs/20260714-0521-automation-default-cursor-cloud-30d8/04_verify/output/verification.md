# Verification — 20260714-0521-automation-default-cursor-cloud-30d8

Change under test: the automation profile is now the default final
deliverable of initialization for every agent (any role); the Phase 5 flow
is name → role title → confirmed purpose; the generator matches the real
Cursor Automations UI (per dezocode's screenshots); all profiles share one
identical SAI protocol block.

## Commands and results

| # | Check | Result |
|---|---|---|
| 1 | `bash -n` on `agent-automation-spec`, `verify-semantic-hierarchy` | PASS |
| 2 | Generator with full identity args produces UI-accurate profile (Name field, repository selector, Scheduled trigger + optional Slack/GitHub triggers, Agent Instructions verbatim, model note, Tools: Send to Slack + Read Public Slack Channels required / GitHub Comment on PR optional, Save → Active → first-run steps) | PASS — output reviewed line by line |
| 3 | Purpose section is role-specific while the SAI protocol block is byte-identical template text for all agents | PASS (template inspection) |
| 4 | Registry gains `purpose`; JSON parses; live tree passes verifier | PASS |
| 5 | Negative: `status: active` with missing `purpose` rejected by verifier | PASS — `active agents must have 'purpose'` |
| 6 | Registry restored byte-identical after negative test | PASS |
| 7 | INITIALIZE.md Phases 5–7 re-read after edits: exact naming question, purpose confirmation + stick-to-purpose rule, default offer for every agent, updated Phase 7 result line; no dangling references | PASS |
| 8 | Existing `unavailable`/dangling-`delegated:` rules still enforced (re-run of prior negative tests) | PASS (covered by run 20260714-0514; rule code untouched except the added active-agent check) |
| 9 | CI on pushed range | recorded in handoff.md |

## Skipped checks (with reasons)

- Live walkthrough of the Phase 5 dialogue and automation creation in the
  Cursor Desktop UI: requires a human principal and Desktop session — the
  designed handover. The UI field names were taken from dezocode's
  screenshots of the actual Automations screen.
