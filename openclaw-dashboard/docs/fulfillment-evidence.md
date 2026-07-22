# Fulfillment evidence checklist (A12)

**Contract:** `20260722-openclaw-dashboard-dezocode`  
**Tracker:** [PR45-REVIEW-TRACKER.md](../../.ai/contracts/20260722-openclaw-dashboard-dezocode/PR45-REVIEW-TRACKER.md)

Alfred fills this file on bootstrap branch before requesting merge to `main`.

## VPS evidence paths (`.ai/runs/<task-id>/04_verify/output/`)

| Gate | File | Pass criteria |
|---|---|---|
| Gateway loopback | `gateway-exposure.txt` | `ss` shows 127.0.0.1:18789 only |
| Ingest SLO | `ingest-latency.json` | p99 ≤ 15ms over ≥1000 samples |
| Phase 5B caps | `openclaw-tools-survey.json` | `agent-verify-caps` exit 0 |
| Three-connection | `agent-telegram-verify.log` | `verify-agent-telegram.sh --scope registry` exit 0 |
| Fleet coherence | `fleet-coherence.log` | `fleet-coherence-gate.sh` exit 0 |
| Telegram session proof | `telegram-session.jsonl` in proof run | dezocode confirms INTAKE+HANDOFF on Telegram |
| Design compliance | `design-compliance.log` | `design-compliance.sh` exit 0 |
| Smoke all gates | `all-gates.log` | `all-gates.sh --enforce` exit 0 |

## Demo artifacts

- [ ] Screen recording: tracking tab live graph + p99 badge
- [ ] Screen recording: chat tab full-screen Habbo + rolodex HUD
- [ ] Screenshot: auth hub reaching GitHub + Composio (no tokens visible)

## Human gates

- [ ] `[SAI][VERIFY]` posted with links to evidence files
- [ ] Saul CTO review — no open P1
- [ ] dezocode + monaecode merge authorization

**Do not** mark complete until every row has real file paths in handoff.
