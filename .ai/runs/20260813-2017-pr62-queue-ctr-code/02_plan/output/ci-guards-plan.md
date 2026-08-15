# Plan — finding-ci-detectors-bloat (PR #62)

Contractor `ctr-code-pr62smoke`. Work item `finding-ci-detectors-bloat`.
Task-ID `20260813-2017-pr62-queue-ctr-code`. Contract v12. Do not PASS.

## Problem

`.ai/_config/code-health.yaml` is 321 lines (yaml cap 300). CI bloat
fails. REQ-5300146420 needs four active health-detectors with synthetic
fixtures and unconditional `run:` coverage, plus finding→CI guards and a
Sai-wake controller. Do not raise global bloat limits.

## Changes (this slice only)

1. Split registry: main keeps version/decision/ci/runtime/scan/bloat/
   duplicates/orphans/existing checks. `include: [code-health-saul.yaml]`
   holds the four Saul quality checks (three moved + new
   `saul-authenticity-proof`). Both yaml files ≤300.
2. `load_config` merges include `checks` and optional
   `saul_quality_learning`. `KNOWN_FIXTURES` unions include fixture
   names. `self_test()` subprocesses the four `verify-saul-* --self-test`
   scripts if present and parses `SELFTEST PASS  <fixture>`.
3. Implement `verify-saul-finding-regression-guards` +
   `sai_auth_finding_guards.py` (FINDING_TO_CI: DETERMINISTIC/HEURISTIC
   link `check_id`; SEMANTIC requires rationale; recurring must link a
   guard; Z: negative fails when defect present).
4. Implement `saul-review-controller` + `sai_auth_saul_controller.py`.
   Wake Sai only on injected cryptographic convergence predicate
   (default fail-closed). Never on shard progress. Fixtures
   `sai-wake-convergence-once-good` (50 shard events + convergence → 1)
   and `sai-wake-request-changes-zero-good` (REQUEST_CHANGES → 0).
5. Wire four `--self-test` commands as unconditional `run:` in
   `icm-enforcement`; chmod +x those scripts. Keep workflow ≤300.
6. Sister shard/arch/authenticity scripts may be absent; CI wiring and
   registry rows still land. `--self-test` of code-health may fail until
   sisters print the agreed fixture names. Live bloat must go green.
7. Blocker `B-SAUL-QUALITY-LOOP-001`: IMPLEMENTING unless all four
   executables exist, then IMPLEMENTED_AWAITING_SAUL. Never PASSED.

## Verify

- `python3 scripts/lib/sai_auth_finding_guards_test.py`
- `python3 scripts/lib/sai_auth_saul_controller_test.py`
- `scripts/verify-code-health` live scan: no bloat on code-health.yaml
- line counts: both yaml ≤300; `code-health.py` ≤500; workflow ≤300
