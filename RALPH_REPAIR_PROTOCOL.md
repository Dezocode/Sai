# Ralph Recursive Repair Protocol

A repair loop is evidence-driven and bounded.

1. Read the failing command and raw evidence.
2. Identify the canonical owner of the failing responsibility.
3. Search for an existing implementation before creating anything.
4. Form one root-cause hypothesis.
5. Make the smallest safe edit inside the claimed scope.
6. Re-run the exact failing check.
7. If it passes, re-run the owning gate.
8. Re-run cumulative FAST checks.
9. Force DEEP if the edit touches architecture, security, dependencies, CI, migrations, auth, policy, or scanner configuration.
10. Record evidence.

After three failed attempts on the same gate with materially the same approach, set the gate `BLOCKED`. Do not weaken thresholds or add ignores as a fourth attempt.

### Forbidden repair shortcuts

- adding broad ignore globs;
- deleting tests that expose the problem;
- changing a scanner from error to warning without approved policy change;
- refreshing the baseline after introducing debt;
- creating `v2`, `new`, `legacy`, `temp`, or duplicate service trees instead of migrating canonically;
- mocking the quality tool in CI;
- marking human/security review complete using agent-generated evidence alone.
