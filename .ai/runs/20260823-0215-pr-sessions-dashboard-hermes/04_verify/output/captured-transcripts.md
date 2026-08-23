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
