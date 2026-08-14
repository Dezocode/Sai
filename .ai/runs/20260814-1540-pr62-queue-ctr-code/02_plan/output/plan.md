# Plan — TPR-001 / TPR-002 (v12 reuse)

HEAD `effc68a2ebce9d1b6dc9f420654e431785d0e399`. Contract v12.
Lease `lease-c3a003pr62q1`. Agent `ctr-code-pr62smoke`.
Task-ID `20260813-2017-pr62-queue-ctr-code`. Wave `20260814-1540`.

Do not PASS. Do not merge. Do not push. Do not restore
`saul-review.yml`. Do not write denied_paths. Do not rework
CTO-015..030. Do not grow `sai_auth_review.py` or
`sai_auth_test.py` past 500. Do not raise yaml 300 / py 500 /
md 600. Do not add `on: pull_request` to self-hosted workflows.
Do not execute freeze-from-candidate. Do not delete Decision 0008.

## TPR-001

DELETE `.github/workflows/trusted-reviewer-provision.yml`.
Stop `sai_auth_wait.py` provisioner snapshot poll. Keep
`provision-trusted-reviewer-root` python + `--self-test`.
`assert_provisioner_workflow()` rejects synthetic
`checkout ref: from_sha` then `run: scripts/provision-trusted-reviewer-root`.
Live tree: file absent ⇒ PASS.

## TPR-002

Default `SAI_CODEX_SANDBOX=workspace-write`. Keep `--ephemeral`.
Add `--ignore-user-config` on the skip-git line. Helper
`codex_exec_env` in `sai_auth_package.py` strips
GITHUB_TOKEN/GH_TOKEN/SSH_AUTH_SOCK/DOCKER_HOST; keeps model
keys. Remove `GITHUB_TOKEN` from Invoke Codex `env:`. Keep
token on Post/Status/Claim. Retarget sandbox fixture in place.

## Tests

New `scripts/lib/sai_auth_tpr_test.py` proving A–H. Call from
`verify-saul-workflow-trust --self-test` and
`invoke-saul-review --self-test`. Wrapper comments so orphans PASS.
Reuse existing B/C/G fixtures; do not duplicate.

## Ledger

TPR-001.yaml / TPR-002.yaml quoted style.
`IMPLEMENTED_AWAITING_SAUL`. clearance_authority saul.
Index in ledger.yaml. Update merge-readiness + threat-trace
one-liners. Residual: Codex model credential; Landlock may be
weak in Hostinger container; runner-group UNKNOWN/VERIFY_REQUIRED.
