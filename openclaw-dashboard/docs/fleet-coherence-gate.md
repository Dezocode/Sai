# Fleet coherence proof gate

**Protocol:** [telegram-session-protocol.md](./telegram-session-protocol.md)  
**Smoke:** `tests/smoke/fleet-coherence-gate.sh`

---

## Purpose

Prove the Alfred **fleet** — Alfred + all subagents + dashboard-created OpenClaw agents —
operates with **identical** ICM, Telegram session, and Slack mirror discipline before
organization onboarding.

Alfred is the **template**; every other agent inherits or documents explicit divergence (BLOCKED only).

---

## Coherence requirements (per agent)

| # | Requirement | Evidence |
|---|---|---|
| C1 | OpenClaw-primary or documented subagent runtime | `registry.json` or `.openclaw/agents/*.md` |
| C2 | Telegram behaviors doc exists | `BEHAVIORS.md` in agent folder or template ref |
| C3 | Session memory schema documented | `session-memory.md` or fleet template link |
| C4 | Registry row with valid gates or BLOCKED | `agent-telegram-registry.md` |
| C5 | Slack mirror configured | `hooks.json` or OpenClaw channel config |
| C6 | ICM run produces paired TG+Slack | `.ai/runs/<task-id>/telegram-session.jsonl` |
| C7 | Contract sender reporting enabled | `contract.json` → `contract_sender.telegram_reporting` |

---

## Fleet roster (contract scope)

Minimum fleet for proof gate PASS:

- `ctr-code-alfred1` (Alfred)
- `config-expert`
- `research-coordinator`

Expand automatically when registry or `.openclaw/agents/` grows.

---

## Proof run (Alfred executes once before fulfillment)

1. Create task-id `YYYYMMDD-HHMM-fleet-coherence-proof-alfred`
2. Send INTAKE Telegram to contract sender + Slack mirror
3. Each subagent sends `[SAI][INTRO]` with its Telegram DM link
4. Run `fleet-coherence-gate.sh` — must exit 0
5. HANDOFF with links to Telegram message ids (redacted in Git) + Slack permalinks

---

## Failure modes

| Failure | Remediation |
|---|---|
| Missing BEHAVIORS.md | Alfred copies template from own `runtimes/openclaw/telegram/` |
| No session memory path | Provision `~/.openclaw/sessions/<agent_id>/` on VPS |
| Telegram without Slack mirror | Fix hooks; re-run stage report |
| Stub PASS | Scripts must fail closed until evidence files exist |
