# PR sessions dashboard

Tracked Hermes implements Pages `pr-sessions.html` + feature-map tab, joining two live data planes by PR number: (1) GitHub authority — unauthenticated public
REST (`api.github.com`, CORS-enabled) for the Dezocode/Sai PR list, per-PR details, and per-HEAD check-run rollups including Saul / Product Quality;
no token ever reaches the page; polls at most once per 5 minutes as 1 listing + up to 24 budgeted enrichment requests that each re-check rate-limit state,
stopping at a small remaining floor or a 60-request per-window budget (anchored locally when no reset header) then backing off until reset; an expired reset
is consumed once so headerless responses never re-zero the window; ETags only save re-transfer. Check-run fetches paginate to `total_count`, capped at
`CHECK_PAGES_MAX = 3`; a page-level 304 reuses its cached page so the aggregate rebuilds completely, the largest total seen governs completeness (a stale
cache total can only lower toward partial), past-cap or gate-stopped reads are labeled partial, and pagination requests pass the per-request gate.
(2) Sessions — the public Hostinger sessions API for live Hermes agent sessions. Regenerate via `--check`/`--out DIR`; CI deploys via `feature-maps-pages.yml`.

Cards are the union of both planes: an open PR with no session renders `Agent: NONE — no worker attached`; head mismatch gets a flag; heartbeat buckets fresh / stale / missing stay distinct; CI rollup keeps the newest attempt per name; planned enrichment (≤24 steps × ≤3 pages each, session-linked then open cards, deduped per head SHA) re-binds force-pushes and prevents ghost cards; "last push" is labeled apart from `updated_at`; missing data renders unavailable, never fabricated.

## Multi-agent /prs feed contract (STEER 20:18Z)

`pr-sessions.html` prefers the multi-agent `/prs` feed over flat `/sessions`; it is accepted only when it parses, `prs` is non-empty, every group has `pr`
plus valid `agents[]` (id/status/heartbeat_at), and `updated_at` is ≤10 minutes old — otherwise it falls back to `/sessions` without claiming the `/prs` source.
Agent rows flatten as `{pr: <parent>, ...agent}`; the Saul block is identity-gated on `agent==="saul"` rendering payload fields verbatim (absent → "unavailable",
never invented); the adversarial `--check` probe drives the shipped JS with fresh/empty/stale/malformed/bare-Saul/non-Saul/503 fixtures.
