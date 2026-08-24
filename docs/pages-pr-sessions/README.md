# PR sessions dashboard

Tracked Hermes implements Pages `pr-sessions.html` + feature-map tab, joining two live data planes by PR number: (1) GitHub authority — unauthenticated public
REST (`api.github.com`, CORS-enabled) for the Dezocode/Sai PR list, per-PR details, and per-HEAD check-run rollups including Saul / Product Quality;
no token ever reaches the page; polls at most once per 5 minutes as 1 listing + up to 24 budgeted enrichment requests that each re-check rate-limit state,
stopping at a small remaining floor or a 60-request per-window budget (anchored locally when no reset header) then backing off until reset; an expired reset
is consumed once so headerless responses never re-zero the window; ETags only save re-transfer. Check-run fetches paginate to `total_count`, capped at
`CHECK_PAGES_MAX = 3`; a page-level 304 reuses its cached page so the aggregate rebuilds completely, the largest total seen governs completeness (a stale
cache total can only lower toward partial), past-cap or gate-stopped reads are labeled partial, and pagination requests pass the per-request gate.
(2) Sessions — the public Hostinger sessions API for live agent sessions. Regenerate via `--check`/`--out DIR`; CI deploys via `feature-maps-pages.yml`.

Cards are the union of both planes: an open PR with no session renders `Agent: NONE — no worker attached`; head mismatch gets a flag; heartbeat buckets fresh / stale / missing stay distinct; CI rollup keeps the newest attempt per name; planned enrichment (≤24 steps × ≤3 pages each, session-linked then open cards, deduped per head SHA) re-binds force-pushes and prevents ghost cards; "last push" is labeled apart from `updated_at`; missing data renders unavailable, never fabricated.

## Multi-agent /prs feed contract (STEER 20:18Z)

`pr-sessions.html` prefers the multi-agent `/prs` feed over flat `/sessions`; it is accepted only when it parses, `prs` is non-empty, every group has `pr`
plus valid `agents[]` (id/status/heartbeat_at), and `updated_at` is ≤10 minutes old — otherwise it falls back to `/sessions` without claiming the `/prs` source.
Agent rows flatten as `{pr: <parent>, ...agent}`; the Saul block is identity-gated on `agent==="saul"` rendering payload fields verbatim (absent → "unavailable",
never invented); the adversarial `--check` probe drives the shipped JS with fresh/empty/stale/malformed/bare-Saul/non-Saul/503 fixtures.

## Sessions API endpoints

Base URL: `https://srv1840454.hstgr.cloud/api/agent-sessions` (alias for `/api/hermes-sessions/*`).

### `GET /sessions`

Returns all tracked sessions. Optional filters: `?pr=136`, `?status=working`, `?agent=atomic`, `?monitor=origin-grokbot`. Each session includes server-computed `heartbeat_age_s` and `liveness` (`fresh`/`stale`/`missing`). Unrecognized status strings carry `"status_recognized": false`.

### `GET /prs`

Multi-agent PR feed: one card per open PR that has at least one session. Each card carries an `agents[]` roster (id, agent, harness, model, status, phase, head, head_full, heartbeat_at, heartbeat_age_s, liveness, updated_at) plus aggregate `liveness` counts and `any_active`.

### `POST /api/runtime-registry` *(verifier token required)*

Registers a new runtime species or updates its liveness window/capabilities. Once registered, sessions referencing this runtime are accepted as full members. Body: `{"runtime":"my-agent","fresh_s":1800,"caps":{"reports_head":true}}`.

### `POST /sessions/{id}/heartbeat`

Idempotent heartbeat: updates status/head/note on an existing session with a server-stamped `heartbeat_at`. Flightboard-shaped keys in the payload are stripped at the airlock — agents can never self-award merge-readiness telemetry. Requires write token (`X-Sessions-Token` header).

### `POST /reconcile` *(verifier token required)*

Pull-adapter pass: synthesizes/maintains sessions from external evidence sources (currently GitHub check-runs). Rate-budget guarded. Returns `{"created":[],"updated":[],"checked_prs":[...]}`.

## Session fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable session identifier (`sai-pr{N}-{agent}`) |
| `runtime` | string | Registered runtime type (e.g. `hermes`, `atomic`, `cursor`, `grok`, `codex`, `human`) |
| `origin` | string | How this session was created: `push:<source>` or `pull:github_checks` |
| `registration` | string | Present only on provisional sessions: `"provisional"` until promoted by operator |
| `agent` | string | Agent display name |
| `harness` | string | Harness/framework the agent runs under |
| `model` | string | Model ID powering the agent |
| `head` | string | Short SHA this session is working against |
| `head_full` | string | Full 40-char SHA |
| `status` | string | Lifecycle state (`spawned`, `tracked`, `running`, `done`, `failed`, …) |
| `liveness` | string | Server-computed: `fresh` (< window), `stale`, or `missing` |
| `heartbeat_age_s` | int | Seconds since last heartbeat |

## Two-tier acceptance

**Tier 1 — registered runtime:** the runtime species exists in the store registry. Sessions are accepted as full members with normal liveness windows and capabilities.

**Tier 2 — provisional fallback:** when `SAUL_REGISTRY_AUTOREGISTER != 0` (default on), a first heartbeat from an unknown runtime auto-provisions it with conservative defaults. Every view carries `registration: "provisional"` until an operator promotes the species via `POST /api/runtime-registry`. Provisional sessions appear on cards but are visibly flagged — being seen never means being trusted.

When `SAUL_REGISTRY_AUTOREGISTER = 0`, unknown runtimes receive `422 RUNTIME_AUTOREGISTER_DISABLED` instead of silent acceptance.
