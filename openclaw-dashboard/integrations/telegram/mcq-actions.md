# Telegram — multiple-choice action requests (BLOCKED handoff)

**Integrations:** Composio Telegram + OpenClaw Telegram channel  
**UI mirror:** `McqActionCard` in dashboard bottom panel + iOS inbox  
**Continuation:** [BLOCKED-MCQ-CONTINUATION.md](../../../.ai/agents/alfred/runtimes/openclaw/telegram/BLOCKED-MCQ-CONTINUATION.md)

## Purpose

When Alfred (or any fleet agent) is **BLOCKED**, the contract requires a Telegram MCQ to
contract sender with **2–4 complete plans** — not vague questions. Alfred persists a
**continuation checkpoint** and resumes his full train of thought after the user selects a plan.

Triggers:

- Missing secret / env var (`auth-matrix.md`)
- Verify or smoke gate FAIL requiring human decision
- Auth provider down
- Fulfillment gate ambiguity
- Scope, security, or approval holds
- Any stop where guessing would violate ICM or security policy

---

## Complete plan definition

A **complete plan** is executable end-to-end if selected:

| Required | Example |
|---|---|
| Ordered steps | 1. You provide X → 2. I run Y → 3. I continue Z |
| Outcome | "Gateway healthy + A1 docs committed" |
| Risk | low / med / high |
| No further clarification | Unless a **new** blocker appears mid-plan |

**Bad:** "Should I continue?"  
**Good:** "Plan B — Defer secrets 24h: I commit A1 doc-only artifacts, leave registry pending, HANDOFF with checkpoint preserved."

Minimum **2** plans; prefer **3–4** when tradeoffs exist.

---

## Message format (Telegram)

```
🔔 Alfred BLOCKED — choose a complete plan
Task: 20260722-…-alfred
Step: A0-3 gateway health
Context: Gateway up on loopback; TELEGRAM_BOT_TOKEN missing — cannot pair inbox.

1️⃣ Plan A — Provide token now
• You send TELEGRAM_BOT_TOKEN (secure reply)
• I write /etc/openclaw/sai.env (0600), rerun health gates
• I continue A0-4 systemd + A1 scaffold
Outcome: channels ready this session | Risk: low

2️⃣ Plan B — Doc-only continue
• I commit A1 documentation without live Telegram test
• Registry stays pending; I note BLOCKED-cleared for docs only
• Resume ingest design when token arrives
Outcome: forward progress without secrets | Risk: med

3️⃣ Plan C — Defer 24h
• I HANDOFF with checkpoint saved
• Resume same task-id when you message "continue Plan C"
Outcome: paused clean state | Risk: low
```

Implementation: OpenClaw Telegram outbound + **inline keyboard** (1–4 buttons) + numbered text fallback.

---

## Continuation (after user responds)

1. Map reply → plan (clarify once if ambiguous)
2. Telegram ack: "✅ Plan N — resuming from `<step_label>`"
3. Load `continuation_checkpoint` from session memory
4. Continue **same task-id**, same train of thought — post `[SAI][CHANGE]` prefixed `Resuming from checkpoint`

See BLOCKED-MCQ-CONTINUATION.md for full schema.

---

## Routing

| Recipient | Telegram | Fallback |
|---|---|---|
| dezocode (contract sender) | U0BHYH0NMCY mapped chat | Slack @mention |
| monaecode | U0BGNS7F0T1 mapped chat | Slack |
| Alfred | Bot DM verified (A10) | Queue `agent-report` |

**BLOCKED MCQ always goes to contract sender first.**

---

## Dashboard mirror

When MCQ sent:

1. Ingest event → tracking tab pulse
2. `McqActionCard` with same plan titles + steps (Cursor buttons)
3. Answer syncs to VPS → resolves Telegram thread + clears `pending_mcq`

---

## Slack / GitHub

Parallel (never substitute for Telegram MCQ):

- `[SAI][BLOCKED][task-id]` to #agentupdates — plan **titles** only
- Optional PR comment on bootstrap PR (no secrets)

---

## Smoke

`tests/smoke/telegram-mcq.sh` — test MCQ with ≥2 complete plans; expect ack within 60s.

Fulfillment: live BLOCKED → MCQ → user selection → resume message chain evidenced in handoff.
