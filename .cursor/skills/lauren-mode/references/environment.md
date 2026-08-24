# Live Cloud Agent environment

Recorded 2026-08-19 from `environment-info` on run `bc-01a01c62-2904-7567-b237-4ba571eafd30`. Re-read the Cursor Cloud `environment-info` tool before treating these IDs as current.

| Field | Value |
|---|---|
| Name | dezocode/sai |
| Source | Personal (dashboard-managed, not a repo file) |
| Environment ID | [6f2ece39-800a-11f1-ba66-0e7d0216e441](https://cursor.com/dashboard/cloud-agents/environments/e/6f2ece39-800a-11f1-ba66-0e7d0216e441) |
| `environmentJsonPath` | null (DB-managed) |
| Repo | `github.com/dezocode/sai` |
| Egress | unrestricted |
| Chrome | `/usr/bin/google-chrome` on this image |

`environment.json` is owner-restricted for personal environments. This agent cannot dump the saved install/start scripts. Precedence is still: committed `.cursor/environment.json` wins over personal and team dashboard configs.

## Do not commit `.cursor/environment.json`

A repo file would replace the personal environment for every Cloud Agent on that revision. Decision 0004 already rejected stuffing plugins into `environment.json` (the schema has no `plugins` key). Skills and plugins load from git. They do not need an install script.

To change install/start, use the dashboard Save flow after `propose-environment-json`. Do not snapshot or trigger a draft build from a skills-only change.

## What "live" means for this task

- Skills and rules become live on the next Cloud Agent whose **working tree** includes this commit.
- This session cannot hot-load `/lauren-mode` into its own `/` picker.
- Recurring system builds on the personal environment may show `SKIPPED`. That is the dashboard scheduler, not a skills failure.

## gitSetup reuse can hide PR 70

Verified 2026-08-20 on fresh mobile agent `bc-01a01c89-0d79-709c-aacf-ba84185f18aa` (after PR 70 merged as `8a30202`):

- `branchName` was null
- `gitSetup` was `reuse` of snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0`
- Install exited 0 immediately (no clone of live `main`)
- The agent thought the lauren files were absent. `origin/main` already had them.

A new Cloud Agent on this personal env can boot the pre-merge snapshot tree. Type `/lauren` or `/lauren-mode` only after the checkout contains `.cursor/skills/lauren-mode/SKILL.md`. If it does not, fetch `origin/main` and check out that SHA. Starting the agent on an explicit branch from latest `main` avoids the null-branch reuse path.
