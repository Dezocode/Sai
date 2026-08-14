# Verify — SAUL-BOOTSTRAP P0

HEAD at plan time: d4e86cbcd9f342a0bae9836483461ec2134b4c17 (Cora v12).

Commands actually run:

- python3 scripts/lib/sai_auth_bootstrap_test.py → 18 fixtures PASS
- scripts/saul-attest --self-test → 22 fixtures PASS (actor=saul spoof still REJECT)
- scripts/sai-blockers --self-test → 53 fixtures PASS (blockers+identity+bootstrap)
- scripts/saul-hostinger-bootstrap-review --self-test → exit 2 NOT_HOSTINGER_SAUL
- PYTHONPATH= scripts/sai-blockers --self-test → 53 PASS
- scripts/invoke-saul-review --self-test → 30 PASS
- scripts/verify-saul-workflow-trust --self-test → 14 PASS
- scripts/verify-agent-authorization --self-test PASS
- scripts/verify-agent-authorization origin/main..HEAD PASS (at Cora HEAD)

Fallback: no `invoke = root` / `attest = root` / root/scripts assign.
saul-review.yml absent.

Line counts: bootstrap.py 97; bootstrap_test.py 293; operator 124;
agent-audit.yml 185; ledger.yaml 74; merge-readiness.yaml 74;
handoff.md 34; sai_auth_review.py 500; sai_auth_test.py 497;
sai_auth_saul_identity.py 307. All within limits.

Mismatch fail-closed: CANDIDATE_HEAD_MISMATCH expected=<sha> actual=<sha>.
Do not PASS. Do not push.
