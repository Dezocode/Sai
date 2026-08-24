# Handoff — Round-18 honest metrics (PR 77)

## What changed
- scripts/render-sai-feature-maps posNum(): null/undefined/"" now mean "not
  reported" -> unknown; real 0 stays a valid measurement. Previously
  Number(null)===0 made explicit-null tokens render invented "0 tok" and
  file_count:null render "0 files" (queued STEER Acceptance delta).
- Selftest: 5 new assertions (explicit-null tokens degrade, null total falls
  back to in/out, real zero stays valid "0 tok", empty-string degrades,
  null file_count never "0 files" while real insertions still render).
- --check prs-probe: new null_metrics /prs case through the shipped
  SESSIONS_JS asserting no "0 tok"/"0 files" and "+3 / -1" preserved;
  probe OK-line updated.

## Verification at authoring time
python3 -m py_compile OK; --selftest ALL PASS; --check ALL PASS features=11
with prs-probe incl. null-metrics; node --check emitted inline JS clean for
both pages; verify-semantic-hierarchy OK; verify-merge-handoff OK.

## Next
Await CI + real-Codex Saul re-bind to pushed HEAD; stay draft; remaining
Acceptance deltas queued (sai-sessions-v2 per-row validation badge,
shortSha client-side, smoke-stub honest-block, evidence comment).
