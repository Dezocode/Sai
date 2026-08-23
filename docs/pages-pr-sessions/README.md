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
CI rollup keeps only the newest attempt per check name (a successful rerun
clears an earlier failure) — guarded by an adversarial `--selftest` node
harness whose fixtures include a superseded failed attempt followed by a
green rerun of the same check name (this exact bug was Saul P1; the harness
fails on the pre-fix rollup); "last push" is an authoritative head-repo push
timestamp, with PR `updated_at` labeled separately as "updated"; a PR
discovered only through a session disappears once that session and the
listing both drop it (no ghost cards). Missing data renders as unavailable,
never fabricated.

Regenerate locally with `scripts/render-sai-feature-maps --check` (runs the
selftest then asserts the pages) or `--out DIR`; CI deploys via
`.github/workflows/feature-maps-pages.yml`.
