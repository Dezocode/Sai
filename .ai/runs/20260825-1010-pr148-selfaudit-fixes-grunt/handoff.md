# Handoff — self-audit fixes: migration completeness + feature-map claims
Task-ID: 20260825-1010-pr148-selfaudit-fixes-grunt
PR: Dezocode/Sai#148
Author: grunt (ox-alpha)
## What
(1) migrate.sh now migrates requeue/, dead-letter/, launches/ dirs (retry/dead-letter state acceptance was incomplete). (2) cursor-runtimes.md claims the new prototypes/plugins/sai-harness/* paths + docs — pre-empts the icm completeness-sweep failure that hit #141 (TestLinkedWorktreeHook / unmapped files).
## Why
Mission acceptance: retry/dead-letter state handled explicitly; sai-verify maps surface. Self-audit against the #148 checklist found both gaps before CI did.
## Verify
T1 still passes; feature-map claim lines present in cursor-runtimes.md; pathRe admits prototypes/* (landed via #141 lineage).
