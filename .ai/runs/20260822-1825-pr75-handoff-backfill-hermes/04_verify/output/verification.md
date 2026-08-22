# 04_verify — handoff backfill verification

Captured command outputs. The original run of this file (head `88b29d1`) held
prospective statements instead of captured results; that finding
(CODEX-UNIT-0004-0001, P2) is remediated in task
`20260822-1930-saul-findings-remediation-hermes`. Two evidence captures exist:

1. Pre-fix capture on head `88b29d18fcd02bdda6242fc7df6b5a6287702b47`
   (2026-08-22 ~19:35 UTC), before the remediation edits were staged:

```
$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
[exit=0]

$ scripts/verify-agent-audit -n 20 HEAD
verify-agent-audit: OK (-n 20 HEAD)
[exit=0]

$ scripts/verify-merge-handoff origin/main..HEAD
verify-merge-handoff: OK (2 task-id(s) checked)
[exit=0]

$ python3 -m json.tool (both metadata.json)
OK 20260822-1303 metadata
OK 20260822-1825 metadata

$ events.jsonl line-parse
OK 20260822-1303-sai-plugin-lane-bootstrap 2 events
OK 20260822-1825-pr75-handoff-backfill-hermes 4 events
```

2. Post-remediation capture on commit `472d597a9a952999b2b40febbf5fe0b623803b9f`
   (the direct parent of the commit carrying this file): recorded verbatim in
   `.ai/runs/20260822-1930-saul-findings-remediation-hermes/04_verify/output/captured-transcripts.md`,
   Capture 2. Verification of any later evidence-only commits is carried by
   branch CI on GitHub, which binds check results to each exact pushed SHA,
   and by the PR 75 evidence comments; a git commit cannot contain a
   transcript of checks run against its own SHA, so ancestor captures plus
   SHA-bound CI are the terminal evidence chain.

Historical note (kept for audit truth): on the first local commit
(`eccedae`, never pushed) `scripts/verify-merge-handoff origin/main..HEAD`
failed with `task-id 20260822-1825-pr75-handoff-backfill-hermes has no
handoff.md or HANDOFF event` until this run's own `handoff.md` was added.
That failure and rerun are now recorded honestly as VERIFY fail/pass events
in this run's `events.jsonl`.
