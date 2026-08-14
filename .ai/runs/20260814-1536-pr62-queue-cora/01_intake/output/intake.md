# Intake — Cora TPR-001/002 reuse of v12

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`. Named child Cora
(`ctr-admin`), physical runtime
`bc-1769f84e-3789-574c-b84c-342fcfdb0bfb`.

Exact requested outcome: evaluate whether existing contract
`20260813-pr62-saul-smoke` **v12** already covers remediating
TPR-001 and TPR-002. Principal steering: it does. REUSE
`ctr-code-pr62smoke` and `lease-c3a003pr62q1`. Do not create
A-013/v13. Do not allocate CTO numbers. Optional: append
REQ-TPR-001 / REQ-TPR-002 to `requirements/ledger.yaml` if
YAML stays ≤300. Contractor writes blocker items. Cora does
not implement, PASS, merge, push, or mark ready.

## Repository facts (command-backed)

- HEAD `01fe60609d6d61d71cb401a06619b71601ed94f6` matches
  `origin/cursor/codebase-health-90ba`.
- v12 allowed_paths already include `.github/workflows/**`,
  `scripts/**`, `tests/**`, `.ai/contracts/20260813-pr62-saul-smoke/**`,
  `.ai/_config/**`, `.ai/shared/schemas/**`, `.ai/runs/**`.
- denied_paths unchanged.
- Lease `lease-c3a003pr62q1` active, revision v12.
- `sai_auth_review.py` 500 lines; `sai_auth_test.py` 497.

## Findings (Primary-confirmed; Saul still clears; not PASS)

- TPR-001: `trusted-reviewer-provision.yml` `workflow_dispatch`
  `from_sha` → checkout that SHA → execute provision scripts
  from that checkout. Circular trust. Preferred: DELETE the
  workflow. Stop polling it in `sai_auth_wait.py`.
- TPR-002: `_codex_cmd` defaults `SAI_CODEX_SANDBOX` to
  `danger-full-access`; Invoke Codex step passes `GITHUB_TOKEN`.
  Smallest fix: default `workspace-write` or `read-only`; strip
  token/socket vars from Codex subprocess env after package
  build; remove them from Invoke Codex `env:`.
