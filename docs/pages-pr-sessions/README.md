# PR sessions dashboard

Tracked Hermes implements Pages `pr-sessions.html` + feature-map tab. Since
the full-flight rework, `pr-sessions.html` joins two live data planes by PR
number:

- GitHub authority: unauthenticated public REST (`api.github.com`,
  CORS-enabled) for the Dezocode/Sai PR list, per-PR details, and per-HEAD
  check-run rollups (including the Saul / Product Quality check). ETag
  conditional GETs keep anonymous rate limits manageable; no token ever
  reaches the page.
- Sessions: public Hostinger sessions API for live Hermes agent sessions.

Cards are the union of both planes; an open PR with no session renders an
`Agent: NONE — no worker attached` warning; a session whose `head` differs
from the authoritative PR HEAD gets a mismatch flag; heartbeat buckets
fresh / stale / missing stay distinct (missing is never counted as stale).
Missing data renders as unavailable, never fabricated.

Regenerate locally with `scripts/render-sai-feature-maps --check` (or
`--out DIR`); CI deploys via `.github/workflows/feature-maps-pages.yml`.
