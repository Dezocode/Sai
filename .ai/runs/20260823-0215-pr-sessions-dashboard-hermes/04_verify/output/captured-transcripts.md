# Captured verification transcripts — PR 77 full-flight round

Captured verbatim on the worktree whose content equals product commit `56a21978ea1f405d5b288d5e9b2422e525c83979`
(staged by the child evidence commit; branch CI + Saul bind the pushed head).

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

## DOM smokes (live API + synthetic + sessions-down)
```
$ for s in live synthetic sessions-down; do node /tmp/smoke_pr77.mjs /tmp/evid-site/pr-sessions.html $s | tail -1; done
--- live: exit=0 SMOKE-OK
    live note: count=2 · updated_at=2026-08-23T04:47:47Z · github=unavailable (HTTP 403 for /pulls?state=all&per_page=100&sort=created&direction=desc) · live GET · refreshes every 60s · no secrets, nothing invented
--- synthetic: exit=0 SMOKE-OK
    live note: (n/a)
--- sessions-down: exit=0 SMOKE-OK
    live note: (n/a)
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
?   	github.com/Dezocode/Sai/cmd/sai	[no test files]
ok  	github.com/Dezocode/Sai/cmd/sai-design-check	0.109s
ok  	github.com/Dezocode/Sai/cmd/sai-verify	5.842s
ok  	github.com/Dezocode/Sai/internal/app	(cached)
$ /usr/local/go/bin/go vet ./...
exit=0

```
## sai-verify drive (captured pre-commit at content-identical tree)
```
pass=63 fail=1 skip=0
FAIL coordination-reporting: **Emit.** ::exec scripts/agent-report emit INTAKE --task-id 20990101-0000-verify-sai-fixture --purpose t --result t --no-deliver read=.git/agent-events/queue has=20990101-0000-verify-sai-fixture
  stderr: agent-report: queued INTAKE event 20990101-0000-verify-sai-fixture:1787460434678672842
(Same single pre-existing linked-worktree fixture FAIL reproduced on BASE in prior rounds.)
```
## Line budget projection vs origin/main
```
.../04_verify/output/captured-transcripts.md       | 137 ++++++
 .../events.jsonl                                   |   9 +
 .../handoff.md                                     |  62 +++
 .../metadata.json                                  |  11 +
 .../skills/verify-sai/features/cursor-runtimes.md  |   3 +
 .cursor/skills/verify-sai/features/protected-ci.md |   4 +-
 .github/workflows/feature-maps-pages.yml           |   1 +
 docs/pages-pr-sessions/README.md                   |  21 +
 scripts/render-sai-feature-maps                    | 474 +++++++++++++++++++--
 9 files changed, 683 insertions(+), 39 deletions(-)
(1200 added-line budget; deletions free.)
```