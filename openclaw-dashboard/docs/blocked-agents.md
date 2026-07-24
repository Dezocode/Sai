# Blocked agents — three-connection gate remediation (A10)

Agents listed here have **documented BLOCKED** status for one or more gates.
`verify-agent-telegram.sh` accepts `habbo_presence: blocked` only when this
file contains a row with **nonempty** `blocked_gate`, `reason`,
`remediation_owner`, and `mcq_ticket`.

**BLOCKED does not waive Telegram or Slack.** Valid `telegram_dm_link` and
`slack_intro_permalink` are still required per
[subagent-onboarding-protocol.md](./subagent-onboarding-protocol.md) §3.

| agent_id | blocked_gate | reason | remediation_owner | mcq_ticket | target_date |
|---|---|---|---|---|---|
| _example_ | habbo_presence | awaiting Phaser asset pipeline | alfred | MCQ-example | — |

**Rules:**

- No `connected=yes` in `agent-telegram-registry.md` while any gate is blocked
- Telegram + Slack intro **always** required (BLOCKED only exempts Habbo `connected`)
- Remove row when gate passes; update registry in same commit
- Placeholder `—` is invalid for required remediation columns

Verification: `openclaw-dashboard/scripts/verify-agent-telegram.sh --scope contract`
