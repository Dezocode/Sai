# Handoff — Cora Ralph liveness-invariant, reuse v12

reuse=true. v13=false. A-013=false. lease-c3a003pr62q1.
contractor ctr-code-pr62smoke. contract
20260813-pr62-saul-smoke v12 unchanged. HEAD
f34bc63635e088fbcd85a400bc2920263b748ab5.

Live `sai-resume` reconstruct: pr62-primary,
READY_FOR_HUMAN_REVIEW=false, continue=true,
liveness=WAITING_EXTERNAL, reassess_blockers=false,
playbook=orchestrate-waiting-external,
physical_runtime_continuity=false, workers COMPLETE,
exit_predicate_satisfied=false. That skip-reassess
after physical replacement is the defect. CI green is
not completion.

Admin review:
`reviews/cora-ralph-liveness-v12-reuse.yaml`.
implements false. technical_pass false. do_not_merge
true. do_not_push true. Did not create a new Decision
or blocker ID. Did not issue A-013/v13. Status of
B-RALPH-001 / B-NO-IDLE-SAUL-001 /
B-RALPH-BLOCKER-CI-CONVERGENCE-001 unchanged. Cora
did not PASS.

Contractor next: implement the seven constraints in
the review YAML on this tree; live smoke required;
after live proof MAY set the three blockers
IMPLEMENTED_AWAITING_SAUL; never PASSED; meta-blocker
still last for Saul. Do not write a second Ralph
engine. Do not grow code-health.py. Do not PASS. Do
not merge. Do not mark ready. Cursor is not Saul.
