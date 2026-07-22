# Amendment: Saul CTO review — PR #45 (ec6635c)

| Field | Value |
|---|---|
| **Date** | 2026-07-22 |
| **Reviewer** | Saul (CTO, `dezo-sec-codex1`) via dezocode identity |
| **PR** | https://github.com/Dezocode/Sai/pull/45 |
| **Head at review** | `ec6635c81bc7dad883cd47b94309beda46e0a736` |
| **Applied by** | Cora (ctr-admin) |

## P1 findings (blocking for fulfillment / unsafe defaults)

### P1-A — Gateway listens on all interfaces

**Finding:** OpenClaw gateway skeleton used `"host": "0.0.0.0"` with Slack and Telegram enabled — unsafe default for an administrative/auth hub.

**Resolution (scaffold):**

- `gateway-options.json` → `"host": "127.0.0.1"` (loopback default)
- New policy doc: `.ai/agents/alfred/runtimes/openclaw/gateway/config/gateway-exposure-policy.md`
- Alfred must configure Tailscale or authenticated TLS reverse proxy **before** any public listener
- Dashboard ingest WebSocket may bind loopback; Tauri/desktop connects via SSH tunnel or Tailscale

**Fulfillment evidence required:** Alfred documents chosen exposure path in `.ai/runs/<task-id>/04_verify/output/gateway-exposure.txt` (no secrets).

### P1-B — Three-connection gate passes without per-agent evidence

**Finding:** `subagent-connection-gate.sh` only checked that registry markdown contained a column header — could exit 0 without validating each agent/subagent.

**Resolution (scaffold):**

- New `openclaw-dashboard/scripts/verify-agent-telegram.sh` — fail-closed validator
- `subagent-connection-gate.sh` delegates to it (no standalone success path)
- Validates each row in `docs/agent-telegram-registry.md`:
  - `telegram_dm_link` — must be URL or `@handle`, not `pending`/`—`
  - `slack_intro_permalink` — must be Slack archive URL when `connected=yes`
  - `habbo_presence` — must be `connected` or `blocked` with row in `docs/blocked-agents.md`
- `connected=yes` forbidden unless all three gates evidenced

**Fulfillment evidence required:** Real Telegram links + Slack intro permalinks + Habbo presence before org onboarding smoke PASS.

### P1-C — Production smoke still stubbed

**Finding:** `verify-ingest-latency.sh`, `telegram-mcq.sh`, dashboard tab smoke exit non-zero or stub — fulfillment conditions unmet.

**Resolution:** Documented as **L4 open** in [PR45-REVIEW-TRACKER.md](./PR45-REVIEW-TRACKER.md). Alfred implements on bootstrap branch; stubs remain until VPS services exist (exit 2 = not implemented, not PASS).

## Non-blocking CEO audit items (addressed)

| Item | Status |
|---|---|
| Missing handoff for task `20260722-0451-*` | Fixed `ec6635c` |
| INITIALIZE.md missing OpenClaw Phase 5B | Fixed `ec6635c` |
| first-message load-order duplicate numbers | Fixed in this amendment batch |

## Saul re-review criteria

Before CTO sign-off on fulfillment:

1. Gateway exposure policy evidenced on VPS
2. `verify-agent-telegram.sh` PASS with real agent rows (or documented BLOCKED)
3. `verify-ingest-latency.sh` exit 0 with p99≤15ms samples
4. `tests/smoke/all-gates.sh` exit 0 **without** `|| true` bypasses on enforce gates
