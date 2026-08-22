# Handoff — task 20260822-2020-pr75-contract-rescope-hermes

## Status
In progress at time of writing; terminal state is established post-push by
branch CI bound to exact SHAs and the next genuine Saul review (see
Evidence-chain discipline below).

## What was done
Resolved the Saul round-3 P1 (head `d9934ee`): "the enabling PR promises a
runnable prototype but contains no prototype implementation." Took the
remedy the finding itself offers: **rescope PR 75 as contract-only** and
defer implementation to named successor PRs. Rationale: implementation
requires macOS/iOS Simulator build proof that this repository's CI cannot
honestly produce; claiming buildability without executing builds would
violate exact-head evidence rules.

- `docs/architecture/SAI-PROTOTYPE-PLUGIN-LANE.md`: status now explicitly
  contract-only; new "Successor work" section names `prototype/lane-enforcement`
  and `prototype/sai-author-shell` with their required proofs; adversarial
  acceptance and merge-gate sections re-scoped so each requirement sits with
  the PR that can actually prove it.
- PR body updated via API to match the doc (recorded in this run's events).
- Successor work is fully specified, so implementation can start under fresh
  Task-IDs without re-litigating scope.

## Evidence in this tree
`04_verify/output/captured-transcripts.md` holds verbatim captures on
`5389fbd` (pre-handoff-staging): hierarchy OK, agent-audit OK,
merge-handoff FAIL solely because this run's handoff was intentionally not
yet staged — the gate working as designed.

## Evidence-chain discipline
No file or event in any commit claims verification results for its own SHA.
Ancestor captures live in-tree; post-push binding is carried by GitHub
branch CI and PR 75 evidence comments, which name exact SHAs.

## Risks
- Documentation-only change; no production code touched.
- Scope decision (contract-first) follows the reviewer's offered remedy;
  if dezocode prefers implementation-first instead, successor PR 2
  (`prototype/sai-author-shell`) is already specified and unblocked.

## Next safe action
Commit staged handoff, run full gates on the final head, push, verify
remote SHA, confirm CI, and await fresh exact-head Saul review. PR remains
DRAFT until P0=P1=P2=0 and an owner explicitly chooses to merge.
