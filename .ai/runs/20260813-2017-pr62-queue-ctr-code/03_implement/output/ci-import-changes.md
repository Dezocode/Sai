# Implement — Hostinger bootstrap import path

`scripts/saul-hostinger-bootstrap-review` now inserts
`Path(__file__).resolve().parent / "lib"` (`scripts/lib`) instead of
`parent.parent / "lib"` (`REPO/lib`). `--self-test` prints
`NOT_HOSTINGER_SAUL` and exits 2 after stdlib imports, before
`import sai_auth`. Cursor/CI cannot impersonate Hostinger Saul.

`sai_auth_saul_identity_test.py` prepends `scripts/lib` to the bootstrap
subprocess `PYTHONPATH` so the fixture stays hermetic if import order
regresses.

Did not restore `saul-review.yml`. Did not PASS. Did not push.
