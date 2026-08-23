# Captured verification transcripts — PR 77 round-5: GitHub-plane robustness

Captured verbatim on the worktree whose content equals the product commit that
stages the round-5 fix (protected-ci doc + renderer GitHub-plane hardening;
staged by the child evidence commit; branch CI + Saul bind the pushed head).

Round-5 scope: GitHub pull-list plane now fails honest — a malformed pull-list
payload degrades as unavailable instead of silent empty; session-linked PRs
outside the first GitHub listing page are still enriched via their per-PR
endpoint (title, state, draft, merged, head, pushed/updated, mergeability).

## Renderer check
```
$ python3 scripts/render-sai-feature-maps --check
exit=0
OK render-sai-feature-maps --check features=11
```
## Emitted inline JS syntax (node --check)
```
$ node --check /tmp/emitted_sessions.js
exit=0
NODE_CHECK_OK```
## DOM smokes (6 scenarios; live repeated 4x for 403-flakiness stability)
```
$ for s in synthetic sessions-down malformed-pulls old-pr-session malformed-sessions live; do node /tmp/smoke_pr77.mjs /tmp/evid-site3/pr-sessions.html $s | tail -1; done
--- synthetic: exit=0 SMOKE-OK
--- sessions-down: exit=0 SMOKE-OK
--- malformed-pulls: exit=0 SMOKE-OK      (malformed pull-list => unavailable, session PR still enriched via per-PR)
--- old-pr-session: exit=0 SMOKE-OK       (session PR outside listing page gets title+state+merged from per-PR detail)
--- malformed-sessions: exit=0 SMOKE-OK
--- live: exit=0 SMOKE-OK (x4 stable; GitHub anon API 403 from VM degrades honestly as github=unavailable)
```
## Repo verifiers
```
$ bash scripts/verify-semantic-hierarchy
exit=0
verify-semantic-hierarchy: OK
$ bash scripts/verify-agent-audit -n 20 HEAD
exit=0
verify-agent-audit: OK (-n 20 HEAD)
$ bash scripts/verify-merge-handoff origin/main..HEAD
exit=0
verify-merge-handoff: OK (1 task-id(s) checked)
```
## Go core
```
$ /usr/local/go/bin/go test ./...
exit=0
?  	github.com/Dezocode/Sai/cmd/sai	[no test files]
ok  	github.com/Dezocode/Sai/cmd/sai-design-check	0.060s
ok  	github.com/Dezocode/Sai/cmd/sai-verify	6.179s
ok  	github.com/Dezocode/Sai/internal/app	(cached)
$ /usr/local/go/bin/go vet ./...
exit=0

```
## sai-verify drive (captured pre-commit at content-identical tree)
```
pass=63 fail=1 skip=0
FAIL proof-artifacts  (only passes when CI supplies --evidence; same single
pre-existing linked-worktree fixture FAIL reproduced identically on BASE
origin/main 759d017 pass=61 fail=1 skip=0)
```
## Line budget projection vs origin/main
```
.cursor/skills/verify-sai/features/protected-ci.md   |   2 +-
scripts/render-sai-feature-maps                      | 512 ++++++++++++++++--
9 files changed, 678 insertions(+), 39 deletions(-)
(1200 added-line budget; deletions free.)
```

# Round-6 evidence — latest-wins check-run rollup (Saul P1 remediation)

Captured verbatim on the worktree whose content equals the product commit
staging the round-6 fix (branch CI + Saul bind the pushed head).

Round-6 scope: refreshChecks dedupes GitHub check-runs by stable check name
keeping the newest attempt, so a superseded failed run no longer keeps CI
marked failed after a green rerun. The rollup lives in single-source
ROLLUP_JS (spliced into the page AND into the --selftest node harness, so the
test drives the exact shipped function). PR "last push" now comes only from
authoritative head.repo.pushed_at; PR updated_at is labeled separately as
"updated"; DETAIL stays enrichment-only (no ghost cards).

## Rollup selftest (adversarial; fails on the pre-fix rollup)
```
$ python3 scripts/render-sai-feature-maps --selftest
PASS P1 latest-wins total by name  got=1 want=1
PASS P1 green rerun clears superseded failure  got=0 want=0
PASS P1 pending count  got=0 want=0
PASS latest-wins timestamp not array order  got=1 want=1
PASS latest-wins total still 1  got=1 want=1
PASS distinct failures total  got=2 want=2
PASS distinct failures fails  got=2 want=2
PASS pending run total  got=1 want=1
PASS pending run pending  got=1 want=1
PASS pending run fails  got=0 want=0
PASS Saul latest-wins conclusion  got=success want=success
PASS Saul latest-wins clears action_required  got=0 want=0
ALL PASS
exit=0
OK render-sai-feature-maps --selftest: rollupChecks latest-wins harness ALL PASS
```
Negative proof — same harness against the OLD (no-dedup) rollup:
```
$ node /tmp/old_rollup.js   # old rollupChecks + SELFTEST_JS
FAIL P1 latest-wins total by name  got=2 want=1
FAIL P1 green rerun clears superseded failure  got=1 want=0
FAIL latest-wins total still 1  got=2 want=1
FAIL Saul latest-wins clears action_required  got=1 want=0
exit=1  (4 selftest failure(s))   # would have caught the P1
```

## Renderer check (now runs the selftest first)
```
$ python3 scripts/render-sai-feature-maps --check
ALL PASS
exit=0
OK render-sai-feature-maps --selftest: rollupChecks latest-wins harness ALL PASS
OK render-sai-feature-maps --check features=11
```
## Emitted inline JS syntax (node --check)
```
$ node --check /tmp/emitted_sessions.js
exit=0
NODE_CHECK_OK
```
## Repo verifiers
```
$ scripts/verify-semantic-hierarchy
exit=0
verify-semantic-hierarchy: OK
$ scripts/verify-agent-audit -n 25 HEAD
exit=0
verify-agent-audit: OK (-n 25 HEAD)
$ scripts/verify-merge-handoff origin/main..HEAD
exit=0
verify-merge-handoff: OK (1 task-id(s) checked)
```
## Go core
```
$ go test ./...
ok  github.com/Dezocode/Sai/cmd/sai-verify  5.969s
$ go vet ./...
exit=0
```
## sai-verify drive (captured pre-commit at content-identical tree)
```
pass=63 fail=1 skip=0
FAIL proof-artifacts  (only passes when CI supplies --evidence; same single
pre-existing linked-worktree fixture FAIL reproduced identically on BASE
origin/main 759d017 pass=61 fail=1 skip=0)
```
## Line budget projection vs origin/main
```
.cursor/skills/verify-sai/features/protected-ci.md   |   2 +-
.github/workflows/feature-maps-pages.yml             |   3 +
docs/pages-pr-sessions/README.md                     |  15 +-
scripts/render-sai-feature-maps                      | 158 ++++++--
4 files changed, 155 insertions(+), 23 deletions(-)
(1200 added-line budget; deletions free.)
```
