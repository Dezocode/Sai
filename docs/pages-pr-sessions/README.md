# PR sessions dashboard

Tracked Hermes implements Pages `pr-sessions.html` + feature-map tab. Since
the full-flight rework, `pr-sessions.html` joins two live data planes by PR
number:

- GitHub authority: unauthenticated public REST (`api.github.com`,
  CORS-enabled) for the Dezocode/Sai PR list, per-PR details, and per-HEAD
  check-run rollups (including the Saul / Product Quality check). No token
  ever reaches the page. The GitHub plane polls at most once per 5 minutes;
  a poll may issue 1 listing + up to 24 budgeted enrichment requests, each
  re-checking the rate-limit state so the batch stops at a small remaining
  floor or a 60-request per-window budget (listing plus enrichment counted,
  anchored locally when no reset header), then backs off until reset. ETag
  GETs only save re-transfer.
- Sessions: public Hostinger sessions API for live Hermes agent sessions.

Cards are the union of both planes; an open PR with no session renders an
`Agent: NONE — no worker attached` warning; a session whose `head` differs
from the authoritative PR HEAD gets a mismatch flag; heartbeat buckets
fresh / stale / missing stay distinct (missing is never counted as stale).
CI rollup keeps only the newest attempt per check name (a successful rerun
clears an earlier failure) — guarded by an adversarial `--selftest` node
harness whose fixtures include a superseded failed attempt followed by a
green rerun of the same check name (this exact bug was Saul P1; the harness
fails on the pre-fix rollup); GitHub enrichment runs through a budgeted,
sequential planner (at most 24 requests per refresh — session-linked cards
then open cards first, check fetches deduped per head SHA; each request re-checks
the rate-limit state so a batch stops at the floor or a 60-request per-window
budget (locally anchored), never exhausting the anon quota); pending-selection lives inside the
planner so a session-only PR absent from the listing still gets its per-PR
detail by number then checks once any HEAD is known, the listing HEAD always
wins over cached detail HEAD for change detection (a force-push re-binds
CI/Saul), and completion is marked by the same SHA resolution (never an
eternal re-plan) - all adversarial `--selftest` fixtures failing on their
pre-fix implementations; "last push" is an authoritative head-repo push
timestamp, with PR `updated_at` labeled separately as "updated"; a PR
discovered only through a session disappears once that session and the
listing both drop it (no ghost cards). Missing data renders as unavailable,
never fabricated.

Regenerate locally with `scripts/render-sai-feature-maps --check` (runs the
selftest then asserts the pages) or `--out DIR`; CI deploys via
`.github/workflows/feature-maps-pages.yml`.
