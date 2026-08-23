# Handoff — PR sessions dashboard (PR 77)

Branch `hermes/pr-sessions-dashboard`, base `759d017` (origin/main).
Task-ID `20260823-0215-pr-sessions-dashboard-hermes`.

## What landed

- `scripts/render-sai-feature-maps`: emits `pr-sessions.html` plus the
  feature-maps site (tab + back-link; scrollable PR wheel; summary/graph
  row; stale-heartbeat styling). Client-side read-only GET of the public
  Hostinger sessions API (`cache:"no-store"`, 60s refresh), cards show
  profile/status/phase/head/heartbeat(+age)/steer/monitors/usage/diff;
  failure and empty states render unavailable — nothing invented; all API
  text HTML-escaped; noscript fallback; no tokens anywhere.
- GitHub authority plane: unauthenticated public REST + ETag conditional
  GETs, polled at most once per GH_POLL_MS=300000 with
  X-RateLimit-Remaining/Reset backoff and a locally anchored
  GH_WINDOW_BUDGET=60 per-window request budget (ghDue/ghStepDue/
  ghWindowRoll in single-source GH_PLANE_JS spliced into the page AND the
  selftest harness; rounds 13-16).
- `--check` asserts both pages, tab link, wheel CSS/mount, summary mount,
  refresh interval, FIELDS array, `.hb-stale` hook, Hostinger boundary,
  usage/diff needles, and rejects session-token strings in output.
- `.github/workflows/feature-maps-pages.yml`: build job runs `--check` and
  asserts `pr-sessions.html` exists in the rendered site.
- `.cursor/skills/verify-sai/features/protected-ci.md` +
  `docs/pages-pr-sessions/README.md`: ci-feature-maps-pages sub-feature,
  proof line, gotchas updated for the full sessions surface incl. the
  expired-reset consumption rule.

## Verification

All captures verbatim in `04_verify/output/captured-transcripts.md` at an
ancestor of the evidence commit (branch CI and the Saul check-binding bind
outcomes to the pushed head after each push, never the tree's own SHA):
renderer `--check` features=11 (runs the adversarial `--selftest` driving
the exact shipped ROLLUP_JS/ENRICH_JS/GH_PLANE_JS harness); node --check on
emitted inline JS; hierarchy / agent-audit / merge-handoff OK; go test+vet
clean; drive pass=63 fail=1 (pre-existing linked-worktree fixture row,
reproduced identically on BASE).

## Constraints honored

Draft only — no merge, no ready-mark, no force-push. No gateway restarts.
No secrets committed. Heartbeats via sai-pr-heartbeat.sh per phase.

## Rounds

- R1-5: GitHub authority plane, union cards, Agent NONE/UNKNOWN +
  mismatch, cursor-runtimes registration, heartbeat fresh/stale/missing
  (missing never an asserted duration), Saul counts from published summary
  or conclusion, malformed payloads degrade as unavailable, off-listing
  PRs enriched per-PR.
- R6-7: latest-wins check-run rollup via ROLLUP_JS + adversarial
  `--selftest`; REQUEST_BUDGET=24 ENRICH_JS planner; done-cache keyed by
  head SHA.
- R8-9: session-only detail planned BY NUMBER before any HEAD; listing
  head wins over cached DETAIL (force-push re-binds); doneShas marks done
  only after check-runs were fetched for that HEAD.
- R10-12: rollupChecks orders by stable id/attempt; session-only cards
  revalidate detail on TTL REVALIDATE_MS; failed DETAIL fetches back off at
  MAX_DETAIL_FAILS and probe again after DETAIL_RETRY_MS.
- R13-15 (b4d3206..103153c): ghDue cadence GH_POLL_MS=300000 + backoff
  below GH_MIN_REMAIN=5; R14/R15 ghStepDue per-step gate + locally anchored
  GH_WINDOW_BUDGET=60 reset-window budget enforced even with no headers.
- R16 (769e2f0, Saul P1 @ 103153c): an EXPIRED X-RateLimit-Reset was
  re-zeroing GH_WINDOW_USED on every request while staying expired forever
  once responses stopped carrying that header — the round-14/15 budget was
  fully bypassed. ghWindowRoll now consumes an expired server reset ONCE
  (rolls budget, re-anchors GH_WINDOW_AT to now, clears GH_RESET_AT); only
  a NEW future server reset may roll the window again; headerless responses
  can no longer touch it. Rate plane extracted to single-source GH_PLANE_JS
  so the selftest drives the exact shipped ghJson/ghWindowRoll. Fixture:
  expired reset consumed once (used=1, header cleared), 70 headerless
  requests accumulate (71 total), budget blocks afterwards. Pre-fix code
  FAILs exactly those 3 assertions (proven negative). Also lands live
  agent-card fields from prior STEERs: FIELDS gains "usage" and "diff";
  usageStats renders real token totals/in-out/calls (missing or negative
  pieces drop, never invented) and diffStats renders file count, +/- lines,
  dirty flag, expandable changed-file list; both degrade to unavailable.
- R17 (STEER 18:57Z keep-alive): page PREFERS multi-agent GET
  https://srv1840454.hstgr.cloud/api/hermes-sessions/prs ({count,
  prs[]{pr,agents[]}} verified live), flattens prs[].agents[] into cards;
  flat /sessions stays the fallback when /prs is non-ok/malformed/
  unreachable. Rows render harness+model tags (tags[] prefixes, fallback
  top-level fields) + Saul review block (conclusion, @head SHA, P0/P1/P2)
  sourced ONLY from agents[].review — absent review renders nothing; the
  note reports src=prs vs src=sessions honestly. --check adds needles PLUS
  a runtime node probe driving shipped SESSIONS_JS with json.dumps
  payloads: load 1 asserts preference + tags + Saul; load 2 stubs /prs as
  HTTP 503 and asserts honest /sessions degradation.

## Next safe action

Round-17 pushes the /prs consumer. Watch CI bind to the new head; a fresh
real-Codex Saul run must bind to it (codex_invoked=true, synthetic=false,
P0=P1=0). Then owner human verification of the /prs consumer on exact HEAD;
KEEP_ALIVE holds until then. Stay draft.
