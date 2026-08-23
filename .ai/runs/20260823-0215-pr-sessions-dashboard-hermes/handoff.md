# Handoff — PR sessions dashboard (PR 77)

Branch `hermes/pr-sessions-dashboard`, base `759d017` (origin/main).
Task-ID `20260823-0215-pr-sessions-dashboard-hermes`.

## What landed

- `scripts/render-sai-feature-maps`: emits `pr-sessions.html` plus the
  feature-maps site (tab + back-link; scrollable PR wheel; summary/graph
  row; stale-heartbeat styling). Client-side read-only GET of the public
  Hostinger sessions API (`cache:"no-store"`, 60s refresh), cards show
  profile/status/phase/head/heartbeat(+age)/steer/monitors; failure and
  empty states render unavailable — nothing invented; all API text
  HTML-escaped; noscript fallback; no tokens anywhere.
- GitHub authority plane: unauthenticated public REST + ETag conditional
  GETs, polled at most once per GH_POLL_MS=300000 with
  X-RateLimit-Remaining/Reset backoff (ghDue, round 13).
- `--check` asserts both pages, tab link, wheel CSS/mount, summary mount,
  refresh interval, FIELDS array, `.hb-stale` hook, Hostinger boundary,
  and rejects session-token strings in generated output.
- `.github/workflows/feature-maps-pages.yml`: build job runs `--check` and
  asserts `pr-sessions.html` exists in the rendered site.
- `.cursor/skills/verify-sai/features/protected-ci.md`: ci-feature-maps-pages
  sub-feature, proof line, and gotcha updated for the full sessions surface.

## Verification

All captures verbatim in `04_verify/output/captured-transcripts.md` at an
ancestor of the evidence commit (in-tree statements never assert results
for their own SHA — branch CI and the Saul check-binding bind outcomes to
the pushed head after each push):

- renderer `--check` features=11; `--selftest` drives the exact shipped
  ROLLUP_JS/ENRICH_JS harness (see Rounds); node DOM smoke: SMOKE-OK
- hierarchy / agent-audit / merge-handoff / anti-regression: OK
- go test ./... + go vet: clean; drive pass=63 fail=1 (pre-existing
  linked-worktree fixture row, reproduced identically on BASE)

## Constraints honored

Draft only — no merge, no ready-mark, no force-push. No gateway restarts.
No secrets committed. Heartbeats via sai-pr-heartbeat.sh per phase.

## Rounds

- R1-5 (56a2197..fde6b56): GitHub authority plane, union cards, Agent
  NONE/UNKNOWN + mismatch flags, cursor-runtimes registration, heartbeat
  fresh/stale/missing distinct (missing never an asserted duration),
  Saul counts from the run's own published summary (latest-run-wins) or
  bare conclusion, malformed payloads degrade as unavailable, off-listing
  session PRs enriched per-PR by number.
- R6-7: latest-wins check-run rollup via single-source ROLLUP_JS +
  adversarial `--selftest` (green rerun clears superseded failure);
  pushed_at from authoritative head-repo push; enrichment budget
  REQUEST_BUDGET=24 via ENRICH_JS planner; done-cache keyed by head SHA.
- R8-9 (ee45cec, e41f4e3): session-only detail planned BY NUMBER before
  any HEAD; listing head wins over cached DETAIL (force-push re-binds);
  doneShas marks done only after check-runs were fetched for that HEAD;
  selftest follows shipped plan->execute->doneShas order.
- R10 (b7a9d38): rollupChecks orders by stable numeric id / attempt,
  timestamps only as fallback — a queued rerun supersedes an older
  completed FAILURE.
- R11-12 (bc21a7d, 91c933e): session-only cards revalidate detail on TTL
  REVALIDATE_MS; failed DETAIL fetches back off at MAX_DETAIL_FAILS and
  probe again after DETAIL_RETRY_MS (backoff, not lockout); doneShas
  resolves a listing-backed head when DETAIL is null; "head repo push"
  relabel; checks re-bind on HEAD change.
- R13 (this commit): GitHub plane cadence + rate-limit honor — ghDue
  gates loadPulls/enrich behind GH_POLL_MS=300000 (at most one GitHub
  poll per 5 min, well under the anonymous 60/hr; first load always
  fetches) and captures X-RateLimit-Remaining/X-RateLimit-Reset per
  response, backing off until reset once remaining is 0 or below
  GH_MIN_REMAIN=5; NOTE renders "sessions 60s · github 5m" plus an
  honest throttled marker; protected-ci.md and docs README corrected
  (ETag revalidation only saves re-transfer, never the quota dodge).
  Fixtures: first-load poll, window hold/resume, exhausted/floor block
  until reset, resume after reset.

## Next safe action

Watch exact-HEAD real-Codex Saul bind to the pushed head (codex_invoked=
true, synthetic=false); morning-ready = SUCCESS P0=P1=0; close any real
Codex P1s. Owner review on the draft PR. Stay draft.
