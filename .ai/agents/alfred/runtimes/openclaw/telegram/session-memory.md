# Alfred — Telegram session memory model

**Service:** `openclaw-dashboard/services/telegram-session/`  
**Protocol:** [telegram-session-protocol.md](../../../../../openclaw-dashboard/docs/telegram-session-protocol.md)

---

## Purpose

Alfred maintains **durable session state** across Telegram conversations so each DM thread
is a continuous agent session — not stateless one-shot replies. Memory aligns with ICM
`.ai/runs/<task-id>/` artifacts.

---

## Storage layout (VPS)

```
~/.openclaw/sessions/ctr-code-alfred1/
  <telegram_chat_id>/
    session_state.json      # current snapshot
    session_transcript.jsonl # inbound/outbound messages (redacted)
    context_summary.md      # rolling summary for model context (<4KB)
    active_task_id.txt      # single line: current task-id
```

### session_state.json schema

```json
{
  "agent_id": "ctr-code-alfred1",
  "contract_id": "20260722-openclaw-dashboard-dezocode",
  "telegram_chat_id": "<id>",
  "contract_sender_slack_id": "U0BHYH0NMCY",
  "active_task_id": "20260722-HHMM-purpose-alfred",
  "icm_stage": "implement",
  "branch": "proj/openclaw-dashboard/ctr-code-alfred1/bootstrap",
  "last_event_type": "CHANGE",
  "last_slack_mirror_at": "2026-07-22T05:00:00Z",
  "last_telegram_update_at": "2026-07-22T05:00:00Z",
  "open_blockers": [],
  "memory_revision": 3,
  "context_summary_hash": "sha256:..."
}
```

---

## Update rules

| Trigger | Memory action |
|---|---|
| New `task-id` | Reset stage to `intake`; append prior task to `archived_tasks[]` |
| Stage transition | Bump `icm_stage`; append to `session_transcript.jsonl` |
| User Telegram reply | Load `context_summary.md` + last 10 transcript lines into prompt |
| HANDOFF | Write final summary; sync redacted copy to `.ai/runs/<task-id>/telegram-session.jsonl` |
| Gateway restart | Reload `session_state.json`; send "session resumed" to contract sender |

---

## Context summary (rolling)

Alfred regenerates `context_summary.md` after every VERIFY or HANDOFF:

```markdown
# Session context — <task-id>
Contract: 20260722-openclaw-dashboard-dezocode
Stage: <stage> | Branch: <branch>
Done this session: <bullets>
Open: <blockers or none>
Next: <one action>
```

Max 4KB. Never store tokens, env vars, or private paths.

---

## Repo mirror (ICM alignment)

Commit-safe artifact per run:

```
.ai/runs/<task-id>/
  telegram-session.jsonl   # {"dir":"out","event":"INTAKE",...} redacted
  metadata.json              # includes telegram_session: true
```

Merge gate: handoff.md references Telegram updates sent to contract sender.

---

## Fleet agents

Subagents use parallel paths:

```
~/.openclaw/sessions/<agent_id>/<chat_id>/
```

Alfred provisions on create; fleet gate verifies structure exists or BLOCKED documented.
