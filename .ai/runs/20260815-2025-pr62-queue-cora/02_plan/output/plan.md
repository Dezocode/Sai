# Plan — Cora Ralph liveness-invariant, reuse v12

HEAD `f34bc63635e088fbcd85a400bc2920263b748ab5`.
**reuse=true. v13=false. A-013=false.** No new Decision.
No new blocker IDs. No second Ralph engine. Cora does not
implement. Prefer not to push.

1. Write compact
   `reviews/cora-ralph-liveness-v12-reuse.yaml` (≤300)
   routing `ralph-liveness-invariant` to
   ctr-code-pr62smoke / lease-c3a003pr62q1 under existing
   v12 allowed_paths.
2. Contractor must (Cora records, does not code):
   - `reassess_blockers` true whenever
     `exit_predicate_satisfied` is false. Physical
     replacement always OBSERVE → REASSESS_BLOCKERS.
   - Distinguish `actionable_frontier_empty` from
     `program_complete`. No fifth state DONE. Frontier
     classes A dispatch / B ACTIVE_EXTERNAL_WAIT /
     C HUMAN_BLOCKED / D READY_FOR_HUMAN_REVIEW.
   - Watchdog worker COMPLETE next → REASSESS_BLOCKERS
     after integrate.
   - CI/Decision-0005: live `sai-resume --enforce` (or
     fold into existing verify-saul-gated-ci live) fails
     if READY=false and (false-terminal claim OR
     reassess_blockers false OR continue false OR missing
     ledger/Check projection). Positive+negative fixtures
     on existing `saul-ralph-resume` in
     code-health-saul.yaml. Do not grow code-health.py
     (486/500).
   - Live/repository smoke on THIS tree. Unit tests alone
     insufficient.
   - Reuse sai-resume / watchdog / gated-ci / antiballoon.
   - After live proof MAY set the three blockers to
     IMPLEMENTED_AWAITING_SAUL. Never PASSED. Meta-blocker
     still clears last for Saul.
3. Optional one-line notes on the three existing blocker
   items; status unchanged until contractor live-proof.
4. Wave run 20260815-2025-pr62-queue-cora + standing
   handoff note on 20260813-2016-pr62-queue-cora.
5. implements false. technical_pass false. do_not_pass
   true. Do not merge. Do not push. Do not mark ready.
