# Handoff — PR sessions dashboard (PR 77)

Branch `hermes/pr-sessions-dashboard`, base `759d017` (origin/main).

## What landed

- `scripts/render-sai-feature-maps`: new `pr-sessions.html` emission.
  - Tab "PR sessions" added to feature-maps.html header (and back-link on the
    sessions page).
  - pr-sessions.html: horizontally scrollable PR wheel (`overflow-x:auto`,
    flex cards, one card per PR, sessions sorted by id).
  - Client-side `fetch` GET of
    `https://srv1840454.hstgr.cloud/api/hermes-sessions/sessions`
    (`cache:"no-store"`); each session card renders profile, status, phase,
    head, heartbeat (+age), steer (note pill or "none reported"), monitors.
  - Failure/empty states render "unavailable"/"no sessions" — nothing invented.
  - All API-derived text HTML-escaped; no secrets or tokens in page source;
    noscript fallback present.
- `--check` extended: asserts both pages, tab link, wheel CSS/mount,
  FIELDS array, Hostinger boundary, and rejects session-token strings in
  generated output. Feature-map prose legitimately mentioning GH_TOKEN /
  GITHUB_TOKEN is not banned (workflow env hygiene is the enforcement point).
- `.github/workflows/feature-maps-pages.yml`: build job now also asserts
  `pr-sessions.html` exists in the rendered site.
- `.cursor/skills/verify-sai/features/protected-ci.md`: ci-feature-maps-pages
  sub-feature + proof line + gotcha updated for the sessions surface.

## Verification

See `04_verify/output/verification.md`. Renderer --check OK features=11;
hierarchy OK; agent-audit OK (-n 20); merge-handoff OK; go test/vet clean;
drive 62/63 with one pre-existing environmental FAIL reproduced on BASE
(linked-worktree queue path), not caused by this diff.

## Constraints honored

Draft only — no merge, no ready-mark, no force-push. No gateway restarts.
No secrets committed. Heartbeats via sai-pr-heartbeat.sh per phase.

## Next safe action

Owner review on the draft PR; Saul exact-head round on pushed HEAD; after
P0=P1=P2=0 and owner approval, Pages main deploy publishes pr-sessions.html
alongside feature-maps.html at dezocode.github.io/Sai.
