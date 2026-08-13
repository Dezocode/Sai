# Pre-contract history remediation options (no RI force-push)

## MEASURED FACT
Commits without Contract-ID on PR #64:
- e9fcfaf Bootstrap …
- e7d9e4e Record stacked sub-PR …
- 46e73c3 Phase C–I …

`verify-agent-authorization origin/cursor/codebase-health-90ba..HEAD` → FAIL (3).

## Options that do NOT invent force-push authority
1. **Co-founder authorized history rewrite** (force-push) after explicit human order.
2. **New stacked PR** replaying tree as contracted commits from parent head (new branch tip; leave #64 open or close by human).
3. **Accept red CI** until human admission with residual risk documented (current default).

RI subprocess will not force-push.
