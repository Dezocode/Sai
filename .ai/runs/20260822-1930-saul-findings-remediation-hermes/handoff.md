# Handoff — task 20260822-1930-saul-findings-remediation-hermes

## Status
Remediation **in progress**: Saul round-1 findings (review `97075351246` @
`88b29d1`) are fixed in commits `3be4ccc` + `472d597`; Saul round 2
(review `97082894733` @ `472d597`) returned five findings caused by evidence
files referencing terminal events absent from the reviewed tree. This
commit series fixes those five by removing every self-referential or
forward-looking claim:

- In-tree `events.jsonl` now records only events about **ancestor** commits.
- Exact-head verification is delegated to captured ancestor transcripts plus
  GitHub branch CI, which binds check outcomes to each pushed SHA.
- This file describes only evidence present in the reviewed tree.
- Run `metadata.json` stays `in_progress` with an explicit note, because no
  in-tree artifact can truthfully mark this run complete before its own push
  exists.

## Evidence in this tree (all verbatim captures)
- `.ai/runs/20260822-1930-saul-findings-remediation-hermes/04_verify/output/captured-transcripts.md`
  - Capture 1 @ `3be4ccc`: suite output including the expected
    verify-merge-handoff block (this run's handoff not yet staged).
  - Capture 2 @ `472d597` (direct parent of the commit carrying this file):
    hierarchy OK, agent-audit OK, merge-handoff OK (3 task-ids), JSON lint x3,
    events parse (2/8/3).
- `.ai/runs/20260822-1825-pr75-handoff-backfill-hermes/04_verify/output/verification.md`
  points only at files and SHAs present in history.

## Terminal evidence chain (outside any single commit)
GitHub branch CI and PR 75 evidence comments bind check results to exact
pushed SHAs after each push; that is the authoritative post-push record for
the head under review. The genuine Saul review itself remains the required
product gate per the PR contract.

## Risks
- Documentation/audit-artifact change only; no production code touched.
- If HEAD moves again, all in-tree statements remain valid because none of
  them assert results for their own SHA.

## Next safe action
Push this evidence-only commit, confirm branch CI green on it, and let the
exact-head Saul review run again. Do not amend, force-push, merge, or mark
the PR ready; those actions require explicit co-founder authorization.
