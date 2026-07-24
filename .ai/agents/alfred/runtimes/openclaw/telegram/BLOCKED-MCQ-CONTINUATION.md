# Alfred — BLOCKED MCQ + continuation protocol (binding)

**Agent:** `ctr-code-alfred1` | **Applies to:** Alfred and all fleet agents Alfred provisions  
**MCQ format:** [mcq-actions.md](../../../../../../openclaw-dashboard/integrations/telegram/mcq-actions.md)  
**Memory:** [session-memory.md](./session-memory.md) → `continuation_checkpoint`

---

## Rule (non-negotiable)

**Any blocker** — missing secret, failed gate, human approval, ambiguous requirement,
dependency unavailable, Saul/security hold — **must** trigger:

1. **Telegram MCQ** to contract sender (dezocode) with **2–4 complete plans**
2. **Continuation checkpoint** persisted **before** waiting
3. **Full resume** from checkpoint when user selects a plan (or maps free-text to one)

Never post BLOCKED to Slack only. Never ask open-ended questions without complete plans.
Never lose context across the wait — the user must not re-explain.

---

## B6 — BLOCKED: MCQ with complete plans

### When to trigger

- Smoke/verify script FAIL you cannot fix without human input
- Missing env var, credential, or approval per `auth-matrix.md`
- Fulfillment gate ambiguity
- Git conflict, scope question, or security-policy hold
- Any situation where proceeding would guess or violate ICM/security rules

### Before sending MCQ (mandatory checkpoint)

Write `continuation_checkpoint` to `session_state.json` **and** append to
`.ai/runs/<task-id>/telegram-session.jsonl`:

```json
{
  "continuation_checkpoint": {
    "task_id": "YYYYMMDD-HHMM-purpose-alfred",
    "icm_stage": "implement",
    "step_label": "A0-3 gateway health verify",
    "train_of_thought": "Installed openclaw, started gateway on 127.0.0.1:18789, doctor passed, about to install systemd unit when TELEGRAM_BOT_TOKEN missing blocked channel pairing test.",
    "completed_since_intake": ["worktree created", "verify-all-dependencies PASS", "gateway loopback up"],
    "next_step_if_unblocked": "Install systemd unit, run verify-gateway-health, proceed to A1 sai-icm-integration.md",
    "files_in_scope": ["openclaw-dashboard/host/systemd/openclaw-gateway.service"],
    "uncommitted_state": "none | describe",
    "blocker": {"type": "missing_secret", "detail": "TELEGRAM_BOT_TOKEN not in /etc/openclaw/sai.env"},
    "pending_mcq": true,
    "checkpoint_at": "ISO8601"
  }
}
```

Regenerate `context_summary.md` including checkpoint summary (still <4KB, no secrets).

### Telegram MCQ message template

```
🛑 Alfred BLOCKED — need your choice
Task-ID: <task-id>
Stage: <icm_stage> | Step: <step_label>

Context:
<2-3 sentences — what you were doing and why blocked>

I will resume exactly from this checkpoint when you choose.

━━ Complete plans (pick one) ━━

1️⃣ Plan A — <short title>
• <step 1>
• <step 2>
• <step 3>
Outcome: <what done looks like> | Risk: <low/med/high>

2️⃣ Plan B — <short title>
• …
Outcome: … | Risk: …

3️⃣ Plan C — <short title> (optional)
• …

4️⃣ Plan D — <short title> (optional — e.g. defer / escalate)
• …

Reply with 1–4, tap inline button, or describe which plan (I will map and confirm once).
```

**Complete plan** means: if the user picks it, you can execute **without further clarification**
unless a new blocker appears. Each plan must include ordered steps, outcome, and risk.

Minimum **2** plans; prefer **3–4** when tradeoffs exist (speed vs safety vs defer).

Use Telegram **inline keyboard** when OpenClaw supports it; always include numbered text fallback.

### Slack mirror (same beat)

Post `[SAI][BLOCKED][task-id]` to `#agentupdates` with:

- Blocker one line
- Plan titles only (not full secrets)
- `Telegram: MCQ sent to contract sender — awaiting selection`

### While waiting

- **Do not** start unrelated work on the same task-id
- **Do not** clear `pending_mcq` until user responds
- **May** work on a **different** task-id only if user explicitly `/new-task`
- Poll session memory on every inbound Telegram message

---

## B7 — Resume after MCQ response

When contract sender replies (button, `1`/`2`/`3`/`4`, or free text):

### 1. Map response

| Input | Action |
|---|---|
| `1`–`4` or button payload | Select matching plan |
| Free text | Infer plan; if ambiguous, send **one** clarifying MCQ with 2 plans max |
| `/status` while pending | Show checkpoint + plan list + "still waiting for your choice" |

### 2. Acknowledge in Telegram

```
✅ Plan <N> selected: <title>
Resuming Task-ID <task-id> from step: <step_label>
Next action: <first step of selected plan>
```

### 3. Update memory

- Set `pending_mcq: false`
- Append `mcq_resolution: {plan_id, selected_at, user_message_redacted}` to session_state
- Keep `continuation_checkpoint` until first VERIFY after resume (then archive to jsonl)

### 4. Continue train of thought

- Reload `continuation_checkpoint.train_of_thought` + `next_step_if_unblocked`
- Resume **same** `task-id` and **same** ICM stage unless plan explicitly changes stage
- Execute selected plan steps in order
- Post `[SAI][CHANGE]` or `[SAI][PLAN]` with prefix: `Resuming from checkpoint — Plan N`

### 5. If new blocker

- New checkpoint supersedes old; send fresh MCQ (do not stack ambiguous asks)

---

## Examples of complete plans (secrets blocker)

**Plan A — Provide token now:** User sends `TELEGRAM_BOT_TOKEN` via secure channel → Alfred writes sai.env → reruns health gates → continues A0-4 systemd.

**Plan B — Doc-only continue:** Alfred commits A1 documentation without live Telegram test → leaves registry `pending` → schedules MCQ when token available.

**Plan C — Defer 24h:** Alfred HANDOFF with checkpoint preserved → `/new-task` only on user command.

---

## Verification

Fulfillment evidence must include:

- One test BLOCKED with MCQ (≥2 complete plans) + user selection + resume message chain
- `session_state.json` shows `continuation_checkpoint` before wait and cleared `pending_mcq` after
- `handoff.md` references Telegram thread message_ids for BLOCKED + resume

```bash
openclaw-dashboard/tests/smoke/telegram-session-reporting.sh
```

---

*Binding — dezocode requirement: BLOCKED always MCQ complete plans + continuation checkpoint.*
