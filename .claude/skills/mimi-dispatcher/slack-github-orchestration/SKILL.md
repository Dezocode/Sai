---
name: slack-github-orchestration
description: >-
  Compose and deliver SAI protocol reports across Slack (#agentupdates) and
  GitHub (PRs, reviews, CI) with evidence discipline. Use when posting any
  [SAI][EVENT] report, opening/annotating PRs, or reconciling Slack and
  GitHub state.
---

# Slack + GitHub orchestration

## Slack

- Format: `.ai/_config/reporting.yaml` template, `[SAI][EVENT][task-id]`
  first line, all fields present.
- Delivery path, in order of preference: (1) live Slack MCP connector if
  authenticated this session, (2) `SAI_AGENT_ID=mimi scripts/agent-report
  emit <TYPE> ...` which queues durably under `.git/agent-events/queue/`
  and flushes FIFO when `SAI_SLACK_BOT_TOKEN` is available.
- **Never claim delivery without the API response / message link.**
  "Queued" and "delivered" are different words; use the right one.
- Mentions: monaecode `U0BGNS7F0T1`, dezocode `U0BHYH0NMCY`; channels:
  `#agentupdates` C0BH15HDN2Z, `#help-newagents` C0BH8LCJLDS.
- **Full-report attachment rule (standing directive, monaecode
  2026-07-17):** every report post links the full report markdown as a
  committed GitHub artifact (run-folder URL on the pushed branch), and
  tags — intelligently, as dispatcher — exactly the humans/agents the
  report concerns (principal always; Sai for VERIFY requests; Saul for
  CTO/PR reviews; contract admin for contract events).
- Never post: secrets, tokens, webhook URLs, sensitive diffs, private
  paths (reporting.yaml `never_post`).

## GitHub

- PRs from fork branches target `Dezocode/Sai:main` unless the brief says
  otherwise. Use `gh pr create --repo Dezocode/Sai`.
- After every push: `git ls-remote` (or `scripts/agent-report
  push-confirm`) to verify the remote SHA before reporting PUSH.
- CTO review requests go to Saul (`dezo-sec-codex1`) as
  `[SAI][CTO-REVIEW][Dezocode/Sai#<n>]`; Sai verification requests as
  `[SAI][VERIFY]`.
- CI: check `gh run list --repo <repo> --branch <branch>`; report
  `[SAI][VERIFY]` or `[SAI][BLOCKED]` on results — never infer green.

## Cross-checks

Before HANDOFF: queue is flushed or its pending state reported; PR links
and merged SHAs in the report match `gh` output; Drive sync status stated
honestly (`pending` if not run).
