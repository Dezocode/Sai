# Plan — SAUL-IDENTITY-001 Hostinger attestation

## Current vs desired

`attempt_clear` treats `actor=="saul"` as Saul. `resume.exit_satisfied`
treats `disposition==APPROVE` as Saul. `human_gate` checks spoofable YAML
fields only. A Cursor named subagent was projected as Saul.

Desired: every Saul gate imports `scripts/lib/sai_auth_saul_identity.py`
and fail-closes unless a Hostinger Codex review is Ed25519-signed over a
canonical payload bound to exact HEAD + contract revision. Actor strings
are not identity. Do not PASS SAUL-IDENTITY-001. Do not merge/push.

## File changes

- NEW `scripts/lib/sai_auth_saul_identity.py` — canonical qualify/sign/verify
- NEW `scripts/lib/sai_auth_saul_identity_test.py` — negative fixtures + one positive
- NEW `scripts/saul-attest` — sign/verify/--self-test; refuse in-tree keys
- NEW `scripts/saul-hostinger-bootstrap-review` — Hostinger-only; Cursor exits 2
- `scripts/lib/sai_auth_blockers.py` — attempt_clear requires qualifying artifact
- `scripts/lib/sai_auth_resume.py` — merge_viable_saul; void invalid READY
- `scripts/lib/sai_auth_verify.py` — human_gate calls qualifying_saul_review
- `scripts/lib/sai_auth_review.py` — consume APPROVE requires qualifying identity
- `.github/workflows/saul-cto-review.default-branch.yml` — attest step if key exists
- `.github/workflows/agent-audit.yml` — `saul-attest --self-test`
- blockers item `SAUL-IDENTITY-001` DISCOVERED/IMPLEMENTED_AWAITING_SAUL, not PASS
- merge-readiness note: WAITING_EXTERNAL; voided Cursor Saul APPROVE

## Denied

No `.ai/agents/saul/**`, `.ai/authorizations/**`, decisions, production
private keys, saul-review.yml, trusted-reviewer-provision.yml.

## Verify

`sai-blockers --self-test`, `saul-attest --self-test`,
`invoke-saul-review --self-test`, `verify-saul-workflow-trust --self-test`,
`verify-agent-authorization`, `sai-resume --self-test`. Line limits.
`actor=="saul"` must not grant PASS.
