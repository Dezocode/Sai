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

See `04_verify/output/captured-transcripts.md`. All captures verbatim at
ancestor `055796c` (the evidence commit is its direct child, changing only
`.ai/runs/`; per repo convention in-tree statements never assert results for
their own SHA — branch CI and the Saul check-binding bind outcomes to the
pushed head after each push):

- renderer `--check` OK features=11 (with new assertions)
- node DOM smoke vs live API: SMOKE-OK, 14/14 checks
- synthetic stale/failed/done/error/empty variants: all honest
- hierarchy / agent-audit / merge-handoff: OK
- go test ./... + go vet: clean
- drive pass=62 fail=1 — single FAIL is the pre-existing linked-worktree
  fixture row (reproduced identically on BASE), queue cleaned after run

## Constraints honored

Draft only — no merge, no ready-mark, no force-push. No gateway restarts.
No secrets committed. Heartbeats via sai-pr-heartbeat.sh per phase.

## Next safe action

Saul exact-head round on pushed HEAD (expect binding to the child of
`055796c`); owner review on the draft PR. After P0=P1=P2=0 and owner
approval, Pages main deploy publishes pr-sessions.html alongside
feature-maps.html at dezocode.github.io/Sai.


## Full-flight update (2026-08-23, owner steer applied)

STEER archived (STEER.applied.2026-08-23T04:08:02Z.md). Product commit
`56a2197` implements P1 (GitHub authority plane via unauthenticated public
REST + ETag conditional GETs, union cards, Agent NONE cards, per-card CI/Saul/
mergeability/HEAD fields, mismatch flags, github.com PR links) and P2
(cursor-runtimes.md registration; heartbeat fresh/stale/missing distinct).
Verification: --check features=11; node --check on emitted JS; DOM smokes
live/synthetic/sessions-down all SMOKE-OK; verifiers OK; go clean; drive
pass=63 fail=1 (single FAIL is the pre-existing linked-worktree fixture row,
also on BASE). Next safe action: exact-head CI + Saul round on the pushed
child head; owner review. Stay draft.


## Saul round-4 fix (2026-08-23)

Check-run 97144393640 @ 42c36c0 returned action_required with two P1s
(CODEX-UNIT-0009-0001 Agent-NONE-during-outage; CODEX-UNIT-0009-0002
invented P0=P1=P2=0 labels) plus a standing P2 (silent empty on malformed
payloads). All three fixed at `fde6b56`: Agent UNKNOWN state,
count parsing from check-run output summaries with latest-run-wins,
malformed-payload degradation. Next safe action: CI + Saul exact-head round
on the pushed child of this commit; owner review after P0=P1=0. Stay draft.

## Round-5 GitHub-plane robustness (2026-08-23, STEER relaunch)

STEER @ 07:05:25Z (worker DEAD, Origin relaunching) archived
(STEER.applied.2026-08-23T07:05:25Z.md) and cleared. Finished the dirty
protected-ci/render work and hardened the GitHub data plane:
- `loadPulls()` now throws on a malformed GitHub pull-list payload; the
  renderer degrades as `github=unavailable (malformed ...)` instead of
  silently rendering an empty universe.
- `enrich()` now fetches per-PR detail for every known-key card, so a
  session-linked PR that falls outside the first GitHub listing page
  (e.g. old/closed) still gets authoritative title/state/draft/merged/head/
  pushed/mergeability from its per-PR endpoint; `refreshDetail` captures
  `state`/`draft`/`mergedAt` and `normalize` honors them.
- protected-ci.md sub-feature updated to claim malformed-payload-on-either-
  plane degradation + per-PR enrichment of out-of-listing session PRs.
Verification (captured-transcripts.md @ product commit): --check features=11;
node --check emitted JS; DOM smokes 6 scenarios all SMOKE-OK (live x4 stable
against intermittent GitHub anon 403); verifiers OK; go test/vet clean; drive
pass=63 fail=1 (proof-artifacts is the pre-existing local-drive-only row,
identical single FAIL on BASE). Line budget 678/1200 added.
Next safe action: push product+evidence commits, watch CI + Saul bind to the
new head; owner review after exact-HEAD green + P0=P1=0. Stay draft.

## Round-6 latest-wins check-run rollup (2026-08-23, STEER @ 08:04:58Z)

STEER (worker DEAD, Origin relaunching) archived
(STEER.applied.2026-08-23T08:04:58Z.md) and cleared. Finished the in-progress
latest-wins rollup and hardened CI/Saul display:
- `refreshChecks` dedupes GitHub check-runs by stable check name keeping the
  newest attempt, so a superseded failed run no longer keeps CI marked failed
  after a green rerun (Saul P1). The rollup is single-source `ROLLUP_JS`,
  spliced into the page and into a new adversarial `--selftest` node harness;
  the harness PASSes all 12 assertions on the fix and FAILs 4 on the pre-fix
  rollup (proven negative), so it would have caught the P1. `--check` now runs
  the selftest first; the Pages workflow gained an explicit setup-node step.
- "last push" now comes only from authoritative `head.repo.pushed_at`; PR
  `updated_at` is labeled separately as "updated". `DETAIL` stays
  enrichment-only so a session-discovered PR never becomes a ghost card after
  its session and the listing both drop it.
- protected-ci.md + docs/pages-pr-sessions/README.md updated to claim the
  selftest guard and the latest-wins rollup.
Verification (captured-transcripts.md @ product commit): --selftest ALL PASS;
--check features=11; node --check emitted JS; OLD-rollup negative check 4 FAIL
(proves adversarial); hierarchy/audit/handoff OK; go test/vet clean; drive
pass=63 fail=1 (proof-artifacts pre-existing local-drive-only row, identical
single FAIL on BASE). Line budget ~703/1200 added.
Next safe action: push product+evidence commits, watch CI + Saul bind to the
new head; owner review after exact-HEAD green + P0=P1=0. Stay draft.

Round-7 (Saul P1 fan-out quota exhaustion, STEER 2026-08-23T08:46:14Z):
enrichment is planned by single-source ENRICH_JS (page + --selftest):
planEnrich caps each refresh at REQUEST_BUDGET=24 sequential requests
(session-linked cards first, check fetches deduped per head SHA) so first
load can't exhaust the anonymous 60/hr GitHub quota; done-cache keyed by head
SHA re-enriches force-pushed PRs at the new HEAD; failed detail fetch is not
cached done. --selftest 22/22; --check features=11; node --check OK; negative
pre-fix harness FAILs force-push; line budget ~1082/1200. Saul runs on
946a0f2 and 232b867 were infra-only neutrals (codex_invoked=false) - NOT the
gate. Round-8 (Saul P1x2 exact-HEAD @ ee45cec, STEER 10:22:53Z): P0=0 P1=2
P2=0. P1-1 session-only PRs never enriched; P1-2 force-pushed PRs pinned to
stale detail. Fixed: pending-selection moved INTO planEnrich - session-only
cards plan detail BY NUMBER before any HEAD, then checks once a HEAD lands;
doneShas() marks done with the same SHA resolution (listing head wins, else
cached DETAIL head) - no eternal re-plan; listing head wins over cached detail
in normalize/refreshChecks/checksFor, so force-pushes re-bind CI/Saul.
--selftest 29/29 (pre-fix harness FAILs divergent-head); --check features=11;
node --check OK; line budget ~1194/1200. Next: watch real-Codex Saul bind to
the new exact HEAD; morning-ready = SUCCESS P0=P1=0, codex_invoked=true,
synthetic=false (neutrals don't count). Stay draft.

Round-9 (STEER 2026-08-23T11:26:02Z): exact-HEAD real-Codex Saul on 48ec687
P1: session-only cards still never load CI/Saul - doneShas() marked a pass-1
detail-only HEAD ENRICHED so pass-2 skipped check-runs forever. Fixed:
doneShas() marks a HEAD done only once its check-runs were fetched for it
(failed checks attempt counts as attempted - no eternal retry); the selftest
blocks now follow shipped enrich() order (plan -> execute -> doneShas),
including an adversarial pass-1-detail/pass-2-checks sequence that FAILs on
the pre-fix marker. --selftest 30/30; --check features=11; node --check
emitted JS; hierarchy/audit/anti-regression OK; line budget 1198/1200. Next:
push, watch CI + real-Codex Saul bind to the new exact HEAD; morning-ready =
exact-HEAD SUCCESS P0=P1=0, codex_invoked=true, synthetic=false. Stay draft.
