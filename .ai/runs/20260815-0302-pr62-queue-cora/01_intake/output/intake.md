# Intake — Cora Saul quality loop reuse of v12

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`. Named child Cora
(`ctr-admin`), physical runtime
`bc-99fab61a-50c8-523a-8e61-64d976db04da`. Grant
`grant-pr62-queue-cora`. Standing commit Task-ID
`20260813-2016-pr62-queue-cora`.

Exact requested outcome: evaluate principal P0
B-SAUL-QUALITY-LOOP-001 / REQ-5300146420 (comment
5300146420) plus cryptographic authenticity spec in
`.ai/shared/quality/saul/AUTHENTICATION.md` (comment
5300187244). Confirm contract `20260813-pr62-saul-smoke`
**v12** already covers executable contractor work without
A-013/v13. Reuse `ctr-code-pr62smoke` and
`lease-c3a003pr62q1`. Append REQ-5300187244 if missing.
Do not write blocker items, scripts, workflows, decisions,
or authorizations. Do not PASS, merge, push, or mark ready.

## Repository facts (command-backed)

- HEAD `516893c68d8d8a77fe43e5e05fe804b3e511a25b` matches
  `origin/cursor/codebase-health-90ba`. Draft PR #62.
- origin/main `40efe0a0724764fc1cf3c45ed8498b5606a0f453`
  (agent-audit.yml only).
- origin `github.com/Dezocode/Sai` canonical, not a fork.
- Working tree clean at intake.
- v12 `current_revision`. allowed_paths already include
  `.ai/runs/**`, `.ai/contracts/20260813-pr62-saul-smoke/**`,
  `tests/**`, `scripts/**`, `.github/workflows/**`,
  `.ai/_config/**`, `.ai/shared/schemas/**`.
- denied_paths: `.ai/agents/saul/**`,
  `.ai/shared/memory/decisions/**`, `.ai/authorizations/**`.
- Lease `lease-c3a003pr62q1` active, revision v12, agent
  `ctr-code-pr62smoke`, Task-ID
  `20260813-2017-pr62-queue-ctr-code`.
- No A-013.yaml / v13.yaml.
- Quality docs under `.ai/shared/quality/**` already landed
  (officer). Contractors must not rewrite them.
- `.ai/_config/code-health.yaml` is 321 lines (>300);
  icm-enforcement FAIL on live HEAD. Split/include under
  `_config/**` is allowed; do not raise global bloat limits.

## Findings (not PASS)

- B-SAUL-QUALITY-LOOP-001 DISCOVERED on ff1005f; principal
  P0 continuous Saul SHA-shard product-quality loop.
- REQ-5300146420 already on requirements/ledger.yaml.
- REQ-5300187244 missing from ledger; AUTHENTICATION.md
  references it. Pubkey pin stays officer/Hostinger
  (`.ai/authorizations/**` denied to contractor).
- Executable machinery maps to v12 allowed_paths:
  scripts/**, tests/**, .github/workflows/**,
  .ai/_config/**, .ai/shared/schemas/**. Quality docs are
  read-only spec; no path expansion to
  `.ai/shared/quality/**` rewrite or authorizations.
- Primary context reconstruction must fail closed
  NO_PRIMARY_CONTEXT / AMBIGUOUS_PRIMARY_CONTEXT with no
  hardcoded current PR/contract/branch/SHA in reusable
  production code.
