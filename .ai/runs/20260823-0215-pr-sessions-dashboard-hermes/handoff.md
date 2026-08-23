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
