# Captured verification transcripts — PR 77

Rounds 5-8. Captures are verbatim on worktrees whose content equals the
product commit staging that round (branch CI + Saul bind outcomes to the
pushed head after each push — in-tree statements never assert results for
their own SHA). Round-by-round scope also lives in `../events.jsonl`.

## Verifier shell (re-run green every round; output shown once)

```
$ python3 scripts/render-sai-feature-maps --check
ALL PASS / OK --selftest harness ALL PASS / OK --check features=11 / exit=0
$ node --check /tmp/emitted_sessions.js          -> exit=0 NODE_CHECK_OK
$ bash scripts/verify-semantic-hierarchy         -> exit=0 OK
$ bash scripts/verify-agent-audit -n 25 HEAD     -> exit=0 OK
$ bash scripts/verify-merge-handoff origin/main..HEAD -> exit=0 OK
$ /usr/local/go/bin/go test ./... && go vet ./... -> exit=0 (all pkgs ok)
$ sai-verify drive (pre-commit, content-identical tree)
pass=63 fail=1 skip=0
FAIL proof-artifacts  (only passes when CI supplies --evidence; same single
pre-existing linked-worktree fixture FAIL reproduced identically on BASE
origin/main 759d017 pass=61 fail=1 skip=0)
```

## DOM smokes (R5; live repeated 4x for 403-flakiness stability)

```
$ for s in synthetic sessions-down malformed-pulls old-pr-session malformed-sessions live; do node /tmp/smoke_pr77.mjs /tmp/evid-site3/pr-sessions.html $s | tail -1; done
--- synthetic/sessions-down/malformed-pulls/malformed-sessions: exit=0 SMOKE-OK
--- malformed-pulls: malformed pull-list => unavailable, session PR still enriched via per-PR
--- old-pr-session: session PR outside listing page gets title+state+merged from per-PR detail
--- live: exit=0 SMOKE-OK (x4 stable; GitHub anon API 403 from VM degrades honestly as github=unavailable)
```

# Round-6 selftest + negative proof (latest-wins rollup)

```
$ python3 scripts/render-sai-feature-maps --selftest    # 12 assertions ALL PASS
Negative proof — same harness against the OLD (no-dedup) rollup:
FAIL P1 latest-wins total by name  got=2 want=1
FAIL Saul latest-wins clears action_required  got=1 want=0
exit=1  (4 selftest failure(s))   # would have caught the P1
```

# Round-7b runtime proof (STEER 09:03:17Z) — exact shipped page JS

Node harness executes the literal <script> block emitted into
pr-sessions.html (stubbed fetch/document/setInterval). 15/15 PASS:
A healthy first load: requests bounded 25 (1 listing + 24 budgeted),
101 union cards, PR 77 detail fetched first, Agent NONE card present.
B quota exhausted after listing: attempts <= listing+budget, all cards
render from listing data, CI/Saul honestly "unavailable" (never invented).
C refresh with ETag 304s: at most 1 request, cached rollups survive.

# Round-8 (real Codex P1x2 @ ee45cec, STEER 2026-08-23T10:22:53Z)

P1-1 session-only PRs never enriched; P1-2 force-pushed PRs pinned to stale
detail. Fix moved pending-selection into planEnrich (detail BY NUMBER before
any HEAD; listing head wins over cached DETAIL).
```
$ ./scripts/render-sai-feature-maps --selftest   # 29 assertions ALL PASS, excerpt
PASS session-only card plans a detail by number    got=true want=true
PASS steady-state replans nothing after 100 cycles got=0 want=0
$ ./scripts/render-sai-feature-maps --check   features=11 OK
$ node --check emitted pr-sessions.html inline JS   NODE_CHECK_OK
```
Line budget then: 1194/1200 added vs base 759d017. Negative proof: pre-fix
harness FAILs the divergent-head fixture.

# Round-13 (real Codex P1+P2x2 exact-HEAD @ 91c933e, check-run 97206101278)

P1: every open dashboard listed GitHub once per minute (the listing poll
alone consumed the anonymous 60/hr allowance); 304 revalidation is not
reliably quota-free. P2s: docs claimed ETag conditional GETs keep anon
limits manageable. Fix: ghDue gates loadPulls + enrich behind
GH_POLL_MS=300000; ghJson honors X-RateLimit-Remaining/Reset backoff below
GH_MIN_REMAIN=5; NOTE renders an honest throttled marker.
```
$ python3 scripts/render-sai-feature-maps --selftest   # 55 assertions ALL PASS
A/B runtime proof (/tmp/r13_negative_proof.cjs on exact emitted <script>
payloads, OLD=91c933e vs NEW; cumulative GitHub calls per 60s tick):
OLD healthy     first-load 3 | +1 listing every tick
NEW healthy     first-load 3 | polls only on 5m boundaries
OLD exhausted   first-load 3 | headers ignored, +1 every tick
NEW exhausted   first-load 3 | backs off until reset (flat)
NEW no-reset    degrades to cadence-only, never eternal lockout
NEGATIVE PROOF ALL PASS — pre-fix reproduces the flagged 60s polling.
```
