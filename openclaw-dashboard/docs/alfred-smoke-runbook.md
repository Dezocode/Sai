# Alfred — smoke test & gate orchestration runbook

**Agent:** Alfred (`ctr-code-alfred1`)  
**Contract:** `20260722-openclaw-dashboard-dezocode`

Alfred owns running and evidencing **all gates** before organization onboarding.

## Gate suite (run on VPS + before every PR)

```bash
# From repo root on bootstrap branch
openclaw-dashboard/tests/smoke/all-gates.sh
```

| Gate | Script | Pass criteria |
|---|---|---|
| ICM hierarchy | `scripts/verify-semantic-hierarchy` | exit 0 |
| Agent setup | `scripts/verify-agent-setup` | exit 0 |
| Design language | `tests/smoke/design-tokens.sh`, `tests/smoke/design-compliance.sh` | tokens v2, immersive-game, CursorSelect, VPS liveData |
| Ingest SLO | `scripts/verify-ingest-latency.sh` | p99 ≤ 15ms |
| Telegram MCQ | `tests/smoke/telegram-mcq.sh` | dezocode ack ≤ 60s |
| Fleet coherence | `tests/smoke/fleet-coherence-gate.sh` | Alfred template + fleet registry + hooks |
| Secrets compliance | `tests/smoke/secrets-compliance.sh` | PR #45 controlling structure; no values in Git |
| Gateway loopback | `scripts/verify-gateway-bind.sh` | 127.0.0.1 only (Saul P1, CI) |
| Subagent gate negative | `tests/smoke/subagent-connection-gate-negative.sh` | rejects `@`, `http-not-a-url` (CI) |
| Subagent connection enforce | `tests/smoke/subagent-connection-gate.sh` | fail-closed — fulfillment only |
| Telegram registry | `scripts/verify-agent-telegram.sh --scope registry` | all registry agents evidenced |
| Tab smoke | `tests/smoke/run-all.sh` | zero blocking errors |
| Contract review | `scripts/agent-contract-pr-review` | no pending_manual |

## Telegram MCQ smoke

1. Send test MCQ per `integrations/telegram/mcq-actions.md`
2. dezocode selects option via inline keyboard
3. Alfred posts `[SAI][VERIFY]` with evidence timestamp
4. Mirror `McqActionCard` in dashboard bottom panel

## Slack / GitHub automation

On any gate **FAIL**:

- Post `[SAI][BLOCKED][task-id]` to #agentupdates
- Optional: GitHub PR comment on bootstrap PR (summary only)
- Send Telegram MCQ to dezocode with retry/defer/block options

## Evidence

Record in `.ai/runs/<task-id>/04_verify/output/smoke-evidence.md`:

- Command outputs (redact secrets)
- Screenshot paths for design shell (optional)
- ingest p99 measurement log
- Telegram message_id for MCQ test

## Responsive TTS smoke

- Mac: trigger agent reply → NSSpeech within 500ms when responsive mode on
- iOS: AVSpeech within 500ms in inbox test thread

Document in same verify output.
