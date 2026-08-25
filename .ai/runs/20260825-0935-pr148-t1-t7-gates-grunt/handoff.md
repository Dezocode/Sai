# Handoff — T1/T7 adversarial gates landed and passing
Task-ID: 20260825-0935-pr148-t1-t7-gates-grunt
PR: Dezocode/Sai#148
Author: grunt (ox-alpha)
## What
tests/T1-restart-resume.sh (ledger integrity across simulated crash + resume, idempotent re-commit = no double-drain) and tests/T7-deletion-safety.sh (zero production references to sai-harness + sai-verify kernel builds with the tree deleted). T1 caught a real bug: ticks was missing from migrate.sh's file list — fixed in migrate.sh, not the test.
## Why
Mission acceptance: restart/resume proven; deletion safety proven; no fake evidence (T7 skips honestly with exit 2 if no go toolchain, never fakes a pass).
## Verify
bash tests/T1-restart-resume.sh → T1 PASS; bash tests/T7-deletion-safety.sh (with go on PATH) → T7 PASS.
