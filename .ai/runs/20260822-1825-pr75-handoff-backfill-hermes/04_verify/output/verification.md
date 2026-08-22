# 04_verify — handoff backfill verification

Commands and results on this exact working tree (base 2a8f89f + a882bd0 +
backfill commit):

- `scripts/verify-agent-audit -n 20 HEAD` — result recorded in
  `06_publish_sync/output/push-evidence.md` (must be OK).
- `scripts/verify-merge-handoff origin/main..HEAD` — must report OK for both
  task ids (1303 backfilled, 1825 has its own handoff).
- `scripts/verify-semantic-hierarchy` — must pass (registry untouched).
- `python3 -m json.tool` on every added JSON file — must parse.
- Every line in both `events.jsonl` files — must be valid JSON.

No numbers are claimed here without the command output captured at execution
time; see the publish/sync stage output for the actual transcripts.
