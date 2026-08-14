# Verify — Hostinger bootstrap import path

PYTHONPATH unset for all commands below. Did not PASS SAUL-IDENTITY-001.
Did not restore saul-review.yml. Did not push.

## Required

```
unset PYTHONPATH
PYTHONPATH= scripts/sai-blockers --self-test
# 35 fixtures; bootstrap-not-hostinger-saul PASS; exit 0

scripts/saul-hostinger-bootstrap-review --self-test ; echo $?
# stderr: NOT_HOSTINGER_SAUL
# exit: 2

scripts/saul-attest --self-test
# 22 fixtures including bootstrap-not-hostinger-saul; exit 0
```

## Extra

- `scripts/saul-hostinger-bootstrap-review` (no `--self-test`, PYTHONPATH
  unset): imports `sai_auth` via `scripts/lib`, then exits 2
  `NOT_HOSTINGER_SAUL` (missing Hostinger env). Not ModuleNotFoundError.
- `python3 -m py_compile` both edited files: OK
- `scripts/verify-semantic-hierarchy`: OK
- `scripts/verify-agent-audit -n 5 HEAD`: OK
- `scripts/verify-merge-handoff origin/main..HEAD`: OK
- `python3 -m json.tool` metadata.json: OK
- line counts: bootstrap 86; identity_test 236; identity.py 307;
  review.py 500
- `.github/workflows/saul-review.yml` absent

## Skipped

- `verify-code-health` live scan: skipped; no new scripts, no CI wiring
  change, size delta is a few lines.
- push confirmation: skipped; lease forbids push.
