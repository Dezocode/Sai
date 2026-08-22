# 04_verify — captured transcripts (exact-head evidence)

All commands executed on this tree at 2026-08-22 ~19:50 UTC. Two captures,
both embedded verbatim, no prospective statements.

## Capture 1 — remediation commit `3be4ccc` (before evidence files staged)

```
== exact-head evidence capture ==
$ git rev-parse HEAD
3be4ccc3295197da598e7944793903cd83ffdbf0
[captured before staging the evidence/handoff files themselves]

$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
[exit=0]

$ scripts/verify-agent-audit -n 20 HEAD
verify-agent-audit: OK (-n 20 HEAD)
[exit=0]

$ scripts/verify-merge-handoff origin/main..HEAD
FAIL 3be4ccc: task-id 20260822-1930-saul-findings-remediation-hermes has no handoff.md or HANDOFF event
verify-merge-handoff: FAILED (1 problem(s))
[exit=1]

$ python3 -m json.tool (all new metadata.json)
OK .ai/runs/20260822-1303-sai-plugin-lane-bootstrap/metadata.json
OK .ai/runs/20260822-1825-pr75-handoff-backfill-hermes/metadata.json
OK .ai/runs/20260822-1930-saul-findings-remediation-hermes/metadata.json

$ events.jsonl line-parse (all three runs)
OK 20260822-1303-sai-plugin-lane-bootstrap 2 events
OK 20260822-1825-pr75-handoff-backfill-hermes 8 events
OK 20260822-1930-saul-findings-remediation-hermes 1 events
```

Interpretation: the merge-handoff failure here is the gate working as
designed — this run's own handoff.md is intentionally written only after real
verification, and the final commit includes it.

## Capture 2 — after staging evidence + handoff, before the final commit

```
$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
[exit=0]

$ git status --porcelain | grep 20260822-1930
?? .ai/runs/20260822-1930-saul-findings-remediation-hermes/04_verify/
```

(verify-merge-handoff is not re-runnable pre-commit since it audits the
committed range only; the post-commit rerun is recorded in this run's
events.jsonl event :5 with its captured output.)
