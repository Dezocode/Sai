# Intake — Cora SAUL-IDENTITY-001 reuse of v12

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`. Named child Cora
(`ctr-admin`), physical runtime
`bc-9907f1f9-81ac-5df6-9880-2879398a4f54`. Grant
`grant-pr62-queue-cora`. Standing commit Task-ID
`20260813-2016-pr62-queue-cora`.

Exact requested outcome: confirm contract
`20260813-pr62-saul-smoke` **v12** already covers
SAUL-IDENTITY-001. Reuse `ctr-code-pr62smoke` and
`lease-c3a003pr62q1`. Do not issue A-013/v13 unless paths
expand. Append REQ-SAUL-IDENTITY-001 to
`requirements/ledger.yaml` (YAML ≤300). Do not write
blocker items, scripts, workflows, decisions, or
authorizations. Do not PASS, merge, push, or mark ready.

## Repository facts (command-backed)

- HEAD `11c39ae4443f125a1cf8bd8a49bb04ba49651c3b` matches
  `origin/cursor/codebase-health-90ba`. Draft PR #62.
- origin/main `40efe0a0724764fc1cf3c45ed8498b5606a0f453`
  (agent-audit.yml only).
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

## Findings (not PASS)

- Principal VOIDED the Cursor-named-subagent Saul APPROVE
  (`codex_invoked=false`). That false projection is
  historical evidence, not deleted. Logical state restored
  to WAITING_EXTERNAL.
- P0 SAUL-IDENTITY-001: only Hostinger Codex with
  unforgeable attestation may PASS. Do not self-PASS.
- Production attestation public key belongs in
  `.ai/authorizations/` later (officer/Sai after Hostinger
  generates it). Contractor must not write that tree or
  generate/commit a production private key.
- Test keys only in fixtures (`tests/**`).
