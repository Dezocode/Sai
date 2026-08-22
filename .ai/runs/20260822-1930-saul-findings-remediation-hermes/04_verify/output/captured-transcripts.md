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

## Capture 2 — on parent commit `472d597a9a952999b2b40febbf5fe0b623803b9f`

Executed after the full suite passed there (transcript below) and before
the evidence-only commit that carries this file. This is the closest
in-repo capture to the reviewed head; verification of the evidence-only
commit itself is carried by GitHub branch CI, which binds check results to
each exact pushed SHA.

```
$ git rev-parse HEAD
472d597a9a952999b2b40febbf5fe0b623803b9f

$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
[exit=0]

$ scripts/verify-agent-audit -n 20 HEAD
verify-agent-audit: OK (-n 20 HEAD)
[exit=0]

$ scripts/verify-merge-handoff origin/main..HEAD
verify-merge-handoff: OK (3 task-id(s) checked)
[exit=0]

$ python3 -m json.tool (all metadata.json)
OK .ai/runs/20260822-1303-sai-plugin-lane-bootstrap/metadata.json
OK .ai/runs/20260822-1825-pr75-handoff-backfill-hermes/metadata.json
OK .ai/runs/20260822-1930-saul-findings-remediation-hermes/metadata.json

$ events.jsonl line-parse (three 0822 runs)
OK 20260822-1303-sai-plugin-lane-bootstrap 2 events
OK 20260822-1825-pr75-handoff-backfill-hermes 8 events
OK 20260822-1930-saul-findings-remediation-hermes 3 events
```

## Evidence-chain statement (no self-reference)

A git commit cannot contain a transcript of checks executed against its own
SHA. Therefore this run's terminal evidence is: (a) Capture 1 (fail-before,
gate working as designed), (b) Capture 2 above on direct parent `472d597`
(all gates pass), and (c) GitHub branch CI + PR 75 evidence comments, which
bind check outcomes to each exact pushed SHA after push. No event or file in
this repository claims a verification result for a SHA it cannot know.

