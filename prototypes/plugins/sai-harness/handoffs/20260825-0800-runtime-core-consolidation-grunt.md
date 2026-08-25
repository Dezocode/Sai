# Handoff — runtime core consolidation
Task-ID: 20260825-0800-runtime-core-consolidation-grunt
PR: Dezocode/Sai#148 (assist branch, primary integrates)
Author: grunt (ox-alpha)
## What
Consolidated validated cross-intercom prototype scripts into canonical layout, behavior preserved: runtime/ (grokbot daemon, aspectizer, lane-connector), channels/ (sai-channel), gateway/ (audit-gateway), tui/ (landing page). NEW runtime/ci-probe.sh: exact-head CI rollup, exits nonzero on fail (closes counter-drift gap G5).
## Why
#148 mission: converge validated #141/#146 Harness experiments under one canonical tree. Consolidation is verbatim-move + path vars; no behavior change (prototype tier, failClosed:false). ci-probe is the only new logic.
## Verify
bash -n on all four consolidated scripts + ci-probe (all pass). Functional validation deferred to primary integration (T1-T7 suite).
