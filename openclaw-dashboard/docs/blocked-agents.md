# Blocked agents — three-connection gate remediation (A10)

Agents listed here have **documented BLOCKED** status for one or more gates.
`verify-agent-telegram.sh` accepts `habbo_presence: blocked` only when this
file contains a row with remediation owner and MCQ ticket.

| agent_id | blocked_gate | reason | remediation_owner | mcq_ticket | target_date |
|---|---|---|---|---|---|
| _example_ | habbo_presence | awaiting Phaser asset pipeline | alfred | — | — |

**Rules:**

- No `connected=yes` in `agent-telegram-registry.md` while any gate is blocked
- Telegram + Slack intro still required unless entire agent onboarding is deferred
- Remove row when gate passes; update registry in same commit

Verification: `openclaw-dashboard/scripts/verify-agent-telegram.sh --scope contract`
