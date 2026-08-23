# PR sessions dashboard

Tracked Hermes implements Pages `pr-sessions.html` + feature-map tab. Since
the full-flight rework, `pr-sessions.html` joins two live data planes by PR
number:

- GitHub authority: unauthenticated public REST (`api.github.com`,
  CORS-enabled) for the Dezocode/Sai PR list, per-PR details, and per-HEAD
  check-run rollups (including the Saul / Product Quality check). No token
  ever reaches the page. The plane polls at most once per 5 minutes with 1
  listing + up to 24 budgeted enrichment requests, each re-checking rate-limit
  state so a batch stops at a small remaining floor or a 60-request per-window
  budget (anchored locally when no reset header) then backs off until reset;
  an expired reset is consumed once so headerless responses never re-zero the
  window; ETags only save re-transfer.
- Sessions: public Hostinger sessions API for live Hermes agent sessions.

Cards are the union of both planes; an open PR with no session renders an
`Agent: NONE — no worker attached` warning; a session whose `head` differs
from the authoritative PR HEAD gets a mismatch flag; heartbeat buckets
fresh / stale / missing stay distinct (missing is never counted as stale).
CI rollup keeps only the newest attempt per check name (a successful rerun
clears an earlier failure); check-run fetches paginate to `total_count`, capped
at `CHECK_PAGES_MAX = 3` budgeted requests, past which the rollup is labeled
partial instead of silently dropping runs beyond the first page. Enrichment is
planned (≤24 sequential requests, session-linked then open cards, deduped per
head SHA) so force-pushes re-bind CI/Saul and no PR becomes a ghost card;
"last push" is an authoritative head-repo timestamp, labeled apart from PR
`updated_at`. Missing data renders as unavailable, never fabricated.

Regenerate with `scripts/render-sai-feature-maps --check` or `--out DIR`; CI deploys via `.github/workflows/feature-maps-pages.yml`.

## Multi-agent /prs feed contract (STEER 20:18Z)

`pr-sessions.html` prefers the multi-agent `/prs` feed over flat `/sessions`;
it is accepted only when it parses, `prs` is non-empty, every group has `pr`
plus valid `agents[]` (id/status/heartbeat_at), and `updated_at` is ≤10 minutes
old — otherwise it falls back to `/sessions` without claiming the `/prs` source. Agent rows flatten as `{pr: <parent>, ...agent}`. The Saul
block is identity-gated on `agent==="saul"` and renders payload fields verbatim
(absent → "unavailable", never invented). The adversarial `--check` probe
drives the shipped JS with fresh/empty/stale/malformed/bare-Saul/non-Saul/503
fixtures proving preference, fallback, gating, and honest degradation.
