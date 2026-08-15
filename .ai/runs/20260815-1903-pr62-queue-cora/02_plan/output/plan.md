# Plan — Cora Decision 0009 ingest, reuse v12

HEAD `abae75d42e675d781be8b4041ea62fc8773defdc`. Contract
`20260813-pr62-saul-smoke` v12. Lease `lease-c3a003pr62q1`.
Contractor `ctr-code-pr62smoke`. Standing Task-ID
`20260813-2016-pr62-queue-cora`.

**reuse=true. v13=false. A-013=false. path_expansion=false.**
Officer Decision 0009 / architecture.md are Sai writes
(`grant-pr62-queue-ceo`, Task-ID
`20260813-2015-pr62-queue-ceo`). Cora does not write those
paths. Contractor executable work already sits under v12
`allowed_paths`. denied_paths unchanged. Not a new human
expansion gate.

## Cora writes (administration only)

1. This wave run `20260815-1903-pr62-queue-cora/` with
   metadata, intake/plan/implement/verify, handoff.md.
2. Compact admin YAML
   `reviews/cora-decision-0009-v12-reuse.yaml`.
3. Compact REQs on `requirements/ledger.yaml` (stay ≤300):
   REQ-5303750100, REQ-5303751556, REQ-5303753512,
   REQ-5303755356, REQ-5303757105.
4. Four blocker items status DISCOVERED, clearance_authority
   saul, do not PASS, plus `blockers/ledger.yaml` index:
   B-SAUL-COMPTROLLER-READINESS-001,
   B-FRONTIER-QUALITY-ARCH-001,
   B-QUALITY-ANTI-BALLOON-001,
   B-RALPH-BLOCKER-CI-CONVERGENCE-001.
5. Standing handoff section on
   `.ai/runs/20260813-2016-pr62-queue-cora/handoff.md`.

Cora does not write A-013, v13, decisions, architecture.md,
authorizations, scripts, workflows, `_config`, schemas, or
`.cursor`. Does not bump lease or `contract.json`. Does not
PASS. Commit locally with grant Task-ID; this wave does
not push.

## Contractor work items (disjoint; Cora does not implement)

1. **comptroller-readiness** — schemas/review-state;
   generated `Saul / Product Quality` and
   `Saul / Blocker / <ID>` Checks from ledger (NOT one
   workflow per blocker); `saul-gated-ci` verifier that
   consumes not mints evidence; no secrets/hardcoded keys.
2. **frontier-quality-arch** — machine-readable
   rust-lang/rust → SAI mapping YAML under contract tree;
   OpenSSF OSPS/Scorecard PASS/NA/DEFERRED/BLOCKER; pin
   privileged checkout SHA if still floating.
3. **anti-balloon** — Decision-0005 detector + fixtures for
   duplicate guards, orphan schemas, per-blocker workflow
   sprawl, etc.
4. **ralph-ci-convergence** — readiness/saul-gated-ci CI
   wiring; fail-closed if required blocker Check missing;
   runner-trust config interface without inventing
   Hostinger labels. Meta blocker PASSes last (Saul only).

Officer next: persist Decision 0009 + architecture.md.
Only Hostinger Codex with unforgeable attestation may PASS.
Do not merge. Do not mark ready.
