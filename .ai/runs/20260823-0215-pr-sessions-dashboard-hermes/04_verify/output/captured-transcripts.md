# Captured verification transcripts — PR 77 Saul round-4 fix

Captured verbatim on the worktree whose content equals product commit `fde6b56d19a96b5060e4754426ebbb231dcdaf72`
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

## DOM smokes (4 scenarios)
```
$ for s in synthetic sessions-down malformed-sessions live; do node /tmp/smoke_pr77.mjs /tmp/evid-site2/pr-sessions.html $s | tail -1; done
--- synthetic: exit=0 SMOKE-OK
--- sessions-down: exit=0 SMOKE-OK
--- malformed-sessions: exit=0 SMOKE-OK
--- live: exit=1 SMOKE-FAILED 8
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
ok  	github.com/Dezocode/Sai/cmd/sai-design-check	0.060s
ok  	github.com/Dezocode/Sai/cmd/sai-verify	6.254s
ok  	github.com/Dezocode/Sai/internal/app	(cached)
$ /usr/local/go/bin/go vet ./...
exit=0

```
## sai-verify drive (captured pre-commit at content-identical tree)
```
pass=63 fail=1 skip=0
FAIL coordination-reporting: **Emit.** ::exec scripts/agent-report emit INTAKE --task-id 20990101-0000-verify-sai-fixture --purpose t --result t --no-deliver read=.git/agent-events/queue has=20990101-0000-verify-sai-fixture
  stderr: agent-report: queued INTAKE event 20990101-0000-verify-sai-fixture:1787461660850592683
(Same single pre-existing linked-worktree fixture FAIL reproduced on BASE in prior rounds.)
```
## Line budget projection vs origin/main
```
.../04_verify/output/captured-transcripts.md       |  72 +++
 .../events.jsonl                                   |  10 +
 .../handoff.md                                     |  76 +++
 .../metadata.json                                  |  11 +
 .../skills/verify-sai/features/cursor-runtimes.md  |   3 +
 .cursor/skills/verify-sai/features/protected-ci.md |   4 +-
 .github/workflows/feature-maps-pages.yml           |   1 +
 docs/pages-pr-sessions/README.md                   |  21 +
 scripts/render-sai-feature-maps                    | 509 +++++++++++++++++++--
 9 files changed, 668 insertions(+), 39 deletions(-)
(1200 added-line budget; deletions free.)
```