# Verification — contractor blocker ledger / wait / trust pin

Commands (cwd `/workspace`, PYTHONPATH=scripts/lib):

- `scripts/sai-blockers --self-test` — 7 fixtures PASS (append, cursor/contractor self-pass reject, Saul pass, history retained, Sai governance, IMPLEMENTED ≠ PASSED)
- `scripts/sai-wait --self-test` — 2 fixtures PASS (early wake, no model)
- `scripts/sai-resume --self-test` — 6 fixtures PASS including `resume-rejects-mismatched-saul-snapshot`
- `scripts/provision-trusted-reviewer-root --self-test` — 5 fixtures PASS including `candidate-mutation-does-not-change-root`
- `scripts/sai-watchdog --self-test` — 7 fixtures PASS
- `scripts/invoke-saul-review --self-test` — 18 fixtures PASS (CTO-012 still fail-closed)
- `scripts/verify-semantic-hierarchy` — OK
- `scripts/verify-code-health` — 38 PASS
- YAML/JSON parse of ledgers, workflows, metadata — OK

Not claimed: READY_FOR_HUMAN_REVIEW. Technical PASS awaits qualifying Saul (`codex_invoked=true`). B-RESUME-001 is IMPLEMENTED_AWAITING_SAUL. B-TRUST-001 still open until runner freeze.
