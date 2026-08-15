# Plan — Ralph liveness invariant (v12 reuse)

Parent `pr62-primary`. Lease `lease-c3a003pr62q1`. HEAD
`1185783ae3e98006aafab72a5d8828db0673d04a`. Decision 0009 already
persisted; do not write decisions/** or authorizations/**.
Do not PASS, push, merge, or impersonate Saul.

## Current vs desired

`reconstruct()` remaps playbook to `poteto-continue-frontier` only when
`physical_runtime_continuity` is false AND liveness is
ACTIVE/REPLACEMENT_REQUIRED. Stored WAITING_EXTERNAL keeps
`orchestrate-waiting-external`, so `reassess_blockers` (tied to that
playbook) stays false while continue is true and exit is unsatisfied.

Desired: `logical_program_terminal` only when READY_FOR_HUMAN_REVIEW.
`reassess_blockers` true whenever `exit_predicate_satisfied` is false;
`next_transition` is REASSESS_BLOCKERS. Physical replacement always
OBSERVE then REASSESS even if stored liveness is WAITING_EXTERNAL.
Worker COMPLETE ≠ program complete. Frontier classes A–D as compact
fields. `sai-resume --enforce` exits 1 on Decision-0009 rejects; CI
runs it live. Watchdog SUBAGENT_COMPLETE recommends REASSESS_BLOCKERS.

## File changes

- EDIT `scripts/lib/sai_auth_resume.py` — remap, reassess, frontier,
  `--enforce` (no second engine)
- EDIT `scripts/lib/sai_auth_resume_test.py` — H–L fixtures; tighten D
- EDIT `scripts/lib/sai_auth_watchdog.py` + test — REASSESS_BLOCKERS
- EDIT `.ai/_config/code-health-saul.yaml` — register new fixture names
  on existing `saul-ralph-resume`
- EDIT `.github/workflows/agent-audit.yml` — `scripts/sai-resume --enforce`
- EDIT contract blockers/ledger/evidence after live `--enforce` green
  to IMPLEMENTED_AWAITING_SAUL (never PASSED). CTO-026 stays uncleared.
- Wave run + standing handoff note. Denied paths untouched.

## Verification

Live `scripts/sai-resume` on this tree must show reassess_blockers true.
Then `--enforce`, `--self-test`, watchdog/gated-ci/code-health self-test
and live, `verify-agent-authorization origin/main..HEAD`,
`verify-merge-handoff origin/main..HEAD`, `wc -l` caps.

## Risks / rollback

Over-remapping READY+exit_ok would continue a true terminal — guard
with `predicate_false`. Rollback: revert the commit; coordinator-state
unchanged.

## Human gates

Saul clearance still required. This actor does not PASS, merge, or push.
