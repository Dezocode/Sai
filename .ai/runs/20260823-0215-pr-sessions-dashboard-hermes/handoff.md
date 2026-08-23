# Handoff — PR sessions dashboard (PR 77)

Branch `hermes/pr-sessions-dashboard`, base `759d017` (origin/main).
Task-ID `20260823-0215-pr-sessions-dashboard-hermes`.

## What landed

- `scripts/render-sai-feature-maps`: emits `pr-sessions.html` plus the
  feature-maps site.
  - Header tab "PR sessions" on feature-maps.html; back-link on sessions page.
  - Horizontally scrollable PR wheel (`overflow-x:auto`, flex cards): one
    `<article class="pcard">` per PR, session rows grouped under their PR
    (never a flat list), sorted by session id.
  - Summary/graph row above the wheel (`#summary`, `PR GRAPH` label):
    counts by PR, session, status, heartbeat freshness (fresh <30m vs
    stale). Rendered from the live response only; empty when unavailable.
  - Stale-heartbeat styling: red `hb-stale` marker row per stale session,
    red card outline + sub badge when any session under a PR is stale
    (heartbeat missing or ≥30 minutes old).
  - Client-side read-only GET of
    `https://srv1840454.hstgr.cloud/api/hermes-sessions/sessions`
    (`cache:"no-store"`), refreshed every 60s via `setInterval(load,60000)`.
  - Cards show profile, status (color-coded active/finished/done/failed),
    phase, head, heartbeat (+relative age), steer (note pill or "none
    reported"), monitors. Failure/empty states render "unavailable"/"no
    sessions" — nothing invented. All API text HTML-escaped; noscript
    fallback; no tokens anywhere.
- `--check` asserts both pages, tab link, wheel CSS/mount, summary mount,
  refresh interval, FIELDS array, `.hb-stale` hook, Hostinger boundary,
  and rejects session-token strings in generated output.
- `.github/workflows/feature-maps-pages.yml`: build job runs `--check` and
  asserts `pr-sessions.html` exists in the rendered site.
- `.cursor/skills/verify-sai/features/protected-ci.md`: ci-feature-maps-pages
  sub-feature, proof line, and gotcha updated for the full sessions surface.

## Verification

See `04_verify/output/captured-transcripts.md`. All captures verbatim at an
ancestor of the evidence commit (per repo convention in-tree statements never
assert results for their own SHA — branch CI and the Saul check-binding bind
outcomes to the pushed head after each push):

- renderer `--check` features=11 (with new assertions)
- `--selftest` drives the exact shipped ROLLUP_JS/ENRICH_JS (see Rounds)
- node DOM smoke vs live API: SMOKE-OK
- hierarchy / agent-audit / merge-handoff / anti-regression: OK
- go test ./... + go vet: clean
- drive pass=63 fail=1 — single FAIL is the pre-existing linked-worktree
  fixture row (reproduced identically on BASE)

## Constraints honored

Draft only — no merge, no ready-mark, no force-push. No gateway restarts.
No secrets committed. Heartbeats via sai-pr-heartbeat.sh per phase.

## Rounds

- R1-2 (56a2197/8e1afff): GitHub authority plane (unauthenticated public
  REST + ETag conditional GETs), union cards, Agent NONE/UNKNOWN cards,
  per-card CI/Saul/mergeability/HEAD fields, mismatch flags, github.com PR
  links; cursor-runtimes.md registration; heartbeat fresh/stale/missing
  distinct; outage degrades to Agent UNKNOWN.
- R3 (6844fc5): missing heartbeat_at renders "stale - heartbeat missing",
  never an asserted elapsed duration.
- R4 (fde6b56): Saul counts parsed from check-run output summary
  (latest-run-wins), bare conclusion otherwise; malformed-payload
  degradation.
- R5: malformed pull-list plane degrades as unavailable; session PRs
  outside the first listing page enriched per-PR by number.
- R6: latest-wins check-run rollup (superseded failure cleared by green
  rerun) as single-source ROLLUP_JS + adversarial `--selftest`; pushed_at
  from authoritative `head.repo.pushed_at`.
- R7: enrichment budget REQUEST_BUDGET=24 via single-source ENRICH_JS
  planner (fan-out cannot exhaust anon quota); done-cache keyed by head
  SHA re-enriches force-pushes.
- R8 (ee45cec P1x2): session-only PRs plan detail BY NUMBER before any
  HEAD, then checks once a HEAD lands; listing head wins over cached
  DETAIL (force-push re-binds CI/Saul); doneShas uses same SHA resolution.
- R9 (e41f4e3 P1): doneShas() marks a HEAD done only after check-runs
  were fetched for it (failed attempt counts as attempted - no eternal
  retry); selftest follows shipped plan->execute->doneShas order.
- R10 (round-10 P1, this commit): rollupChecks orders by stable numeric
  check-run id / attempt, timestamps only as fallback — a queued rerun
  with no timestamps supersedes an older completed FAILURE (CI reads
  pending, not stuck failed); adversarial queued-rerun fixtures added;
  `--selftest` 36/36 ALL PASS.

## Next safe action

Watch exact-HEAD real-Codex Saul bind to the pushed head (codex_invoked=
true, synthetic=false); morning-ready = SUCCESS P0=P1=0; close any real
Codex P1s. Owner review on the draft PR. Stay draft.
