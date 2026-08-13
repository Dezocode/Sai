# Cursor capability findings (2026-08-13)

Workers: wake research, pstack research, CTO-012, first-write cue.
Sources: cursor.com docs fetched 2026-08-13; pstack `63d938c2e4a1` (0.14.1).

| Claim | Class |
|---|---|
| Same `bcId` follow-up via `POST /v1/agents/{id}/runs` or SDK `Agent.resume` + `send` (prompt required; new run) | DOCUMENTED |
| GitHub/Hostinger silently resumes a paused interactive Cloud turn | UNSUPPORTED |
| Automations on workflow/CI completed start a **new** cloud agent | DOCUMENTED |
| `/loop` only while that conversation is still armed | DOCUMENTED |
| `/babysit` / `/in-cloud` are a different `bcId` | DOCUMENTED |
| This Cloud session did not load project pstack slash commands | OBSERVED |
| `/setup-pstack` home-dir rules do not persist on Cloud VMs | DOCUMENTED / INFERRED |
| Nested Task workers have a different `bcId` than the Slack primary | OBSERVED |

`physical_runtime_continuity` after WAITING_EXTERNAL: **false**.
`logical_runtime_continuity` via `coordinator-state.json` + session-pickup: **required fallback**.
Do not invent a GitHub→same-turn auto-resume hook. Do not add separately billed architecture without dezocode approval.
