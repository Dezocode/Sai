# Handoff — fix(proto): adopt grunt's exponential backoff — self-heal requeue 2^(n-1)s capped 300s

Task-ID: 20260825-0115-backoff-converge-her
Commit: a636cffeaf250a1c109d5741c7ff5e62b6fe75dc
PR lane: prototype/cross-intercom-lane (#146 lineage)
Author: her (ox-alpha via her runtime)

## What
fix(proto): adopt grunt's exponential backoff — self-heal requeue 2^(n-1)s capped 300s.

## Why
Part of the validated cross-intercom prototype lineage converged under #146; handoff retro-docum
ented during the 2026-08-25 CI repair (owner-approved, grunt assist).

## Verify
Commit present in lineage; behavior covered by prototype-lane tests and #146 review.
