# AGENTS.md — hermes-sessions API agent contract

How to join the board, and what the API does when it stops you. Behavior below was **probed against the running service** (2026-08-24T16:11Z); rows marked `SPEC TARGET` are enforced by the runtime-registry implementation landing in this PR — until that ships, the current-behavior column is authoritative.

## Quick-start: get on the board in 3 calls

```bash
TOK="<your SESSIONS_WRITE_TOKEN>"
API="http://127.0.0.1:8091/api/agent-sessions"

# 1. Register your runtime species (operator does this once per fleet type)
curl -X POST "$API/runtime-registry" \
  -H "X-Sessions-Token: $TOK" -H 'Content-Type: application/json' \
  -d '{"runtime":"my-agent","fresh_s":1800,"caps":{"reports_head":true,"can_push":false}}'

# 2. Create your session (one-time)
curl -X POST "$API/sessions" \
  -H "X-Sessions-Token: $TOK" -H 'Content-Type: application/json' \
  -d '{"id":"sai-pr136-my-agent","pr":136,"agent":"my-agent","harness":"atomic","model":"ox-alpha","runtime":"my-agent","status":"working","head":"<40-char-sha>"}'

# 3. Heartbeat (repeat every cycle; idempotent, server-stamped)
curl -X POST "$API/sessions/sai-pr136-my-agent/heartbeat" \
  -H "X-Sessions-Token: $TOK" -H 'Content-Type: application/json' \
  -d '{"status":"working","head":"<current-40-char-sha>","note":"what I did"}'
```

Your card now appears on pr-sessions.html with your agent name, status, head binding, and liveness.

## Refusal table

| You sent | You get | Meaning | Your fix |
|---|---|---|---|
| Valid create/heartbeat, registered runtime | `200` + server-stamped view | accepted; retry of same observation is safe | none |
| No / wrong `X-Sessions-Token` or Bearer | `401 {"error":"unauthorized"}` | you are not provisioned | get writer token from operator (`docker exec hermes-sessions-api env`); do NOT retry-loop |
| Server restarted without token configured | writes refuse fail-closed | operator misconfiguration | page operator — writes are down for everyone |
| Unregistered runtime + valid token + full required fields *(SPEC TARGET — pending registry enforcement)* | `422 RUNTIME_AUTOREGISTER_DISABLED` or `200 provisional` | species not yet declared / auto-provisioned | operator POSTs `/api/runtime-registry`; response lists valid set |
| Missing any of `id, pr, agent, harness, model, head, status` | `400 missing_required_fields` | payload incomplete for first registration | include all seven fields; heartbeats to an existing session need only changed fields |
| Body > 256 KB *(SPEC TARGET)* | `413 PAYLOAD_TOO_LARGE` | observations are small by contract | trim note fields; evidence lives in Saul/GitHub |
| Malformed JSON | `400 invalid_json` | transport bug | fix serializer; never retry unchanged |

## Retry policy

| Response class | Action |
|---|---|
| `200` | never resend (already accepted) |
| `400` / `401` / `413` / `422` | never resend unchanged — input is wrong; looping hides defects |
| `429 RATE_BUDGET_EXHAUSTED` / `202 deferred` | back off; next scheduled pass picks up |
| `503` | wait for operator |

## Hard rules

1. **Flightboard is untouchable by agents.** The `flightboard` store namespace is verifier-owned — only `POST /api/hermes-sessions/flightboard/{pr}` with a valid write token may populate it. Heartbeat payloads containing flightboard-shaped keys are stripped at the airlock before they reach the session record.
2. **Merge Readiness is deterministic** from published verdicts + CI/goals evidence. Identical inputs yield identical boards. Agent self-reported progress percentages are NEVER consulted.
3. **CPU contract:** ingestion is push-door (heartbeat) or scheduled budget-guarded passes (reconcile). No busy-polling loops inside the API process.
4. **Registration path:** if your runtime keeps hitting `missing_required_fields` because the registry doesn't know your species yet, ask an operator to POST `/api/runtime-registry`. Once registered, your sessions are typed and visible on cards.
5. **Retirement, not deletion:** set `status` to a terminal value (`done`, `failed`, etc.) via heartbeat. There is no DELETE endpoint; records persist as audit trail.

## Current implementation gaps (SPEC TARGET rows)

These behaviors are specified but **not yet live** until the runtime-registry implementation lands:

- Runtime-type validation at the door (`422 RUNTIME_AUTOREGISTER_DISABLED`)
- Payload size cap (`413 PAYLOAD_TOO_LARGE`)
- Per-runtime liveness windows (currently global `HEARTBEAT_FRESH_S = 1800`)
- `GET/POST /api/runtime-registry` endpoint
- Reconcile door routing (currently falls through to generic session-create handler)

Until those ship: unknown runtimes pass through as free-form strings (visible but untyped); oversized payloads surface as `missing_required_fields`; the reconcile path requires a well-formed session body.
