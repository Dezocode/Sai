# Saul finding → CI regression guard

The Decision-0005 registry is the learning backbone. Saul findings must strengthen it rather than remain one-off review prose.

## Blocking rule

Every blocking Saul finding receives a `quality_guard` disposition before final merge readiness:

1. **deterministic** — preferred when the invariant is mechanically decidable;
2. **heuristic** — bounded CI detector when exact decidability is impractical but the defect class can be usefully detected; or
3. **semantic** — only when automation is genuinely unsuitable. This requires explicit Saul rationale and the invariant remains in Saul review policy; it cannot silently disappear.

For deterministic or heuristic guards, final merge readiness requires:

- a registered check in `.ai/_config/code-health.yaml`;
- mandatory/unconditional CI execution according to Decision 0005;
- positive fixture(s) proving allowed behavior is accepted;
- negative fixture(s) reproducing the defect class and proving it is rejected;
- a link from the blocker/finding to the guard/check id; and
- fail-closed behavior on detector errors where the invariant is blocking.

The learning loop is:

`Saul finding -> blocker -> remediation -> regression guard -> code-health registry -> mandatory CI -> future agents fail earlier/cheaper`.

A contractor fixing the immediate code without the required guard leaves the finding incomplete for merge readiness unless real Saul classifies it `semantic` with explicit non-automation rationale.
