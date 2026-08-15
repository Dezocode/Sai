# Verify — finding-ci-detectors-bloat

Did not PASS. Did not push. Did not merge. Did not raise bloat limits.

## Required tests

```
python3 scripts/lib/sai_auth_finding_guards_test.py
# 11 SELFTEST PASS (finding-*-good / finding-*-bad); OK

python3 scripts/lib/sai_auth_saul_controller_test.py
# SELFTEST PASS  sai-wake-convergence-once-good
# SELFTEST PASS  sai-wake-request-changes-zero-good
# OK

scripts/verify-saul-finding-regression-guards --self-test
# 11 fixtures executed; exit 0

scripts/saul-review-controller --self-test
# 2 fixtures executed; exit 0

scripts/verify-code-health bloat
# PASS  bloat (no fail on .ai/_config/code-health.yaml)
# exit 0

scripts/verify-code-health
# 44 PASS unstaged; 45 PASS with exclusive files staged
# ci-coverage saul-sha-shard-quality/architecture/authenticity/finding-regression-guard executed
# exit 0
```

`scripts/verify-code-health --self-test` also exit 0 once sister
verify-saul-{shard,architecture,authenticity} scripts were present and
printed the coordinated fixture names.

## Line counts

| file | lines | cap |
|---|---|---|
| `.ai/_config/code-health.yaml` | 298 | 300 |
| `.ai/_config/code-health-saul.yaml` | 81 | 300 |
| `scripts/lib/code-health.py` | 500 | 500 |
| `.github/workflows/agent-audit.yml` | 194 | 300 |
| blockers/ledger.yaml | 76 | 300 |

## Registry (merged)

- saul-sha-shard-quality: active / synthetic
- saul-architecture-quality: active / synthetic
- saul-authenticity-proof: active / synthetic
- saul-finding-regression-guard: active / synthetic

## Blocker

B-SAUL-QUALITY-LOOP-001 = IMPLEMENTED_AWAITING_SAUL. Not PASSED.
