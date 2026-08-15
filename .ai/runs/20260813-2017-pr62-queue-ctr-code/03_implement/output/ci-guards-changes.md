# Implement — finding-ci-detectors-bloat

Did not PASS. Did not push. Did not merge. Did not raise bloat limits.

## Registry split

- `.ai/_config/code-health.yaml` keeps version/decision/ci/runtime/scan/
  bloat/duplicates/orphans/existing checks plus `include: [code-health-saul.yaml]`.
- `.ai/_config/code-health-saul.yaml` holds four active health-detectors:
  `saul-sha-shard-quality`, `saul-architecture-quality`,
  `saul-authenticity-proof`, `saul-finding-regression-guard`.
- `scripts/lib/code-health.py` `load_config` merges include `checks` and
  optional `saul_quality_learning`. `KNOWN_FIXTURES` unions include
  fixture names. `self_test()` subprocesses the four verify-saul
  `--self-test` scripts if present and parses `SELFTEST PASS  <fixture>`.

## Finding → CI

`scripts/verify-saul-finding-regression-guards` execs
`scripts/lib/sai_auth_finding_guards.py`. Blocking findings require
`quality_guard` DETERMINISTIC|HEURISTIC|SEMANTIC. Linked modes need
`check_id` in the registry. SEMANTIC requires non-empty rationale.
Recurring DETERMINISTIC/HEURISTIC must link a guard.

## Controller

`scripts/saul-review-controller` execs
`scripts/lib/sai_auth_saul_controller.py`. Default convergence
predicate is fail-closed. Shard progress never wakes Sai. Injected
predicate wakes only on technical convergence.

## CI

`.github/workflows/agent-audit.yml` icm-enforcement: chmod +x the four
verify-saul scripts plus `saul-review-controller`; unconditional `run:`
of the four `--self-test` commands (token-prefix match).

## Blocker

B-SAUL-QUALITY-LOOP-001 → IMPLEMENTED_AWAITING_SAUL once the four
verify-saul executables were present locally. Never PASSED.
