# Captured verification transcripts — PR 77

Rounds 5-8. Captures are verbatim on worktrees whose content equals the
product commit staging that round (branch CI + Saul bind outcomes to the
pushed head after each push — in-tree statements never assert results for
their own SHA). The identical verifier shell was re-run green each round;
its output is shown once below.

Round scope:
- R5: malformed pull-list payload degrades as unavailable instead of
  silent empty; session-linked PRs outside the first GitHub listing page
  still enrich via their per-PR endpoint.
- R6: latest-wins check-run rollup (Saul P1) lives in single-source
  ROLLUP_JS spliced into the page AND the selftest harness, so the test
  drives the exact shipped function; "last push" comes only from
  authoritative head.repo.pushed_at ("updated" labeled separately);
  DETAIL stays enrichment-only (no ghost cards).
- R7/R7b: enrichment budget REQUEST_BUDGET=24 via single-source
  ENRICH_JS planner shared with the selftest; runtime proof executes the
  exact shipped page JS.
- R8 (real Codex P1x2 @ ee45cec): session-only cards plan a detail BY PR
  NUMBER before any HEAD; listing head wins over cached DETAIL so a
  force-push re-binds CI/Saul; doneShas uses the same SHA resolution.

## Verifier shell (renderer, node syntax, repo verifiers, go, drive)

```
$ python3 scripts/render-sai-feature-maps --check
ALL PASS
exit=0
OK render-sai-feature-maps --selftest: rollupChecks latest-wins harness ALL PASS
OK render-sai-feature-maps --check features=11
$ node --check /tmp/emitted_sessions.js
exit=0
NODE_CHECK_OK
$ bash scripts/verify-semantic-hierarchy
exit=0
verify-semantic-hierarchy: OK
$ bash scripts/verify-agent-audit -n 25 HEAD
exit=0
verify-agent-audit: OK (-n 25 HEAD)
$ bash scripts/verify-merge-handoff origin/main..HEAD
exit=0
verify-merge-handoff: OK (1 task-id(s) checked)
$ /usr/local/go/bin/go test ./...
exit=0
?   github.com/Dezocode/Sai/cmd/sai	[no test files]
ok  	github.com/Dezocode/Sai/cmd/sai-design-check	0.060s
ok  	github.com/Dezocode/Sai/cmd/sai-verify	6.179s
ok  	github.com/Dezocode/Sai/internal/app	(cached)
$ /usr/local/go/bin/go vet ./...
exit=0
$ sai-verify drive (captured pre-commit at content-identical tree)
pass=63 fail=1 skip=0
FAIL proof-artifacts  (only passes when CI supplies --evidence; same single
pre-existing linked-worktree fixture FAIL reproduced identically on BASE
origin/main 759d017 pass=61 fail=1 skip=0)
```

## DOM smokes (R5; live repeated 4x for 403-flakiness stability)

```
$ for s in synthetic sessions-down malformed-pulls old-pr-session malformed-sessions live; do node /tmp/smoke_pr77.mjs /tmp/evid-site3/pr-sessions.html $s | tail -1; done
--- synthetic: exit=0 SMOKE-OK
--- sessions-down: exit=0 SMOKE-OK
--- malformed-pulls: exit=0 SMOKE-OK      (malformed pull-list => unavailable, session PR still enriched via per-PR)
--- old-pr-session: exit=0 SMOKE-OK       (session PR outside listing page gets title+state+merged from per-PR detail)
--- malformed-sessions: exit=0 SMOKE-OK
--- live: exit=0 SMOKE-OK (x4 stable; GitHub anon API 403 from VM degrades honestly as github=unavailable)
```

# Round-6 selftest + negative proof (latest-wins rollup)

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

# Round-7b runtime proof (STEER 09:03:17Z) — exact shipped page JS

Harness: /tmp/verify_runtime_budget.mjs (node; stubbed fetch/document/
setInterval; executes the literal <script> block emitted into
pr-sessions.html at HEAD).

Scenario A (healthy first load, 100 GitHub PRs + 2 sessions):
PASS first-load GitHub requests bounded got=25 (1 listing + 24 budgeted)
PASS exactly 1 listing request
PASS enrichment requests <= 24 budget
PASS union cards rendered = 101 (100 GH PRs + session-only pr=9999 ghost)
PASS session-linked PR 77 detail fetched FIRST (priority order)
PASS CI rollup rendered ("1 checks")
PASS Agent: NONE card present for open PR without session

Scenario B (GitHub quota exhausted right after the listing):
PASS total GitHub attempts <= listing + budget
PASS all 101 cards still render from listing-level data
PASS CI/Saul fields honestly ">unavailable<" — never invented totals

Scenario C (refresh with ETag revalidation, everything 304 Not Modified):
PASS refresh issues at most 1 GitHub request (listing only; 304 does not
count against the anonymous 60/hr quota)
PASS all cards survive the refresh
PASS cached check-rollup data survives and still renders

Result: RUNTIME PROOF ALL PASS (15/15). The budgeted planner bounds
first-load GitHub calls to 25 requests worst-case, degrades honestly when
the quota is hit mid-load, and steady-state refreshes stay at ~1 request.

# Round-8 (real Codex P1x2 exact-HEAD @ ee45cec, STEER 2026-08-23T10:22:53Z)

P1-1: session-only PRs never enriched (assemble leaves pr=null; old
pendingCards dropped cards without headSha, so refreshDetail never ran).
P1-2: force-pushed PRs stayed pinned to stale detail (normalize preferred
cached DETAIL headSha over the refreshed listing head, so ENRICHED never
invalidated).

```
$ ./scripts/render-sai-feature-maps --selftest   (29 assertions, excerpt)
PASS session-only card plans a detail by number    got=true want=true
PASS done HEAD stops replanning                    got=0 want=0
PASS divergent listing HEAD replans detail         got=true want=true
PASS steady-state replans nothing after 100 cycles got=0 want=0
ALL PASS
$ ./scripts/render-sai-feature-maps --check   (runs selftest)  features=11 OK
$ node --check emitted pr-sessions.html inline JS   NODE_CHECK_OK, 0 banned tokens
```

Line budget projected: 1194/1200 added lines vs base 759d017. Negative-proof:
the pre-fix harness FAILs the divergent-head fixture (old pendingCards only
planned cards that already had a headSha, so a session-only or force-pushed
card could never re-plan).

# Round-13 (real Codex P1+P2x2 exact-HEAD @ 91c933e, check-run 97206101278)

P1: every open dashboard listed GitHub once per minute (setInterval(load,
60000) -> loadPulls), so the listing poll alone consumed the anonymous
60/hr allowance; unauthenticated 304 revalidation is not reliably quota-
free. P2s: protected-ci.md + docs README claimed ETag conditional GETs
keep anon limits manageable.

Fix: ghDue(now,lastPoll,remain,resetAt,pollMs,minRem) gates loadPulls +
enrich behind GH_POLL_MS=300000 (first load always fetches); ghJson
captures X-RateLimit-Remaining/X-RateLimit-Reset per response and the
plane backs off until reset once remaining is 0 or below GH_MIN_REMAIN=5.
NOTE renders "sessions 60s · github 5m" plus an honest throttled marker.

```
$ python3 scripts/render-sai-feature-maps --selftest   (55 assertions; new fixtures excerpt)
PASS ghDue first load polls                got=true want=true
PASS ghDue holds inside window             got=false want=false
PASS ghDue blocks when exhausted until reset got=false want=false
PASS ghDue resumes after reset             got=true want=true
ALL PASS
$ ./scripts/render-sai-feature-maps --check   features=11 OK
$ node --check emitted pr-sessions.html inline JS   exit=0 NODE_CHECK_OK

A/B runtime proof (node harness /tmp/r13_negative_proof.cjs; stubbed fetch/
document/clock driving the exact emitted <script> payload of OLD=91c933e vs
NEW=round-13; cumulative GitHub calls after each 60s tick):
OLD healthy     first-load 3 | 4,5,6,7,8,9,10,11,12,13   (+1 listing every tick)
NEW healthy     first-load 3 | 3,3,3,3,4,4,4,4,4,5       (poll only on 5m boundaries)
OLD exhausted   first-load 3 | 4,5,6,7,8,9,10,11,12,13   (headers ignored)
NEW exhausted   first-load 3 | 3,3,3,3,3,3,3,3,3,3       (backs off until reset)
NEW no-reset    first-load 3 | 3,3,3,3,4,4,4,4,4,5       (degrades to cadence-only,
                                                          never eternal lockout)
NEGATIVE PROOF ALL PASS — pre-fix code reproduces the flagged 60s polling;
post-fix holds quota headroom.
```
