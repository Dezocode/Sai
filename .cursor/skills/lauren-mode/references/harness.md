# 08-19-26 Cloud Agent harness

Source: [cursor.com/changelog/08-19-26](https://cursor.com/changelog/08-19-26) and [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities.md). Load this file when the task is long-running, event-driven, or needs isolated subagents.

## Custom Modes

A slash skill attaches to one message. A Custom Mode keeps the skill pinned for the whole session. `/lauren-mode` is the SAI pin. `/poteto-mode` remains the upstream pstack skill (also `mode: true` in the plugin). Prefer `/lauren-mode` in Cloud Agents so the harness rules below stay in context.

## /goal

Use the `CreateGoal` tool when the user wants the agent to keep going until an objective is fully met. Examples: "fix all flaky tests", "drive this PR to green", "keep going until that Slack feedback is in".

- Call `CreateGoal` once with a concrete objective.
- Call `UpdateGoal` with `status: "complete"` only after evidence shows the objective is met.
- Pair the goal with this Custom Mode. Pair with `/loop` only for recurring check-ins, not as a substitute for a goal.

## Subagents on their own machines

The 08-19-26 release lets each subagent run on its own VM with a clean clone.

When isolation matters (fresh-environment tests, parallel fixes that would collide, verifying the parent agent's branch):

```
Task:
  environment: "cloud"
  run_in_background: true
  subagent_type: "poteto-agent"   # or explore / computerUse as the playbook says
```

From the Agents Window on Desktop, `/in-cloud` sends the next task to a cloud subagent. `/babysit` is the PR-watch path. Do not swarm colliding writes onto one working tree. SAI still allows one agent per working tree.

Resume with the returned agent id. Do not poll a background `Task` with sleep loops. Wait for the completion notification.

## Subscriptions

Cloud agents can wait on events and wake in the same conversation.

| Source | Wake on |
|---|---|
| GitHub | PR comments, reviews, lifecycle, CI on a branch |
| Slack | Thread replies, channel messages, new public channels |
| Linear | Issue create/state, comments |
| Timers | One-off delay or cron (`/loop` for recurring) |

Describe the wait in the prompt ("open a PR and keep it green until merge") or invoke `/subscribe`. Agents auto-subscribe to PRs they create and try to fix GitHub Actions CI they caused, unless the user pushed a new commit, sent a follow-up, the check already failed on the base, or 10 CI follow-ups already ran.

Subscriptions last at most 180 days. Unsubscribe when the wait is over. Bursts coalesce. Re-read the PR, thread, or issue before acting.

## Steering

Follow-up messages wait for the next tool call. They do not cut the agent off mid-action. Keep working through the current tool. Apply the follow-up on the next turn. The user can Send now or press Enter twice. Do not treat a queued follow-up as a hard interrupt.
