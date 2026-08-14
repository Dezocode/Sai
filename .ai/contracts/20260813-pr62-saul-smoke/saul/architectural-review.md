# Architectural review contract (Saul package)

Contract `20260813-pr62-saul-smoke` v10. Classification:
`REQUIRED_FOR_FINAL_MERGE_QUALITY`. Do not rewrite `.ai/agents/saul/**`.
This file is a candidate-packaged evaluation contract. It is not a PASS.

Saul evaluates **two planes** on the exact head:

1. **Defect plane** — correctness, security, authorization, CI, trust
   boundary, tests, regressions.
2. **Architectural merge-readiness plane** — whether this exact state is
   a sound design for `main`: trust topology, simplicity, transitional
   retirement, bounded PR, attack surface, rollback, operational
   ownership.

Saul may **amend/reframe** his own blockers with history preserved.
Saul must not weaken: candidate is DATA; never candidate-HEAD trust;
never checkout PR head into a trusted CWD then execute.

`CONDITIONAL_PASS_ON_HUMAN_MERGE` is **Saul-only**. Cora/contractor/Sai
must not emit it as clearance. It is not agent merge permission.
Eligible only when all ten principal predicates hold:

1. Artifact complete and reviewed in the candidate.
2. Only missing property is "now on protected main".
3. Human merge of this PR establishes that property.
4. Candidate cannot exploit the transition.
5. Secrets and privileged runners protected.
6. Least privilege; fail closed.
7. Rollback understood.
8. No hidden independent P0/P1 defect.
9. Record condition, exact SHA, activation event, post-merge state,
   risk, rollback, and verification.
10. Do not treat the classification as merge permission.

## Required output sections

Saul's qualifying review of this exact head MUST include:

### CURRENT EXACT STATE
SHA, revision, CI, which workflows exist on the candidate vs
`origin/main`.

### ARCHITECTURAL VERDICT
Whether merge-activation of
`saul-cto-review.default-branch.yml` via human merge of PR #62 is
sound, or a concrete threat trace if not.

### QUALITY VERDICT
Evaluate `quality-profile.yaml`. Do not claim an SLSA level. Do not
fabricate PASS for uninspectable repo settings.

### P0..Pn
Independent defects. Already-ledgered items stay there unless Saul
amends them with history.

### MERGE-CONDITIONAL ITEMS
Any `CONDITIONAL_PASS_ON_HUMAN_MERGE` with the ten predicates proven
or explicitly failed.

### DEFERRED NONBLOCKING
Follow-ups that must not block human review (pinned actions,
runner-group inspection, collaborator dispatch residual).

### PR BLOAT / COMPLEXITY
Apply `.ai/_config/pr-ballooning.yaml`. Flag excessive scope as an
architectural finding, not a new failing CI check.

### TRUST-BOUNDARY
Candidate DATA vs trusted executable tree. Confirm trusted `run:`
does not execute `candidate-data/scripts`.

### WHAT WOULD PREVENT MAIN REGRESSION
`git cat-file -e origin/main:.github/workflows/saul-cto-review.default-branch.yml`
after merge; confirm `saul-review.yml` on main has no `pull_request`
trigger.

### SMALLEST NEXT REMEDIATION FRONTIER
If not merge-viable: the smallest next machine or human action. Do
not demand an intermediate bootstrap PR when merge-activation is safe.

Do not merge. Do not mark ready. Do not PASS from this contract file.
