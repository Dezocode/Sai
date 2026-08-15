# Implement — architecture-review

Added executable LOCAL_ARCH / IMPACT_ARCH / SYSTEM_ARCH engine.
Caller must supply repository, base_sha, head_sha — no current
PR/contract/branch/SHA defaults. ARCH-* payloads are in-memory only
(`ledger_write: false`). Cursor/contractor/self-clear is REJECT
`ARCH_CLEARANCE_REQUIRES_AUTHENTIC_SAUL`.

## Files

- `.ai/shared/schemas/saul-architecture-evidence.schema.json` (169)
- `scripts/lib/sai_auth_review_architecture.py` (440 ≤ 500)
- `scripts/lib/sai_auth_review_architecture_test.py` (248 ≤ 500)
- `scripts/verify-saul-architecture-quality` (executable; `--self-test`
  runs the test module; comments reference both python files)

Did not edit code-health.yaml, workflows, coverage/authenticity files,
sai_auth_review.py, live blocker ledger, decisions, authorizations, or
quality docs. Did not PASS. Did not commit. Did not push. Did not merge.
