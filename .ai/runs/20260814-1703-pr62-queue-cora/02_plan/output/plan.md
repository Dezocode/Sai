# Plan — Cora SAUL-IDENTITY-001 reuse of v12

HEAD `11c39ae4443f125a1cf8bd8a49bb04ba49651c3b`. Contract
`20260813-pr62-saul-smoke` v12. Lease `lease-c3a003pr62q1`.
Contractor `ctr-code-pr62smoke`. Task-ID
`20260813-2017-pr62-queue-ctr-code`.

**reuse=true. v13=false. A-013=false.** Identity work sits
under already-granted v12 `allowed_paths`. Not authority
expanding. Not path expansion. denied_paths unchanged.

Coverage:

- Canonical `qualifying_saul_review()` + Ed25519
  attestation (openssl; test keys in fixtures only) →
  `scripts/**`, `tests/**`, optionally `.ai/shared/schemas/**`.
- `attempt_clear` consumes review artifact (not
  `--actor saul`); resume/human_gate/consume share the
  validator; negative spoof tests → `scripts/**`, `tests/**`.
- Hostinger-only bootstrap/attest scripts → `scripts/**`.
- Append SAUL-IDENTITY-001 blocker
  DISCOVERED/IMPLEMENTED_AWAITING_SAUL not PASS →
  `.ai/contracts/20260813-pr62-saul-smoke/**`.
- Do not restore `saul-review.yml`. Production public key
  stays in denied `.ai/authorizations/**` (officer/Sai
  later). Contractor must not generate a production
  private key.

Cora writes: compact REQ-SAUL-IDENTITY-001 on
`requirements/ledger.yaml` (stays ≤300); this wave dir;
standing-run handoff append. Does not write A-013, v13,
blockers/items, scripts, workflows, `_config`,
authorizations, decisions, or `.cursor`. Does not bump
lease or `contract.json`. Commit uses grant Task-ID
`20260813-2016-pr62-queue-cora`. This wave does not push.

Contractor next: implement identity work under v12;
append blocker item without PASS. Only Hostinger Codex
with unforgeable attestation may PASS.
